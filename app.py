from sqlalchemy.engine import create_engine, Engine
from dotenv import load_dotenv
from loaders import *
from filters import *
from plotting import *
import plotly.express as px


load_dotenv()
token = open(".mapbox_token").read() if ".mapbox_token" in os.listdir() else os.getenv("MAPBOX_TOKEN")
px.set_mapbox_access_token(token)

engine = create_engine(os.getenv("POSTGRES_CONNECTION_STRING"))


@st.experimental_memo(ttl=86400)
def load_data(_engine):
    dataset = load_dataset(_engine)
    baseline_df = dataset.sample(10000) # cache a baseline for comparison
    hotspots_per_account = pd.DataFrame(dataset.groupby("owner").size())
    options = get_form_config(dataset)
    options.countries.insert(0,"All")
    options.makers.insert(0,"All")

    n_blocks_in_dataset = _engine.execute(n_blocks_sql).one()[0]
    return dataset, baseline_df, hotspots_per_account, options, n_blocks_in_dataset


dataset, baseline_df, hotspots_per_account, options, n_blocks_in_dataset = load_data(engine)

st.title("Hotspot POC Filtering")
st.markdown(f"""This tool is useful for combing through the entire hotspot population based on common metrics related to POC.
Results, which are refreshed daily, are based on challenge receipts and data transfer metrics for the last `{n_blocks_in_dataset}` blocks.
See [`helium-transaction-etl`](https://github.com/evandiewald/helium-transaction-etl).""")

with st.form("filters_form") as form:
    # makers
    with st.expander("Makers"):
        makers = st.multiselect("Manufacturer(s)", options=options.makers, default="All")
        # only witnesses same maker
        same_maker_only = st.checkbox("Only include hotspots that exclusively witness others of the same manufacturer.")

    # countries
    with st.expander("Countries"):
        countries = st.multiselect("Countries", options=options.countries, default="All")

    # data transfer
    with st.expander("Data Transfer"):
        data_transfer_opts = st.radio("Data Transfer", ["Data Transferring Hotspots ONLY", "NO Data Transferring Hotspots ONLY", "Custom Range"],
                                      index=2)
        data_transfer_slider_disabled: bool = False if data_transfer_opts == "Custom Range" else True
        data_transfer_range = st.slider("Select percentile range of data transferring hotspots",
                                        min_value=0, max_value=100, value=(0, 100), step=1, disabled=data_transfer_slider_disabled)

    # witnessing numbers
    # with st.expander("Witness Counts"):
    #     n_witnessed_range = st.slider("Select percentile range of number of unique witnesses.",
    #                                   min_value=0, max_value=100, value=(0, 100), step=1)
    #     total_witnessed_range = st.slider("Select percentile range for total number of witness events.",
    #                                   min_value=0, max_value=100, value=(0, 100), step=1)

    # distances
    with st.expander("Witness Distances"):
        st.markdown("**Minimum** Witness Distance (the distance between this hotspot and its *nearest* witness)")
        min_distance_min = st.number_input("MINIMUM Witness Distance must be GREATER THAN (km):", value=0)
        min_distance_max = st.number_input("MINIMUM Witness Distance must be LESS THAN (km):", value=100000)
        st.markdown("**Maximum** Witness Distance (the distance between this hotspot and its *furthest* witness)")
        max_distance_min = st.number_input("MAXIMUM Witness Distance must be GREATER THAN (km):", value=0)
        max_distance_max = st.number_input("MAXIMUM Witness Distance must be LESS THAN (km):", value=100000)

    # first_block
    with st.expander("Assertion Times"):
        first_block_max = st.number_input("Only include hotspots asserted BEFORE block", value=9999999, min_value=0)
        first_block_min = st.number_input("Only include hotspots asserted AFTER block", value=0, min_value=0)

    # transmit scale
    with st.expander("Reward Scales"):
        perfect_reward_scale_only = st.checkbox("Only include hotspots who only witness beaconers with an optimal reward scale.")
        avg_tx_reward_scale_range = st.slider("Select range of average reward scales.",
                                      min_value=0.0, max_value=1.0, value=(0., 1.), step=0.05, disabled=perfect_reward_scale_only)
        std_tx_reward_scale_range = st.slider("Select range of standard deviations in reward scales.",
                                      min_value=0.0, max_value=1.0, value=(0., 1.), step=0.05, disabled=perfect_reward_scale_only)

    # antenna gain / elevation
    # with st.expander("Antenna Gain / Elevation"):
    #     gain_range = st.slider("Select range of antenna gains (dB).",
    #                            min_value=10, max_value=150, value=(10, 150), step=10)
    #     elevation_range = st.slider("Select percentile range of elevations.",
    #                            min_value=0, max_value=100, value=(0, 100), step=1)

    # average / std age of transmitters
    # with st.expander("Age and Variability of Witnessed Hotspots"):
    #     avg_tx_age_blocks_range = st.slider("Select range of average beaconer age (blocks).",
    #                                   min_value=0, max_value=int(5e5), value=(0, int(5e5)), step=1000)
    #     std_tx_age_blocks_range = st.slider("Select range of variability in beaconer age (blocks).",
    #                                   min_value=0, max_value=int(5e5), value=(0, int(1e5)), step=1000)

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
        countries=countries,
        data_transfer_opts=data_transfer_opts,
        data_transfer_range=data_transfer_range,
        first_block_max=first_block_max,
        first_block_min=first_block_min,
        # n_witnessed_range=n_witnessed_range,
        # total_witnessed_range=total_witnessed_range,
        min_distance_min=min_distance_min,
        min_distance_max=min_distance_max,
        max_distance_min=max_distance_min,
        max_distance_max=max_distance_max,
        perfect_reward_scale_only=perfect_reward_scale_only,
        avg_tx_reward_scale_range=avg_tx_reward_scale_range,
        std_tx_reward_scale_range=std_tx_reward_scale_range,
        witnesses_denylisted_tx=witnesses_denylisted_tx,
        same_maker_only=same_maker_only,
        # avg_tx_age_blocks_range=avg_tx_age_blocks_range,
        # std_tx_age_blocks_range=std_tx_age_blocks_range,
        reasserted_hotspots_only=reasserted_hotspots_only,
        # gain_range=gain_range,
        # elevation_range=elevation_range,
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
                    color_key = "denied_at_some_point"
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

                st.subheader("RSSI vs SNR R2")
                st.plotly_chart(plot_histogram(plot_df, "r2_rssi_snr"))

                st.subheader("RSSI vs Distance Slope")
                st.plotly_chart(plot_histogram(plot_df, "slope_rssi_snr"))


