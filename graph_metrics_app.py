import matplotlib.pyplot as plt
import streamlit as st
import os
import pandas as pd
from dotenv import load_dotenv
import plotly.express as px
from sqlalchemy.engine import create_engine, Engine
import networkx as nx
import h3
import numpy as np


GRAPH_METRICS_PATH = "static/graph_metrics_sample.csv"

load_dotenv()
token = open(".mapbox_token").read() if ".mapbox_token" in os.listdir() else os.getenv("MAPBOX_TOKEN")
px.set_mapbox_access_token(token)


@st.experimental_memo
def load_graph_metrics_distribution(_path):
    df = pd.read_csv(_path)
    return df


@st.experimental_memo
def load_makers(_path):
    df = pd.read_csv(_path, index_col="address")
    return df


@st.experimental_memo
def load_gateway_inventory(_engine):
    gateway_inventory = pd.read_sql("select address, name, reward_scale, location, owner, payer, first_block from gateway_inventory;", con=_engine, index_col="address")
    gateway_inventory["coordinates"] = gateway_inventory["location"].apply(h3.h3_to_geo)
    gateway_inventory["lat"] = gateway_inventory["coordinates"].apply(lambda x: x[0])
    gateway_inventory["lon"] = gateway_inventory["coordinates"].apply(lambda x: x[1])
    return gateway_inventory


engine = create_engine(os.getenv("POSTGRES_CONNECTION_STRING"))
graph_metrics = load_graph_metrics_distribution(GRAPH_METRICS_PATH)
gateway_inventory = load_gateway_inventory(engine)
makers = load_makers("static/makers.csv")

st.title("Hotspot Graph Theory")

st.markdown("""This tool can be used to characterize the connectivity of a hotspot using graph theory. When you plug in a hotspot address, we generate
 its witness graph based on a 2-hop traversal. In other words, the witnesses of its witnesses. We use this graph to generate a range of relevant statistics, 
 such as:
 * **Maximal Clique Size**: The [Maximal Clique](https://en.wikipedia.org/wiki/Clique_(graph_theory)) is the largest subset of vertices in the subgraph that are all fully connected. 
    In other words, these are hotspots that all witness each other. Large cliques (5-6+) are very uncommon on the Helium Network.
 * **Clustering Coefficient**: The [Clustering Coefficient](https://en.wikipedia.org/wiki/Clustering_coefficient) quantifies how "clique-y" the root node and its 
    neighbors are. Clustering coefficients over 0.5 are very uncommon on the Helium Network.
 * **Same Maker/Owner Ratio**: The ratio of hotspots in the graph that are of the same maker/owner as the root node.""")

address = st.text_input("Hotspot Address")


def calculate_graph_metrics(address: str, engine: Engine):
    edges_sql = f"""with a as
    
        (select distinct on (transmitter_address, witness_address) transmitter_address, witness_address
         from challenge_receipts_parsed
         where witness_address = '{address}'),
    
        b as
         (select distinct on (transmitter_address, witness_address) transmitter_address, witness_address from 
         challenge_receipts_parsed where witness_address in (select transmitter_address from a)
        )
    
        select transmitter_address, witness_address from a
        union all 
        select transmitter_address, witness_address from b;"""

    edges = engine.execute(edges_sql).all()

    G = nx.Graph(edges)

    # cliques
    cliques = nx.cliques_containing_node(G, nodes=[address])[address]
    clique_sizes = [len(c) for c in cliques]
    largest_clique = [c for c in cliques if len(c) == max(clique_sizes)][0]
    # largest_clique_size = max(clique_sizes)

    # clustering coefficient
    clustering_coeff = nx.clustering(G, nodes=[address])[address]

    # degree
    in_degree = G.degree[address]

    return G, largest_clique, clustering_coeff, in_degree


def delta_relative_to_pop(graph_metrics, key, value):
    return f"{np.round(len(graph_metrics[graph_metrics[key] <= value]) / len(graph_metrics) * 100, 0)}th Percentile"

def blocks_to_est_days(blocks: int):
    return f"Approx. {np.round(blocks / 1440, 1)} day(s)"


