# Retail Pulse

An interactive sales dashboard built with **Streamlit** and **Plotly**, exploring 1M+ retail transactions from 2009 to 2011.

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://YOUR-APP-NAME.streamlit.app)

**Live app:** https://YOUR-APP-NAME.streamlit.app

![Retail Pulse dashboard](screenshot.png)

## What it does

- **KPI cards** with change versus the previous period and monthly sparklines: revenue, invoices, customers, average order value and return rate.
- **Trends:** area, line, bar or step charts at daily, weekly or monthly level, with a moving average and a year-over-year view.
- **Geography:** bar, treemap, donut or world map of sales by country.
- **Products:** bar, lollipop, treemap or bubble charts of the top products.
- **Patterns:** heatmap, weekday bars, hourly line or polar clock showing when customers buy.
- **Customers:** top customers, Pareto curve and invoice-value distribution.
- **Data explorer:** search transactions and download the filtered rows as CSV.
- Filters for date range, country and returns, a revenue or units switch, and light and dark themes.

## Tech stack

Python, Streamlit, Plotly, pandas, NumPy, PyArrow (Parquet).

## Run it locally

```bash
git clone https://github.com/YOUR-USERNAME/YOUR-REPO.git
cd YOUR-REPO
pip install -r requirements.txt
streamlit run app.py
```

The data is stored as `retail_clean.parquet`, which loads much faster than CSV. To rebuild it from a CSV, run `python convert_to_parquet.py`.

## Data

Online retail transactions (invoice, product, quantity, date, customer, country, line total). Returns appear as negative quantities and credit-note invoices starting with "C".
