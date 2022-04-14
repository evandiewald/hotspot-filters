import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import h3


def plot_witness_counts(filtered_df: pd.DataFrame, baseline_df: pd.DataFrame, color_key: str = "source"):
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=filtered_df["n_witnessed"],
                               name="Filtered",
                               histnorm="probability density",
                               xbins=dict(
                                   size=5
                               )))
    fig.add_trace(go.Histogram(x=baseline_df["n_witnessed"],
                               name="Baseline",
                               histnorm="probability density",
                               xbins=dict(
                                   size=5
                               )))

    # Overlay both histograms
    fig.update_layout(barmode="overlay")
    # Reduce opacity to see both histograms
    fig.update_traces(opacity=0.3)
    fig.update_layout(
        title_text="Witness Counts",  # title of plot
        xaxis_title_text="Number of Unique Witnesses",  # xaxis label
        yaxis_title_text="P(x)"  # yaxis label
    )
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
        title_text="Witness Distances",  # title of plot
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
        title_text="Reward Scales of Witnessed Hotspots",  # title of plot
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
        title_text="Same-Maker Witnessing",  # title of plot
        xaxis_title_text="Ratio of Witnessed Hotspots that have the Same Maker",  # xaxis label
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
        title_text="Age of Witnessed Hotspots",  # title of plot
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
        title_text="Variability in Assertion Time",  # title of plot
        xaxis_title_text="Standard Deviation of First Blocks of Witnessed (blocks)",  # xaxis label
        yaxis_title_text="P(x)"  # yaxis label
    )
    return fig


def plot_manufacturer_breakdown(filtered_df: pd.DataFrame):
    fig = px.pie(filtered_df, names="name_maker")
    fig.update_layout(
        title_text="Manufacturers in Subset"
    )
    return fig


def plot_denylist_breakdown(filtered_df: pd.DataFrame):
    fig = px.pie(filtered_df, names="denied_at_some_point")
    fig.update_layout(
        title_text="Any-time Denied Hotspots in Subset"
    )
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
