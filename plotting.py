import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import h3
import streamlit as st


def plot_histogram(plot_df, on_key: str):
    fig = px.histogram(plot_df, x=on_key, color="source", marginal="box", histnorm="probability", barmode="overlay")
    return fig


def plot_witness_distances(filtered_df: pd.DataFrame, baseline_df: pd.DataFrame, color_key: str = "source"):
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=filtered_df["med_distance"],
                               name="Filtered",
                               histnorm="probability density",
                               xbins=dict(  # bins used for histogram
                                   start=0,
                                   end=100,
                                   size=2.5
                               )
                               ))
    fig.add_trace(go.Histogram(x=baseline_df["med_distance"],
                               name="Baseline",
                               histnorm="probability density",
                               xbins=dict(  # bins used for histogram
                                   start=0,
                                   end=100,
                                   size=2.5
                               ),
                               ))

    # Overlay both histograms
    fig.update_layout(barmode="overlay")
    # Reduce opacity to see both histograms
    fig.update_traces(opacity=0.3)
    fig.update_layout(
        xaxis_title_text="Median Witness Distance, km",  # xaxis label
        yaxis_title_text="P(x)"  # yaxis label
    )
    return fig


def plot_avg_tx_reward_scales(filtered_df: pd.DataFrame, baseline_df: pd.DataFrame, color_key: str = "source"):
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=filtered_df["avg_tx_reward_scale"],
                               name="Filtered",
                               histnorm="probability density",
                               xbins=dict(
                                   start=0,
                                   end=1,
                                   size=0.025
                               )))
    fig.add_trace(go.Histogram(x=baseline_df["avg_tx_reward_scale"],
                               name="Baseline",
                               histnorm="probability density",
                               xbins=dict(
                                   start=0,
                                   end=1,
                                   size=0.025
                               )))

    # Overlay both histograms
    fig.update_layout(barmode="overlay")
    # Reduce opacity to see both histograms
    fig.update_traces(opacity=0.3)
    fig.update_layout(
        xaxis_title_text="Average Transmit Scale",  # xaxis label
        yaxis_title_text="P(x)"  # yaxis label
    )
    return fig


def plot_same_maker_ratio(filtered_df: pd.DataFrame, baseline_df: pd.DataFrame, color_key: str = "source"):
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=filtered_df["same_maker_ratio"],
                               name="Filtered",
                               histnorm="probability density",
                               xbins=dict(
                                   start=0,
                                   end=1,
                                   size=0.025
                               )))
    fig.add_trace(go.Histogram(x=baseline_df["same_maker_ratio"],
                               name="Baseline",
                               histnorm="probability density",
                               xbins=dict(
                                   start=0,
                                   end=1,
                                   size=0.025
                               )))

    # Overlay both histograms
    fig.update_layout(barmode="overlay")
    # Reduce opacity to see both histograms
    fig.update_traces(opacity=0.3)
    fig.update_layout(
        xaxis_title_text="Ratio of Witnessed Hotspots that have the Same Maker",  # xaxis label
        yaxis_title_text="P(x)"  # yaxis label
    )
    return fig


def plot_data_credits(filtered_df: pd.DataFrame, baseline_df: pd.DataFrame, color_key: str = "source"):
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=filtered_df["packets_transferred"],
                               name="Filtered",
                               histnorm="probability density",
                               xbins=dict(
                                   start=0,
                                   end=1000,
                                   size=10
                               )))
    fig.add_trace(go.Histogram(x=baseline_df["packets_transferred"],
                               name="Baseline",
                               histnorm="probability density",
                               xbins=dict(
                                   start=0,
                                   end=1000,
                                   size=10
                               )))

    # Overlay both histograms
    fig.update_layout(barmode="overlay")
    # Reduce opacity to see both histograms
    fig.update_traces(opacity=0.3)
    fig.update_layout(
        xaxis_title_text="Packets Transferred",  # xaxis label
        yaxis_title_text="P(x)"  # yaxis label
    )
    return fig


def plot_avg_tx_age_blocks(filtered_df: pd.DataFrame, baseline_df: pd.DataFrame, color_key: str = "source"):
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=filtered_df["avg_tx_age_blocks"],
                               name="Filtered",
                               histnorm="probability density",
                               xbins=dict(
                                   start=0,
                                   end=600e3,
                                   size=2500
                               )))
    fig.add_trace(go.Histogram(x=baseline_df["avg_tx_age_blocks"],
                               name="Baseline",
                               histnorm="probability density",
                               xbins=dict(
                                   start=0,
                                   end=600e3,
                                   size=2500
                               )))

    # Overlay both histograms
    fig.update_layout(barmode="overlay")
    # Reduce opacity to see both histograms
    fig.update_traces(opacity=0.3)
    fig.update_layout(
        xaxis_title_text="Average Age of Witnessed Hotspots (blocks)",  # xaxis label
        yaxis_title_text="P(x)"  # yaxis label
    )
    return fig


def plot_std_tx_first_block(filtered_df: pd.DataFrame, baseline_df: pd.DataFrame, color_key: str = "source"):
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=filtered_df["std_tx_first_block"],
                               name="Filtered",
                               histnorm="probability density",
                               xbins=dict(
                                   start=0,
                                   end=7500,
                                   size=250
                               )))
    fig.add_trace(go.Histogram(x=baseline_df["std_tx_first_block"],
                               name="Baseline",
                               histnorm="probability density",
                               xbins=dict(
                                   start=0,
                                   end=7500,
                                   size=250
                               )))

    # Overlay both histograms
    fig.update_layout(barmode="overlay")
    # Reduce opacity to see both histograms
    fig.update_traces(opacity=0.3)
    fig.update_layout(
        xaxis_title_text="Standard Deviation of First Blocks of Witnessed (blocks)",  # xaxis label
        yaxis_title_text="P(x)"  # yaxis label
    )
    return fig


