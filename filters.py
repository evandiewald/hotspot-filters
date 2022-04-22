import pandas as pd
from typing import List, Union, Optional, Tuple
from pydantic import BaseModel
import numpy as np


class Filters(BaseModel):
    makers: Optional[List[str]]
    countries: Optional[List[str]]

    data_transfer_opts: Optional[str]
    data_transfer_range: Optional[Tuple[float, float]]

    n_witnessed_range: Optional[Tuple[float, float]]
    total_witnessed_range: Optional[Tuple[float, float]]

    med_distance_range: Optional[Tuple[float, float]]
    max_distance_range: Optional[Tuple[float, float]]

    first_block_max: Optional[int]
    first_block_min: Optional[int]

    perfect_reward_scale_only: bool
    avg_tx_reward_scale_range: Optional[Tuple[float, float]]
    std_tx_reward_scale_range: Optional[Tuple[float, float]]

    witnesses_denylisted_tx: bool = False

    same_maker_only: bool = False

    avg_tx_age_blocks_range: Optional[Tuple[float, float]]
    std_tx_age_blocks_range: Optional[Tuple[float, float]]

    reasserted_hotspots_only: bool = False

    gain_range: Optional[Tuple[float, float]]
    elevation_range: Optional[Tuple[float, float]]

    on_current_denylist: bool = False
    on_any_denylist: bool = False
    previously_denied: bool = False
    never_denied: bool = False


def filter_dataset(dataset: pd.DataFrame, filters: Filters) -> pd.DataFrame:
    filtered = dataset[
        (dataset["name_maker"].isin(filters.makers) if "All" not in filters.makers else True) &
        (dataset["long_country"].isin(filters.countries) if "All" not in filters.countries else True) &
        (dataset["packets_transferred"] > 0 if filters.data_transfer_opts == "Data Transferring Hotspots ONLY" else True) &
        (dataset["packets_transferred"] == 0 if filters.data_transfer_opts == "NO Data Transferring Hotspots ONLY" else True) &
        (dataset["packets_transferred"].between(np.percentile(dataset["packets_transferred"], filters.data_transfer_range[0]),
                                                np.percentile(dataset["packets_transferred"], filters.data_transfer_range[1])
                                                if filters.data_transfer_opts == "Custom Range" else True)) &
        (dataset["n_witnessed"].between(np.percentile(dataset["n_witnessed"], filters.n_witnessed_range[0]),
                                        np.percentile(dataset["n_witnessed"], filters.n_witnessed_range[1])) if filters.n_witnessed_range else True) &
        (dataset["total_witnessed"].between(np.percentile(dataset["total_witnessed"], filters.total_witnessed_range[0]),
                                            np.percentile(dataset["total_witnessed"], filters.total_witnessed_range[1])) if filters.total_witnessed_range else True) &
        (dataset["med_distance"].between(np.percentile(dataset["med_distance"], filters.med_distance_range[0]),
                                         np.percentile(dataset["med_distance"], filters.med_distance_range[1])) if filters.med_distance_range else True) &
        (dataset["max_distance"].between(np.percentile(dataset["max_distance"], filters.max_distance_range[0]),
                                         np.percentile(dataset["max_distance"], filters.max_distance_range[1])) if filters.max_distance_range else True) &
        (dataset["avg_tx_reward_scale"] > 0.999 if filters.perfect_reward_scale_only is True else True) &
        (dataset["avg_tx_reward_scale"].between(filters.avg_tx_reward_scale_range[0], filters.avg_tx_reward_scale_range[1])
         if filters.perfect_reward_scale_only is False else True) &
        (dataset["std_tx_reward_scale"].between(filters.std_tx_reward_scale_range[0], filters.std_tx_reward_scale_range[1])
         if filters.perfect_reward_scale_only is False else True) &
        (dataset["n_denylisted_tx"] > 0 if filters.witnesses_denylisted_tx else True) &
        (dataset["same_maker_ratio"] > 0.999 if filters.same_maker_only else True) &
        (dataset["avg_tx_age_blocks"].between(filters.avg_tx_age_blocks_range[0], filters.avg_tx_age_blocks_range[1]) if filters.avg_tx_age_blocks_range else True) &
        (dataset["std_tx_first_block"].between(filters.std_tx_age_blocks_range[0], filters.std_tx_age_blocks_range[1]) if filters.std_tx_age_blocks_range else True) &
        (dataset["nonce"] > 1 if filters.reasserted_hotspots_only else True) &
        (dataset["gain"].between(filters.gain_range[0], filters.gain_range[1]) if filters.gain_range else True) &
        (dataset["elevation"].between(np.percentile(dataset["elevation"], filters.elevation_range[0]),
                                      np.percentile(dataset["elevation"], filters.elevation_range[1])) if filters.elevation_range else True) &
        (dataset["rx_on_denylist"] == 1 if filters.on_current_denylist else True) &
        (dataset["rx_on_denylist"] == 0 if filters.previously_denied or filters.never_denied else True) &
        (dataset["denied_at_some_point"] if filters.on_any_denylist or filters.previously_denied else True) &
        (dataset["first_block"] < filters.first_block_max if filters.first_block_max else True) &
        (dataset["first_block"] > filters.first_block_min if filters.first_block_min else True)
        ]
    return filtered
