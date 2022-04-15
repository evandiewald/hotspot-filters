import streamlit as st
import pandas as pd
from datetime import datetime
import os
from queries import *
from sqlalchemy.engine import Engine
from pydantic import BaseModel
from typing import List
import requests
import numpy as np


def load_unique_denied_hotspots():
    r = requests.get("https://api.github.com/repos/helium/denylist/releases").json()
    tags = [t["tag_name"] for t in r]

    denylist = pd.DataFrame(columns=["address"])
    for tag in tags:
        data = requests.get(f"https://raw.githubusercontent.com/helium/denylist/{tag}/denylist.csv")

        release_list = pd.DataFrame(data.text.split(",\n"), columns=["address"])
        release_list["address"].replace('', np.nan, inplace=True)
        release_list = release_list.dropna()
        denylist = pd.concat([denylist, release_list])
    return set(denylist["address"])


@st.experimental_memo(ttl=86400) # refresh daily
def load_dataset(_engine: Engine) -> pd.DataFrame:
    today_str = datetime.today().strftime("%Y-%m-%d")
    result_path = f"static/cache_{today_str}.csv.gz"

    # see if cache already exists locally
    if os.path.exists(result_path):
        print("Loading dataset locally...")
        dataset = pd.read_csv(result_path, index_col=0)

    # if not, pull from postgres
    else:
        print("Loading dataset from database...")
        # detailed_receipts query
        result = pd.read_sql(detailed_receipt_sql, con=_engine).fillna(0)

        # gateway inventory, makers, anytime denylist, and data transfer for additional details
        gateway_inventory = pd.read_sql("gateway_inventory", con=_engine)
        makers = pd.read_csv("static/makers.csv")
        denied_set = load_unique_denied_hotspots()
        data_transfer = pd.read_sql(data_transfer_sql, con=_engine)

        # inner join drops inactive gateways. drop extraneous columns
        dataset = result.merge(gateway_inventory, on="address").merge(makers, left_on="payer", right_on="address", suffixes=("_gateway", "_maker")). \
            drop(["id", "last_poc_onion_key_hash", "last_poc_challenge", "mode", "payer", "first_timestamp"], axis=1)

        print(dataset.columns)

        # left join with data transfer, fill non-transferring hotspots with zeros, then drop nan's (usually only 1 witness event)
        dataset = dataset.merge(data_transfer, "left", left_on="address_gateway", right_on="client")
        dataset = dataset.drop("client", axis=1).fillna(value={"dcs_transferred": 0, "packets_transferred": 0}).dropna()

        # clean this column. with few data points these slopes are +/- infinity
        dataset.loc[dataset["slope_rssi_distance"] > 10, "slope_rssi_distance"] = 10
        dataset.loc[dataset["slope_rssi_distance"] < -10, "slope_rssi_distance"] = -10

        # add denied set
        dataset["denied_at_some_point"] = dataset["address_gateway"].apply(lambda x: x in denied_set)

        # save today's cache locally
        if os.path.isdir("static") is False:
            os.mkdir("static")
        dataset.to_csv(result_path, compression="gzip")

    # return our large table of active hotspots, their details and metrics
    return dataset


class FormConfig(BaseModel):
    makers: List[str]


@st.experimental_memo
def get_form_config(dataset: pd.DataFrame) -> FormConfig:

    config = FormConfig(
        makers=list(set(dataset["name_maker"]))
    )
    return config
