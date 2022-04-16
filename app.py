import plistlib

from sqlalchemy.engine import create_engine, Engine
from dotenv import load_dotenv
from loaders import *
from filters import *
from plotting import *
import plotly.express as px


load_dotenv()
px.set_mapbox_access_token(open(".mapbox_token").read())

engine = create_engine(os.getenv("POSTGRES_CONNECTION_STRING"))

dataset = load_dataset(engine)
baseline_df = dataset.sample(10000) # cache a baseline for comparison
hotspots_per_account = pd.DataFrame(dataset.groupby("owner").size())
options = get_form_config(dataset)

st.title("Hotspot POC Filtering")
st.markdown("""This tool is useful for combing through the entire hotspot population based on common metrics related to POC.
Results, which are refreshed daily, are based on challenge receipts and data transfer metrics for the last `15,000` blocks.
See [`helium-transaction-etl`](https://github.com/evandiewald/helium-transaction-etl).""")

with st.form("filters_form") as form:
    # makers
    with st.expander("Makers"):
        makers = st.multiselect("Manufacturer(s)", options=options.makers, default=options.makers)
        # only witnesses same maker
        same_maker_only = st.checkbox("Only include hotspots that exclusively witness others of the same manufacturer.")

    # data transfer
    with st.expander("Data Transfer"):
        data_transfer_opts = st.radio("Data Transfer", ["Data Transferring Hotspots ONLY", "NO Data Transferring Hotspots ONLY", "Custom Range"],
                                      index=2)
        data_transfer_slider_disabled: bool = False if data_transfer_opts == "Custom Range" else True
        data_transfer_range = st.slider("Select percentile range of data transferring hotspots",
                                        min_value=0, max_value=100, value=(0, 100), step=1, disabled=data_transfer_slider_disabled)

    # witnessing numbers
    with st.expander("Witness Counts"):
        n_witnessed_range = st.slider("Select percentile range of number of unique witnesses.",
                                      min_value=0, max_value=100, value=(0, 100), step=1)
        total_witnessed_range = st.slider("Select percentile range for total number of witness events.",
                                      min_value=0, max_value=100, value=(0, 100), step=1)

    # distances
    with st.expander("Witness Distances"):
        med_distance_range = st.slider("Select percentile range of median witness distances.",
                                      min_value=0, max_value=100, value=(0, 100), step=1)
        max_distance_range = st.slider("Select percentile range of max witness distances.",
                                      min_value=0, max_value=100, value=(0, 100), step=1)

    # transmit scale
    with st.expander("Reward Scales"):
        perfect_reward_scale_only = st.checkbox("Only include hotspots who only witness beaconers with an optimal reward scale.")
        avg_tx_reward_scale_range = st.slider("Select range of average reward scales.",
                                      min_value=0.0, max_value=1.0, value=(0., 1.), step=0.05, disabled=perfect_reward_scale_only)
        std_tx_reward_scale_range = st.slider("Select range of standard deviations in reward scales.",
                                      min_value=0.0, max_value=1.0, value=(0., 1.), step=0.05, disabled=perfect_reward_scale_only)

    # antenna gain / elevation
    with st.expander("Antenna Gain / Elevation"):
        gain_range = st.slider("Select range of antenna gains (dB).",
                               min_value=10, max_value=150, value=(10, 150), step=10)
        elevation_range = st.slider("Select percentile range of elevations.",
                               min_value=0, max_value=100, value=(0, 100), step=1)

    # average / std age of transmitters
    with st.expander("Age and Variability of Witnessed Hotspots"):
        avg_tx_age_blocks_range = st.slider("Select range of average beaconer age (blocks).",
                                      min_value=0, max_value=int(5e5), value=(0, int(5e5)), step=1000)
        std_tx_age_blocks_range = st.slider("Select range of variability in beaconer age (blocks).",
                                      min_value=0, max_value=int(5e5), value=(0, int(1e5)), step=1000)

    # hotspot has been moved
    with st.expander("Re-asserted Hotspots"):
        reasserted_hotspots_only = st.checkbox("Only include hotspots that have been reasserted.")

    # denylist
    with st.expander("Denylist"):
        on_current_denylist = st.checkbox("Only include hotspots on the CURRENT denylist.")
        on_any_denylist = st.checkbox("Only include hotspots on ANY iteration of the denylist.", disabled=on_current_denylist)
        previously_denied = st.checkbox("Only include hotspots that were denied in a previous iteration of the denylist, but not the current version", disabled=on_current_denylist)
        never_denied = st.checkbox("Only include hotspots that have never been denied.", disabled=on_current_denylist)
        # witnesses a denylisted transmitter
        witnesses_denylisted_tx = st.checkbox("Only include hotspots that have witnessed a denylisted hotspot.")

    categorize_by = st.radio("Categorize Plots by", ["Denylist Status", "Manufacturer"])
    display_df = st.checkbox("Show Result Set Dataframe")
    display_plots = st.checkbox("Show plots")
    submit = st.form_submit_button("Submit")