if st.button("Submit"):
    try:
        G, clique, clustering_coeff, in_degree = calculate_graph_metrics(address, engine)

        nodes = pd.DataFrame({"address": n, "order": nx.dijkstra_path_length(G, address, n), "in_clique": True if n in clique else False} for n in G.nodes())
        nodes = nodes.merge(gateway_inventory, left_on="address", right_on=gateway_inventory.index)
        nodes = nodes.merge(makers, left_on="payer", right_on=makers.index, suffixes=("_gateway", "_maker"))
        nodes = nodes.set_index("address")
        nodes["address"] = nodes.index # this allows you to copy / paste the dataframe
        nodes["marker_size"] = 100

        same_maker_first_hop = len(nodes[(nodes["order"] == 1) & (nodes["payer"] == nodes["payer"][address])]) / len(nodes[nodes["order"] == 1])
        same_maker_overall = (len(nodes[nodes["payer"] == nodes["payer"][address]]) - 1) / (len(nodes) - 1)
        same_maker_clique = (len(nodes[(nodes["in_clique"] > 0) & (nodes["payer"] == nodes["payer"][address])]) - 1) / (len(nodes[nodes["in_clique"] > 0]) - 1)

        same_owner_first_hop = len(nodes[(nodes["order"] == 1) & (nodes["owner"] == nodes["owner"][address])]) / len(nodes[nodes["order"] == 1])
        same_owner_overall = (len(nodes[nodes["owner"] == nodes["owner"][address]]) - 1) / (len(nodes) - 1)
        same_owner_clique = (len(nodes[(nodes["in_clique"] > 0) & (nodes["owner"] == nodes["owner"][address])]) - 1) / (len(nodes[nodes["in_clique"] > 0]) - 1)

        range_first_blocks_first_hop = int(np.std(nodes[nodes["order"] == 1]["first_block"]))#max(nodes[nodes["order"] == 1]["first_block"]) - min(nodes[nodes["order"] == 1]["first_block"])
        range_first_blocks_overall = int(np.std(nodes[nodes["order"] > 0]["first_block"]))#max(nodes[nodes["order"] > 0]["first_block"]) - min(nodes[nodes["order"] > 0]["first_block"])
        range_first_blocks_clique = int(np.std(nodes[nodes["in_clique"] > 0]["first_block"]))#max(nodes[nodes["in_clique"] > 0]["first_block"]) - min(nodes[nodes["in_clique"] > 0]["first_block"])

        st.subheader("Hotspot Locations")
        st.markdown("The *order* of a node refers to its shortest-path distance from the root node. The root node itself will have an order of 0, "
                    "its immediate witnesses are 1st order, and *their* witnesses are 2nd order.")
        st.plotly_chart(px.scatter_mapbox(nodes, lat="lat", lon="lon", color="order", size="marker_size", hover_data=["name_gateway", "name_maker", "reward_scale", "owner", "in_clique"], hover_name=nodes.index).update_layout(mapbox_style="dark",
                          showlegend=False,
                          mapbox_zoom=10,
                          margin={'l':0, 'r':0, 'b':0, 't':0}))

        st.subheader("Graph Metrics")
        cols1 = st.columns(3)
        cols1[0].metric("In Degree", in_degree)
        cols1[1].metric("Largest Clique Size", len(clique), delta=delta_relative_to_pop(graph_metrics, "largest_clique", len(clique)))
        cols1[2].metric("Clustering Coefficient", np.round(clustering_coeff, 2), delta=delta_relative_to_pop(graph_metrics, "clustering_coefficient", clustering_coeff))

        pos = {p: (nodes["lon"][p], nodes["lat"][p]) for p in nodes.index}
        fig, ax = plt.subplots()
        ax.set_title("Witness Graph with Largest Clique (Yellow Nodes)")
        nx.draw(G, pos, node_color=nodes["in_clique"], ax=ax)
        st.pyplot(fig)

        st.subheader("Same-Maker Witness Ratios")
        cols2 = st.columns(3)
        cols2[0].metric("1 Degree", np.round(same_maker_first_hop, 2))
        cols2[1].metric("2 Degrees", np.round(same_maker_overall, 2))
        cols2[2].metric("In Largest Clique", np.round(same_maker_clique, 2))

        st.subheader("Same-Owner Witness Ratios")
        cols3 = st.columns(3)
        cols3[0].metric("1 Degree", np.round(same_owner_first_hop, 2))
        cols3[1].metric("2 Degrees", np.round(same_owner_overall, 2))
        cols3[2].metric("In Largest Clique", np.round(same_owner_clique, 2))

        st.subheader("Standard Deviation in Assertion Time (blocks)")
        st.caption("This is an indication of how quickly a cluster was deployed. On a network this large, it is anomalous if all a hotspot's witnesses were asserted within a couple days.")
        cols4 = st.columns(3)
        cols4[0].metric("1 Degree", range_first_blocks_first_hop, delta=blocks_to_est_days(range_first_blocks_first_hop))
        cols4[1].metric("2 Degrees", range_first_blocks_overall, delta=blocks_to_est_days(range_first_blocks_overall))
        cols4[2].metric("In Largest Clique", range_first_blocks_clique, delta=blocks_to_est_days(range_first_blocks_clique))

        st.dataframe(nodes.drop(["coordinates", "location", "lat", "lon", "payer", "marker_size"], axis=1).style.hide(axis="index").background_gradient(cmap="Blues"))
        st.download_button(
            "Export CSV",
            nodes.to_csv().encode("utf-8"),
            "results.csv",
            "text/csv",
            key='download-csv'
        )

    except IndexError:
        st.error("No results found - we likely don't have data for this hotspot yet.")
