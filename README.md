# hotspot-filters

Filtering tool to identify and analyze hotspots with common characteristics.

## Getting Started
- Follow the instructions to run a [transaction ETL](https://github.com/evandiewald/helium-transaction-etl)
- Make a copy of `.env.template` called `.env` and insert your postgres connection string.
- `pip install -r requirements.txt`
  - `psycopg2` may need to be installed separately. Use `psycopg2[binary]` on Ubuntu.
- `streamlit run app.py`
The query is relatively time-consuming and will cache daily by default.