def plot_data_transfer(filtered_df: pd.DataFrame, baseline_df: pd.DataFrame):

    labels = ["Transferred Packets", "No Data Transfer"]
    fig = make_subplots(rows=1, cols=2, specs=[[{'type':'domain'}, {'type':'domain'}]])
    fig.add_trace(go.Pie(labels=labels, values=[len(filtered_df[filtered_df["packets_transferred"] > 0]) / len(filtered_df),
                                                len(filtered_df[filtered_df["packets_transferred"] < 1]) / len(filtered_df)]), 1,1)
    fig.add_trace(go.Pie(labels=labels, values=[len(baseline_df[baseline_df["packets_transferred"] > 0]) / len(baseline_df),
                                                len(baseline_df[baseline_df["packets_transferred"] < 1]) / len(baseline_df)]), 1,2)
    fig.update_traces(hole=.4, hoverinfo="label+percent+name")

    fig.update_layout(
        # Add annotations in the center of the donut pies.
        annotations=[dict(text="Filtered", x=0.18, y=0.5, font_size=20, showarrow=False),
                     dict(text="Baseline", x=0.82, y=0.5, font_size=20, showarrow=False)])
    return fig


def plot_manufacturer_breakdown(filtered_df: pd.DataFrame):
    fig = px.pie(filtered_df, names="name_maker")
    fig.update_layout(
        title_text="Manufacturers in Subset"
    )
    return fig


def plot_denylist_breakdown(filtered_df: pd.DataFrame, baseline_df: pd.DataFrame):

    labels = ["Denied at Some Point", "Never Denied"]
    fig = make_subplots(rows=1, cols=2, specs=[[{'type':'domain'}, {'type':'domain'}]])
    fig.add_trace(go.Pie(labels=labels, values=[len(filtered_df[filtered_df["denied_at_some_point"] == True]) / len(filtered_df),
                                                len(filtered_df[filtered_df["denied_at_some_point"] == False]) / len(filtered_df)]), 1,1)
    fig.add_trace(go.Pie(labels=labels, values=[len(baseline_df[baseline_df["denied_at_some_point"] == True]) / len(baseline_df),
                                                len(baseline_df[baseline_df["denied_at_some_point"] == False]) / len(baseline_df)]), 1,2)
    fig.update_traces(hole=.4, hoverinfo="label+percent+name")

    fig.update_layout(
        # Add annotations in the center of the donut pies.
        annotations=[dict(text="Filtered", x=0.18, y=0.5, font_size=20, showarrow=False),
                     dict(text="Baseline", x=0.82, y=0.5, font_size=20, showarrow=False)])
    return fig


def plot_ownership_breakdown(filtered_df: pd.DataFrame, baseline_df: pd.DataFrame):
    hotspots_by_owner_filtered = pd.DataFrame(filtered_df.groupby("owner").size())
    hotspots_by_owner_filtered["source"] = "filtered"
    baseline_df["source"] = "baseline"
    plot_df = pd.concat([hotspots_by_owner_filtered, baseline_df])

    fig = px.histogram(plot_df, x=plot_df[0], color="source", marginal="box", histnorm="probability", barmode="overlay")

    return fig


def plot_hotspot_locations(filtered_df: pd.DataFrame, color_key: str = "rx_on_denylist"):
    # not sure why result_type = "expand" isn't doing this in one step

    filtered_df["coords"] = filtered_df["location"].apply(h3.h3_to_geo)
    filtered_df["lat"] = filtered_df["coords"].apply(lambda x: x[0])
    filtered_df["lon"] = filtered_df["coords"].apply(lambda x: x[1])

    fig = px.scatter_mapbox(filtered_df, lat="lat", lon="lon", hover_name="address_gateway", color=color_key)
    fig.update_layout(mapbox_style="dark",
                      # mapbox_accesstoken=os.getenv("MAPBOX_API_KEY"),
                      showlegend=False,
                      mapbox_zoom=3,
                      mapbox_center=dict(
                          lat=filtered_df["lat"].iloc[0],
                          lon=filtered_df["lon"].iloc[0]
                      ),
                      margin={'l':0, 'r':0, 'b':0, 't':0})
    return fig


def zscore(mu, std, sample_mean):
    return np.round((sample_mean - mu) / std, 1)


def generate_metrics(filtered_df: pd.DataFrame, baseline_df: pd.DataFrame, feature_key: str):
    baseline_mean, baseline_std = baseline_df[feature_key].mean(), baseline_df[feature_key].std()
    filtered_mean, filtered_std = filtered_df[feature_key].mean(), filtered_df[feature_key].std()

    cols = st.columns(5)

    cols[0].metric("Baseline Median", value=np.round(baseline_mean, 1))
    cols[1].metric("Baseline Middle 95%", value=np.round(baseline_std, 1))
    cols[2].metric("Filtered Median", value=np.round(filtered_mean, 1))
    cols[3].metric("Filtered Middle 95%", value=np.round(filtered_std, 1))
    cols[4].metric("Z-Score of Filtered",
                    value=zscore(baseline_mean, baseline_std, filtered_mean))
    return cols