if submit:
    filters = Filters(
        makers=makers,
        data_transfer_opts=data_transfer_opts,
        data_transfer_range=data_transfer_range,
        n_witnessed_range=n_witnessed_range,
        total_witnessed_range=total_witnessed_range,
        med_distance_range=med_distance_range,
        max_distance_range=max_distance_range,
        perfect_reward_scale_only=perfect_reward_scale_only,
        avg_tx_reward_scale_range=avg_tx_reward_scale_range,
        std_tx_reward_scale_range=std_tx_reward_scale_range,
        witnesses_denylisted_tx=witnesses_denylisted_tx,
        same_maker_only=same_maker_only,
        avg_tx_age_blocks_range=avg_tx_age_blocks_range,
        std_tx_age_blocks_range=std_tx_age_blocks_range,
        reasserted_hotspots_only=reasserted_hotspots_only,
        gain_range=gain_range,
        elevation_range=elevation_range,
        on_current_denylist=on_current_denylist,
        on_any_denylist=on_any_denylist,
        previously_denied=previously_denied,
        never_denied=never_denied
    )
    filtered_df = filter_dataset(dataset, filters)

    filtered_df["source"] = "filtered"
    baseline_df["source"] = "baseline"
    plot_df = pd.concat([filtered_df, baseline_df])

    n_results = len(filtered_df)
    st.metric("Number of Hotspots in Subset", value=n_results)

    with st.spinner("Generating Plots..."):
        if n_results > 100e3:
            st.warning("Result set is too large to display dataframe.")
        else:
            if display_df:
                st.dataframe(filtered_df)
                st.download_button(
                    "Export CSV",
                    filtered_df.to_csv().encode("utf-8"),
                    "results.csv",
                    "text/csv",
                    key='download-csv'
                )

            if display_plots:
                if categorize_by == "Denylist Status":
                    color_key = "rx_on_denylist"
                else:
                    color_key = "name_maker"

                st.subheader("Denylist Breakdown")
                st.plotly_chart(plot_denylist_breakdown(filtered_df, baseline_df))

                st.subheader("Hotspot Locations")
                st.plotly_chart(plot_hotspot_locations(filtered_df, color_key))

                st.subheader("Ownership Patterns")
                st.plotly_chart(plot_ownership_breakdown(filtered_df, hotspots_per_account))

                st.subheader("Witness Counts")
                st.plotly_chart(plot_histogram(plot_df, "n_witnessed"))

                st.subheader("Witness Distances")
                st.plotly_chart(plot_histogram(plot_df, "med_distance"))

                st.subheader("Data Transfer")
                st.plotly_chart(plot_data_transfer(filtered_df, baseline_df))

                st.subheader("Reward Scales of Witnessed")
                st.plotly_chart(plot_histogram(plot_df, "avg_tx_reward_scale"))

                st.subheader("Same-Maker Witnessing")
                st.plotly_chart(plot_histogram(plot_df, "same_maker_ratio"))

                st.subheader("Age of Witnessed Hotspots")
                st.plotly_chart(plot_histogram(plot_df, "avg_tx_age_blocks"))

                st.subheader("Variability in Age of Witnessed Hotspots")
                st.plotly_chart(plot_histogram(plot_df, "std_tx_first_block"))

                st.subheader("RSSI vs Distance R2")
                st.plotly_chart(plot_histogram(plot_df, "r2_rssi_distance"))

                st.subheader("RSSI vs Distance Slope")
                st.plotly_chart(plot_histogram(plot_df, "slope_rssi_distance"))


