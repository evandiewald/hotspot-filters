import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder, StandardScaler, LabelBinarizer
from sklearn.mixture import GaussianMixture, BayesianGaussianMixture
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt


dataset = pd.read_csv("static/cache_2022-04-19.csv.gz", index_col="address_gateway")
dataset["transferred_data"] = dataset["packets_transferred"].map(lambda x: 1 if x > 0 else 0)

lb = LabelBinarizer()
makers_encoded = lb.fit_transform(dataset["name_maker"])

X = np.array(dataset.drop(["Unnamed: 0",
                           "n_denylisted_tx",
                           "rx_on_denylist",
                           "owner",
                           "location",
                           "first_block",
                           "last_block",
                           "nonce",
                           "location_hex",
                           "name_gateway",
                           "name_maker",
                           "address_maker",
                           "dcs_transferred",
                           "packets_transferred",
                           "denied_at_some_point"], axis=1))

scaler = StandardScaler()
X = scaler.fit_transform(X)

# X = np.hstack([X, makers_encoded])

gmm = BayesianGaussianMixture(n_components=6).fit(X)
gmm_labels = gmm.predict(X)

dataset["gmm_labels"] = gmm_labels

counts_by_maker = dataset.pivot_table(columns="name_maker", index="gmm_labels", aggfunc="size", fill_value=0)
counts_by_denylist = dataset.pivot_table(columns="denied_at_some_point", index="gmm_labels", aggfunc="size", fill_value=0)


