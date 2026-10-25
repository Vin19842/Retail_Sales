from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(
    page_title="Retail Pulse",
    page_icon=":material/storefront:",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ── Theme ────────────────────────────────────────────────────────────────────
# Colours are theme-neutral: text, page and widget colours all come from
# Streamlit's own theme, so light and dark both render correctly.
# Switch themes from the app menu (top right).

palette = {
    "text": "#8b98a9",
    "muted": "#8b98a9",
    "border": "rgba(128,128,128,.28)",
    "grid": "rgba(128,128,128,.18)",
    "card_bg": "rgba(128,128,128,.07)",
    "accent": "#3b82f6",
    "accent_2": "#6366f1",
    "accent_3": "#f59e0b",
    "accent_soft": "rgba(59,130,246,.14)",
    "chart_low": "#9cc5ff",
    "hover_bg": "rgba(15,23,42,.96)",
    "heat_low": "rgba(128,128,128,.12)",
    "heat_mid": "#8bb8fb",
    "fill": "rgba(59,130,246,.15)",
    "negative": "#ef4444",
}
plotly_template = "none"

css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, .stApp, [data-testid="stSidebar"] { font-family: 'Inter', sans-serif; }
    [data-testid="stHeader"] { background: transparent; }
    .stAppDeployButton { display: none; }
    .block-container { max-width: 1500px; padding-top: 1.4rem; padding-bottom: 3rem; }

    h1, h2, h3, h4 { letter-spacing: -.01em; }
    h3 { font-size: 1.05rem !important; font-weight: 650 !important; margin-bottom: .1rem; }

    /* Top bar */
    .topbar {
        display: flex; align-items: center; justify-content: space-between;
        gap: 24px; flex-wrap: wrap;
        padding: 2px 0 18px; margin-bottom: 20px;
        border-bottom: 1px solid __BORDER__;
    }
    .brand { display: flex; align-items: center; gap: 14px; }
    .logo {
        width: 40px; height: 40px; border-radius: 10px; background: __ACCENT__;
        display: flex; align-items: center; justify-content: center;
    }
    .brand-title { font-size: 1.5rem; font-weight: 700; line-height: 1.15; }
    .brand-sub { font-size: .82rem; opacity: .65; margin-top: 2px; }
    .meta { display: flex; gap: 34px; flex-wrap: wrap; }
    .meta-item .k {
        font-size: .66rem; font-weight: 600; text-transform: uppercase;
        letter-spacing: .09em; opacity: .6;
    }
    .meta-item .v { font-size: .9rem; font-weight: 600; margin-top: 2px; }

    .section-label {
        opacity: .6; font-size: .68rem; font-weight: 600;
        letter-spacing: .12em; text-transform: uppercase; margin: 0 0 .5rem 0;
    }

    /* Cards */
    [data-testid="stVerticalBlockBorderWrapper"] {
        border-color: __BORDER__ !important;
        border-radius: 12px;
        background: __CARD_BG__;
    }
    [data-testid="stMetricLabel"] p { opacity: .72; font-size: .8rem; font-weight: 500; }
    [data-testid="stMetricValue"] { font-size: 1.75rem; font-weight: 700; letter-spacing: -.02em; }

    /* Tabs: classic underline */
    [data-baseweb="tab-list"] { gap: 4px; border-bottom: 1px solid __BORDER__; }
    [data-baseweb="tab-border"] { display: none; }
    [data-baseweb="tab-highlight"] { background-color: __ACCENT__ !important; height: 2px; }
    button[data-baseweb="tab"] { font-weight: 600; padding: 10px 16px; height: auto; }
    button[data-baseweb="tab"][aria-selected="true"] p { color: __ACCENT__ !important; }

    [data-testid="stSlider"] [role="slider"] { background-color: __ACCENT__ !important; }
    [data-testid="stSliderThumbValue"] { color: __ACCENT__ !important; }

    [data-testid="stBaseButton-segmented_controlActive"] {
        background: __ACCENT_SOFT__ !important; border-color: __ACCENT__ !important;
    }

    .insight {
        background: __CARD_BG__; border: 1px solid __BORDER__; border-left: 3px solid __ACCENT__;
        border-radius: 8px; padding: 10px 16px; font-size: .88rem; margin: .6rem 0 1rem 0;
    }
    .insight b { font-weight: 650; }

    .stButton button, [data-testid="stDownloadButton"] button { border-radius: 8px; font-weight: 600; }
    [data-testid="stSidebar"] { border-right: 1px solid __BORDER__; }

    /* Chart text follows the app's text colour; tooltips stay light-on-dark */
    .js-plotly-plot .plotly text { fill: currentColor !important; }
    .js-plotly-plot .plotly .hoverlayer text { fill: #f1f5f9 !important; }
</style>
"""
for token, value in {
    "__CARD_BG__": palette["card_bg"],
    "__BORDER__": palette["border"],
    "__ACCENT__": palette["accent"],
    "__ACCENT_SOFT__": palette["accent_soft"],
}.items():
    css = css.replace(token, value)
st.markdown(css, unsafe_allow_html=True)


# ── Data ─────────────────────────────────────────────────────────────────────

@st.cache_data(show_spinner="Loading retail data…")
def load_data():
    parquet_path = Path("retail_clean.parquet")
    csv_path = Path("retail_clean.csv")

    if parquet_path.exists():
        data = pd.read_parquet(parquet_path)
    elif csv_path.exists():
        data = pd.read_csv(csv_path, parse_dates=["InvoiceDate"])
    else:
        raise FileNotFoundError(
            "Place retail_clean.parquet (or retail_clean.csv) in the same folder as app.py."
        )

    data["InvoiceDate"] = pd.to_datetime(data["InvoiceDate"], errors="coerce")
    data["Quantity"] = pd.to_numeric(data["Quantity"], errors="coerce")
    data["LineTotal"] = pd.to_numeric(data["LineTotal"], errors="coerce")
    data = data.dropna(subset=["InvoiceDate"])
    data["Month"] = data["InvoiceDate"].dt.to_period("M").dt.to_timestamp()
    return data


try:
    df = load_data()
except FileNotFoundError as error:
    st.error(str(error))
    st.stop()

required_columns = {
    "Invoice", "StockCode", "Description", "Quantity",
    "InvoiceDate", "Customer ID", "Country", "LineTotal",
}
missing_columns = sorted(required_columns.difference(df.columns))
if missing_columns:
    st.error(f"CSV is missing columns: {', '.join(missing_columns)}")
    st.stop()


# ── Sidebar ──────────────────────────────────────────────────────────────────

min_date = df["InvoiceDate"].min().date()
max_date = df["InvoiceDate"].max().date()


def reset_filters():
    st.session_state["f_dates"] = (min_date, max_date)
    st.session_state["f_countries"] = []
    st.session_state["f_returns"] = True


with st.sidebar:
    st.markdown("## :material/storefront: Retail Pulse")
    st.caption("Sales intelligence dashboard")
    st.divider()

    st.markdown("**Chart metric**")
    measure = st.segmented_control(
        "Chart metric",
        ["Revenue", "Units sold"],
        default="Revenue",
        key="measure",
        label_visibility="collapsed",
        help="Controls what the charts show. KPI cards always show revenue.",
    ) or "Revenue"

    st.markdown("**Filters**")
    date_range = st.date_input(
        "Invoice date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        key="f_dates",
    )

    countries = sorted(df["Country"].dropna().astype(str).unique())
    selected_countries = st.multiselect(
        "Countries",
        options=countries,
        default=[],
        placeholder="All countries",
        help="Leave empty to include every country.",
        key="f_countries",
    )

    include_returns = st.toggle("Include returns", value=True, key="f_returns")

    st.button("Reset filters", icon=":material/restart_alt:", on_click=reset_filters,
              width="stretch")

    st.divider()
    st.caption(
        "Revenue in GBP. Returns have negative quantities. "
        "Switch light/dark from the app menu (top right)."
    )


# ── Helpers ──────────────────────────────────────────────────────────────────

IS_REVENUE = measure == "Revenue"
VALUE_COL = "LineTotal" if IS_REVENUE else "Quantity"
PREFIX = "£" if IS_REVENUE else ""
MEASURE_NOUN = "Revenue" if IS_REVENUE else "Units"
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
SEQ_SCALE = [palette["chart_low"], palette["accent"]]
SEQ_SCALE_2 = [palette["chart_low"], palette["accent_2"]]
HEAT_SCALE = [palette["heat_low"], palette["heat_mid"], palette["accent"]]

COUNTRY_FIX = {
    "EIRE": "Ireland",
    "RSA": "South Africa",
    "USA": "United States",
    "Channel Islands": "Jersey",
    "West Indies": "Jamaica",
    "Korea": "South Korea",
}


def money(value, prefix=PREFIX):
    sign = "-" if value < 0 else ""
    value = abs(value)
    if value >= 1_000_000:
        return f"{sign}{prefix}{value / 1_000_000:,.2f}M"
    if value >= 10_000:
        return f"{sign}{prefix}{value / 1_000:,.1f}K"
    return f"{sign}{prefix}{value:,.0f}"


def style_chart(fig, height=380):
    fig.update_layout(
        template=plotly_template,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, Arial, sans-serif", color=palette["text"], size=12),
        hoverlabel=dict(
            bgcolor=palette["hover_bg"],
            bordercolor=palette["border"],
            font_color="#f1f5f9",
        ),
        height=height,
        margin=dict(l=10, r=10, t=24, b=10),
        legend=dict(orientation="h", y=1.1, x=1, xanchor="right", title_text=""),
    )
    fig.update_xaxes(showgrid=False, zeroline=False, linecolor=palette["border"], automargin=True)
    fig.update_yaxes(zeroline=False, gridcolor=palette["grid"], automargin=True)
    return fig


def show(fig):
    with st.container(border=True):
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False}, theme=None)


def insight(text):
    st.markdown(f'<div class="insight">{text}</div>', unsafe_allow_html=True)


def chart_picker(label, options, key, default=0):
    return st.segmented_control(
        label, options, default=options[default], key=key, label_visibility="collapsed"
    ) or options[default]


def section_header(title, caption=None):
    st.markdown(f"### {title}")
    if caption:
        st.caption(caption)


# ── Filters ──────────────────────────────────────────────────────────────────

if not isinstance(date_range, (tuple, list)) or len(date_range) != 2:
    st.info("Select both a start date and an end date.")
    st.stop()

start_date, end_date = date_range


def apply_filters(frame, start, end):
    end_exclusive = pd.Timestamp(end) + pd.Timedelta(days=1)
    out = frame.loc[
        frame["InvoiceDate"].ge(pd.Timestamp(start)) & frame["InvoiceDate"].lt(end_exclusive)
    ]
    if selected_countries:
        out = out.loc[out["Country"].isin(selected_countries)]
    if not include_returns:
        out = out.loc[out["Quantity"].ge(0)]
    return out.copy()


view = apply_filters(df, start_date, end_date)

period_days = (pd.Timestamp(end_date) - pd.Timestamp(start_date)).days + 1
prev_end = pd.Timestamp(start_date) - pd.Timedelta(days=1)
prev_start = prev_end - pd.Timedelta(days=period_days - 1)
prev_view = apply_filters(df, prev_start, prev_end)


# ── Hero ─────────────────────────────────────────────────────────────────────

LOGO = (
    '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">'
    '<rect x="3" y="13" width="4" height="8" rx="1" fill="#fff"/>'
    '<rect x="10" y="8" width="4" height="13" rx="1" fill="#fff"/>'
    '<rect x="17" y="3" width="4" height="18" rx="1" fill="#fff"/></svg>'
)
market_text = (
    f"{len(selected_countries)} selected" if selected_countries else "All countries"
)
st.markdown(
    f"""
    <div class="topbar">
        <div class="brand">
            <div class="logo">{LOGO}</div>
            <div>
                <div class="brand-title">Retail Pulse</div>
                <div class="brand-sub">Sales performance dashboard</div>
            </div>
        </div>
        <div class="meta">
            <div class="meta-item"><div class="k">Period</div>
                <div class="v">{start_date:%d %b %Y} – {end_date:%d %b %Y}</div></div>
            <div class="meta-item"><div class="k">Markets</div><div class="v">{market_text}</div></div>
            <div class="meta-item"><div class="k">Metric</div><div class="v">{measure}</div></div>
            <div class="meta-item"><div class="k">Returns</div>
                <div class="v">{'Included' if include_returns else 'Excluded'}</div></div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

if view.empty:
    st.info("No rows match these filters. Try a wider date range or more countries.")
    st.stop()

view = view.assign(Value=view[VALUE_COL])


# ── KPIs (native metrics with deltas and sparklines) ─────────────────────────

def compute_kpis(frame):
    if frame.empty:
        return dict(revenue=0.0, invoices=0, customers=0, aov=0.0, return_rate=0.0)
    inv = frame["Invoice"].astype(str)
    sales_invoices = inv.loc[~inv.str.upper().str.startswith("C")].nunique()
    gross = frame.loc[frame["Quantity"].ge(0), "LineTotal"].sum()
    return dict(
        revenue=float(frame["LineTotal"].sum()),
        invoices=int(sales_invoices),
        customers=int(frame["Customer ID"].nunique()),
        aov=float(gross / sales_invoices) if sales_invoices else 0.0,
        return_rate=float(frame["Quantity"].lt(0).mean() * 100),
    )


def monthly_kpis(frame):
    m = frame.assign(
        _ret=frame["Quantity"].lt(0),
        _sale=~frame["Invoice"].astype(str).str.upper().str.startswith("C"),
    )
    grouped = m.groupby("Month")
    invoices = m[m["_sale"]].groupby("Month")["Invoice"].nunique()
    gross = m[m["Quantity"].ge(0)].groupby("Month")["LineTotal"].sum()
    out = pd.DataFrame({
        "revenue": grouped["LineTotal"].sum(),
        "invoices": invoices,
        "customers": grouped["Customer ID"].nunique(),
        "aov": gross / invoices,
        "return_rate": grouped["_ret"].mean() * 100,
    })
    return out.replace([np.inf, -np.inf], np.nan).fillna(0)


cur, prev = compute_kpis(view), compute_kpis(prev_view)
has_prev = not prev_view.empty
spark = monthly_kpis(view)


def metric_card(label, value, key, inverse=False):
    delta, delta_color = None, "off"
    if has_prev and prev[key]:
        change = (cur[key] - prev[key]) / abs(prev[key]) * 100
        delta = f"{change:+.1f}%"
        delta_color = "inverse" if inverse else "normal"
    kwargs = dict(
        label=label, value=value, delta=delta, delta_color=delta_color,
        help=f"Change versus the previous {period_days} days." if delta else
             "No earlier period available to compare.",
    )
    series = spark[key].tolist()
    try:
        extra = {"chart_data": series, "chart_type": "area"} if len(series) > 1 else {}
        st.metric(**kwargs, border=True, **extra)
    except TypeError:
        with st.container(border=True):
            st.metric(**kwargs)


st.markdown('<div class="section-label">Key metrics</div>', unsafe_allow_html=True)
cols = st.columns(5)
with cols[0]:
    metric_card(
        ":material/payments: " + ("Net revenue" if include_returns else "Revenue"),
        money(cur["revenue"], "£"), "revenue",
    )
with cols[1]:
    metric_card(":material/receipt_long: Sales invoices", f"{cur['invoices']:,}", "invoices")
with cols[2]:
    metric_card(":material/group: Customers", f"{cur['customers']:,}", "customers")
with cols[3]:
    metric_card(":material/shopping_basket: Avg. order value", f"£{cur['aov']:,.0f}", "aov")
with cols[4]:
    metric_card(":material/undo: Return line rate", f"{cur['return_rate']:.1f}%",
                "return_rate", inverse=True)

st.caption(f"{len(view):,} transaction lines in view · sparklines show monthly trend.")
st.write("")


# ── Tabs ─────────────────────────────────────────────────────────────────────

tab_trend, tab_geo, tab_prod, tab_pattern, tab_cust, tab_data = st.tabs([
    ":material/trending_up: Trends",
    ":material/public: Geography",
    ":material/inventory_2: Products",
    ":material/schedule: Patterns",
    ":material/groups: Customers",
    ":material/table_chart: Data",
])


# ── Trends ───────────────────────────────────────────────────────────────────

@st.fragment
def render_trends():
    head_l, head_m, head_r = st.columns([2.2, 1.6, 1.4])
    with head_l:
        section_header(f"{MEASURE_NOUN} over time", "Choose how the trend is drawn and grouped.")
    with head_m:
        trend_style = chart_picker("Chart type", ["Area", "Line", "Bar", "Step"], "trend_style")
    with head_r:
        grain = chart_picker("Grain", ["Daily", "Weekly", "Monthly"], "grain", default=2)

    opt_a, opt_b = st.columns([1, 3])
    show_avg = opt_a.toggle("Moving average", value=True)
    window = opt_b.slider("Moving-average window (periods)", 2, 12, 3, disabled=not show_avg)

    freq = {"Daily": "D", "Weekly": "W", "Monthly": "MS"}[grain]
    series = view.set_index("InvoiceDate")["Value"].resample(freq).sum().reset_index()
    series.columns = ["Period", "Value"]
    series["Avg"] = series["Value"].rolling(window, min_periods=1).mean()
    hover_fmt = {"Daily": "%d %b %Y", "Weekly": "Week of %d %b %Y", "Monthly": "%B %Y"}[grain]

    fig = go.Figure()
    hover = f"<b>%{{x|{hover_fmt}}}</b><br>{MEASURE_NOUN}: {PREFIX}%{{y:,.0f}}<extra></extra>"
    if trend_style == "Bar":
        fig.add_trace(go.Bar(
            x=series["Period"], y=series["Value"], name=MEASURE_NOUN,
            marker=dict(color=palette["accent"], cornerradius=6), hovertemplate=hover,
        ))
    elif trend_style == "Step":
        fig.add_trace(go.Scatter(
            x=series["Period"], y=series["Value"], name=MEASURE_NOUN, mode="lines",
            line=dict(color=palette["accent"], width=3, shape="hv"),
            fill="tozeroy", fillcolor=palette["fill"], hovertemplate=hover,
        ))
    else:
        fig.add_trace(go.Scatter(
            x=series["Period"], y=series["Value"], name=MEASURE_NOUN,
            mode="lines+markers" if grain == "Monthly" else "lines",
            line=dict(color=palette["accent"], width=3, shape="spline", smoothing=0.5),
            marker=dict(size=7, color=palette["accent"], line=dict(color=palette["hover_bg"], width=2)),
            fill="tozeroy" if trend_style == "Area" else None,
            fillcolor=palette["fill"], hovertemplate=hover,
        ))

    if show_avg:
        fig.add_trace(go.Scatter(
            x=series["Period"], y=series["Avg"], name=f"{window}-period average", mode="lines",
            line=dict(color=palette["accent_3"], width=2.5, dash="dash"),
            hovertemplate=f"Average: {PREFIX}%{{y:,.0f}}<extra></extra>",
        ))

    peak = series.loc[series["Value"].idxmax()]
    fig.add_annotation(
        x=peak["Period"], y=peak["Value"], text=f"Peak · {money(peak['Value'])}",
        showarrow=True, arrowhead=2, ax=0, ay=-42,
        bgcolor=palette["card_bg"], bordercolor=palette["accent"],
        font=dict(color=palette["text"], size=12),
    )
    fig = style_chart(fig, height=440)
    fig.update_layout(hovermode="x unified")
    fig.update_xaxes(title="")
    fig.update_yaxes(title="", tickprefix=PREFIX, tickformat=",.0f")
    show(fig)

    unit = {"Daily": "day", "Weekly": "week", "Monthly": "month"}[grain]
    insight(
        f"<b>Best {unit}:</b> {peak['Period']:%d %b %Y} with {money(peak['Value'])}. "
        f"Average per {unit}: {money(series['Value'].mean())}."
    )
    st.caption("December 2011 is partial; the dataset ends on December 9.")

    st.markdown("### Year-over-year by month")
    yoy = view.assign(Year=view["InvoiceDate"].dt.year.astype(str), MonthNum=view["InvoiceDate"].dt.month)
    yoy = yoy.groupby(["Year", "MonthNum"], as_index=False)["Value"].sum()
    yoy["MonthName"] = pd.to_datetime(yoy["MonthNum"], format="%m").dt.strftime("%b")
    yoy_style = chart_picker("YoY chart type", ["Grouped bars", "Lines"], "yoy_style")
    colors = [palette["accent"], palette["accent_2"], palette["accent_3"], palette["negative"]]
    if yoy_style == "Grouped bars":
        yoy_fig = px.bar(yoy, x="MonthName", y="Value", color="Year", barmode="group",
                         color_discrete_sequence=colors)
        yoy_fig.update_traces(marker_cornerradius=5)
    else:
        yoy_fig = px.line(yoy, x="MonthName", y="Value", color="Year", markers=True,
                          color_discrete_sequence=colors)
        yoy_fig.update_traces(line=dict(width=3))
    yoy_fig.update_xaxes(categoryorder="array", categoryarray=[
        "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
    yoy_fig = style_chart(yoy_fig, height=360)
    yoy_fig.update_xaxes(title="")
    yoy_fig.update_yaxes(title="", tickprefix=PREFIX, tickformat=",.0f")
    show(yoy_fig)


# ── Geography ────────────────────────────────────────────────────────────────

@st.fragment
def render_geo():
    head_l, head_r = st.columns([2.4, 2.6])
    with head_l:
        section_header(f"{MEASURE_NOUN} by country", "Switch views to compare markets differently.")
    with head_r:
        geo_style = chart_picker("Geo chart", ["Bar", "Treemap", "Donut", "World map"], "geo_style")

    top_n = st.slider("Countries to show", 5, 25, 10, key="geo_n",
                      disabled=geo_style == "World map")

    country_all = view.groupby("Country", as_index=False)["Value"].sum().sort_values("Value", ascending=False)
    country_top = country_all.head(top_n)

    if geo_style == "Bar":
        data = country_top.sort_values("Value")
        geo_fig = px.bar(data, x="Value", y="Country", orientation="h",
                         color="Value", color_continuous_scale=SEQ_SCALE)
        geo_fig.update_traces(marker_cornerradius=6,
                              hovertemplate=f"<b>%{{y}}</b><br>{MEASURE_NOUN}: {PREFIX}%{{x:,.0f}}<extra></extra>")
        geo_fig.update_coloraxes(showscale=False)
        geo_fig = style_chart(geo_fig, height=max(380, top_n * 30))
        geo_fig.update_xaxes(title="", tickprefix=PREFIX, tickformat=",.0f")
        geo_fig.update_yaxes(title="")
    elif geo_style == "Treemap":
        data = country_top[country_top["Value"] > 0]
        geo_fig = px.treemap(data, path=[px.Constant("All countries"), "Country"], values="Value",
                             color="Value", color_continuous_scale=SEQ_SCALE)
        geo_fig.update_traces(
            marker=dict(cornerradius=8),
            hovertemplate=f"<b>%{{label}}</b><br>{MEASURE_NOUN}: {PREFIX}%{{value:,.0f}}<extra></extra>",
            textinfo="label+percent root",
        )
        geo_fig.update_coloraxes(showscale=False)
        geo_fig = style_chart(geo_fig, height=480)
    elif geo_style == "Donut":
        data = country_all[country_all["Value"] > 0].copy()
        head = data.head(top_n)
        other = data["Value"].iloc[top_n:].sum()
        if other > 0:
            head = pd.concat([head, pd.DataFrame({"Country": ["Other"], "Value": [other]})])
        seq = ["#4f9dff", "#6e7ff3", "#2dd4bf", "#f2b24c", "#f472b6", "#94a3b8", "#38bdf8", "#a78bfa", "#fb923c", "#34d399"] * 3
        geo_fig = px.pie(head, names="Country", values="Value", hole=0.58,
                         color_discrete_sequence=seq)
        geo_fig.update_traces(
            textposition="outside", textinfo="label+percent",
            marker=dict(line=dict(color=palette["hover_bg"], width=2)),
            hovertemplate=f"<b>%{{label}}</b><br>{MEASURE_NOUN}: {PREFIX}%{{value:,.0f}}<extra></extra>",
        )
        geo_fig = style_chart(geo_fig, height=480)
        geo_fig.update_layout(showlegend=False)
        geo_fig.add_annotation(
            text=f"<b>{money(data['Value'].sum())}</b><br>total", showarrow=False,
            font=dict(size=18, color=palette["text"]),
        )
    else:
        data = country_all[country_all["Value"] > 0].copy()
        data["Place"] = data["Country"].replace(COUNTRY_FIX)
        geo_fig = px.choropleth(data, locations="Place", locationmode="country names",
                                color="Value", color_continuous_scale=SEQ_SCALE,
                                hover_name="Country")
        geo_fig.update_geos(
            showframe=False, showcoastlines=False, bgcolor="rgba(0,0,0,0)",
            landcolor=palette["heat_low"], showcountries=True,
            countrycolor=palette["border"], projection_type="natural earth",
        )
        geo_fig = style_chart(geo_fig, height=480)
        geo_fig.update_layout(
            coloraxis_colorbar=dict(title=MEASURE_NOUN, tickprefix=PREFIX, tickformat="~s"),
            margin=dict(l=0, r=0, t=0, b=0),
        )
    show(geo_fig)

    total = country_all["Value"].sum()
    if not country_all.empty and total:
        lead = country_all.iloc[0]
        insight(f"<b>{lead['Country']}</b> leads with {money(lead['Value'])}, "
                f"{lead['Value'] / total * 100:.0f}% of the {MEASURE_NOUN.lower()} in view.")


# ── Products ─────────────────────────────────────────────────────────────────

@st.fragment
def render_products():
    head_l, head_r = st.columns([2.4, 2.6])
    with head_l:
        section_header("Best-performing products", "Ranked by the selected measure for the current filters.")
    with head_r:
        prod_style = chart_picker("Product chart", ["Bar", "Lollipop", "Treemap", "Bubble"], "prod_style")

    prod_n = st.slider("Products to show", 5, 30, 10, key="prod_n")

    products = (
        view.groupby("StockCode", as_index=False)
        .agg(Value=("Value", "sum"), Units=("Quantity", "sum"),
             Revenue=("LineTotal", "sum"), Orders=("Invoice", "nunique"))
        .nlargest(prod_n, "Value")
    )
    names = view.dropna(subset=["Description"]).groupby("StockCode")["Description"].first()
    products["Product"] = (
        products["StockCode"].map(names).fillna(products["StockCode"].astype(str))
        .astype(str).str.title().str.slice(0, 40)
    )
    products["Product"] = products["Product"] + np.where(
        products["Product"].duplicated(keep=False), " (" + products["StockCode"].astype(str) + ")", "")
    ordered = products.sort_values("Value")

    if prod_style == "Bar":
        prod_fig = px.bar(ordered, x="Value", y="Product", orientation="h",
                          color="Value", color_continuous_scale=SEQ_SCALE_2)
        prod_fig.update_traces(marker_cornerradius=6,
                               hovertemplate=f"<b>%{{y}}</b><br>{MEASURE_NOUN}: {PREFIX}%{{x:,.0f}}<extra></extra>")
        prod_fig.update_coloraxes(showscale=False)
        prod_fig = style_chart(prod_fig, height=max(420, prod_n * 32))
        prod_fig.update_xaxes(title="", tickprefix=PREFIX, tickformat=",.0f")
        prod_fig.update_yaxes(title="")
    elif prod_style == "Lollipop":
        prod_fig = go.Figure()
        prod_fig.add_trace(go.Scatter(
            x=ordered["Value"], y=ordered["Product"], mode="markers",
            marker=dict(size=14, color=palette["accent_2"], line=dict(color=palette["hover_bg"], width=2)),
            hovertemplate=f"<b>%{{y}}</b><br>{MEASURE_NOUN}: {PREFIX}%{{x:,.0f}}<extra></extra>",
            showlegend=False,
        ))
        for _, row in ordered.iterrows():
            prod_fig.add_shape(type="line", x0=0, x1=row["Value"], y0=row["Product"], y1=row["Product"],
                               line=dict(color=palette["accent_2"], width=3))
        prod_fig = style_chart(prod_fig, height=max(420, prod_n * 32))
        prod_fig.update_xaxes(title="", tickprefix=PREFIX, tickformat=",.0f", showgrid=True,
                              gridcolor=palette["grid"])
        prod_fig.update_yaxes(title="", showgrid=False)
    elif prod_style == "Treemap":
        data = products[products["Value"] > 0]
        prod_fig = px.treemap(data, path=[px.Constant("Top products"), "Product"], values="Value",
                              color="Value", color_continuous_scale=SEQ_SCALE_2)
        prod_fig.update_traces(
            marker=dict(cornerradius=8), textinfo="label+value",
            hovertemplate=f"<b>%{{label}}</b><br>{MEASURE_NOUN}: {PREFIX}%{{value:,.0f}}<extra></extra>",
        )
        prod_fig.update_coloraxes(showscale=False)
        prod_fig = style_chart(prod_fig, height=500)
    else:
        data = products[(products["Units"] > 0) & (products["Revenue"] > 0)]
        prod_fig = px.scatter(
            data, x="Units", y="Revenue", size="Orders", color="Revenue",
            hover_name="Product", size_max=48, color_continuous_scale=SEQ_SCALE_2,
        )
        prod_fig.update_traces(marker=dict(line=dict(color=palette["hover_bg"], width=1.5), opacity=0.85))
        prod_fig.update_coloraxes(showscale=False)
        prod_fig = style_chart(prod_fig, height=500)
        prod_fig.update_xaxes(title="Units sold", showgrid=True, gridcolor=palette["grid"])
        prod_fig.update_yaxes(title="Revenue (£)", tickprefix="£", tickformat=",.0f")
    show(prod_fig)

    with st.expander("View product table"):
        table = products.sort_values("Value", ascending=False)[
            ["StockCode", "Product", "Units", "Revenue", "Orders"]
        ]
        st.dataframe(
            table, hide_index=True, width="stretch",
            column_config={
                "Revenue": st.column_config.NumberColumn(format="£%.0f"),
                "Units": st.column_config.NumberColumn(format="%d"),
            },
        )


# ── Patterns ─────────────────────────────────────────────────────────────────

@st.fragment
def render_patterns():
    head_l, head_r = st.columns([2.4, 2.6])
    with head_l:
        section_header("When do customers buy?", f"{MEASURE_NOUN} by weekday and hour.")
    with head_r:
        pat_style = chart_picker(
            "Pattern chart", ["Heatmap", "Weekday bars", "Hourly line", "Polar clock"], "pat_style"
        )

    time_data = view.assign(Weekday=view["InvoiceDate"].dt.day_name(), Hour=view["InvoiceDate"].dt.hour)
    heat = time_data.pivot_table(index="Weekday", columns="Hour", values="Value",
                                 aggfunc="sum", fill_value=0
                                 ).reindex(index=WEEKDAYS, columns=range(24), fill_value=0)

    if pat_style == "Heatmap":
        pat_fig = px.imshow(heat, aspect="auto", color_continuous_scale=HEAT_SCALE,
                            labels={"x": "Hour", "y": "Weekday", "color": MEASURE_NOUN})
        pat_fig.update_traces(xgap=3, ygap=3)
        pat_fig = style_chart(pat_fig, height=420)
        pat_fig.update_xaxes(title="Hour of day", tickmode="array", tickvals=list(range(24)),
                             ticktext=[f"{h:02d}" for h in range(24)])
        pat_fig.update_yaxes(title="")
        pat_fig.update_coloraxes(colorbar_title=MEASURE_NOUN, colorbar_tickprefix=PREFIX,
                                 colorbar_tickformat="~s")
    elif pat_style == "Weekday bars":
        wd = heat.sum(axis=1).reset_index()
        wd.columns = ["Weekday", "Value"]
        pat_fig = px.bar(wd, x="Weekday", y="Value", color="Value", color_continuous_scale=SEQ_SCALE)
        pat_fig.update_traces(marker_cornerradius=8,
                              hovertemplate=f"<b>%{{x}}</b><br>{MEASURE_NOUN}: {PREFIX}%{{y:,.0f}}<extra></extra>")
        pat_fig.update_coloraxes(showscale=False)
        pat_fig = style_chart(pat_fig, height=420)
        pat_fig.update_xaxes(title="")
        pat_fig.update_yaxes(title="", tickprefix=PREFIX, tickformat=",.0f")
    elif pat_style == "Hourly line":
        hr = heat.sum(axis=0).reset_index()
        hr.columns = ["Hour", "Value"]
        pat_fig = px.area(hr, x="Hour", y="Value", line_shape="spline")
        pat_fig.update_traces(line=dict(color=palette["accent"], width=3), fillcolor=palette["fill"],
                              hovertemplate=f"<b>%{{x}}:00</b><br>{MEASURE_NOUN}: {PREFIX}%{{y:,.0f}}<extra></extra>")
        pat_fig = style_chart(pat_fig, height=420)
        pat_fig.update_xaxes(title="Hour of day", dtick=1)
        pat_fig.update_yaxes(title="", tickprefix=PREFIX, tickformat=",.0f")
    else:
        hr = heat.sum(axis=0).reset_index()
        hr.columns = ["Hour", "Value"]
        pat_fig = px.bar_polar(hr, r="Value", theta="Hour", color="Value",
                               color_continuous_scale=SEQ_SCALE)
        pat_fig.update_coloraxes(showscale=False)
        pat_fig = style_chart(pat_fig, height=480)
        pat_fig.update_layout(polar=dict(
            bgcolor="rgba(0,0,0,0)",
            angularaxis=dict(direction="clockwise", rotation=90, tickmode="array",
                             tickvals=list(range(0, 24, 3)),
                             ticktext=[f"{h:02d}:00" for h in range(0, 24, 3)],
                             gridcolor=palette["grid"]),
            radialaxis=dict(gridcolor=palette["grid"], showticklabels=False),
        ))
    show(pat_fig)

    best_wd = heat.sum(axis=1).idxmax()
    best_hr = int(heat.sum(axis=0).idxmax())
    insight(f"<b>Busiest day:</b> {best_wd}. <b>Busiest hour:</b> {best_hr:02d}:00 to {best_hr:02d}:59.")


# ── Customers ────────────────────────────────────────────────────────────────

@st.fragment
def render_customers():
    head_l, head_r = st.columns([2.4, 2.6])
    with head_l:
        section_header("Customer insights", "Based on invoices with an identified customer.")
    with head_r:
        cust_style = chart_picker(
            "Customer chart", ["Top customers", "Pareto", "Order values"], "cust_style"
        )

    known = view.dropna(subset=["Customer ID"]).copy()
    if known.empty:
        st.info("No identified customers for these filters.")
        return

    known["Customer"] = "C-" + known["Customer ID"].astype(str).str.replace(r"\.0$", "", regex=True)
    cust = (known.groupby("Customer", as_index=False)
            .agg(Value=("Value", "sum"), Revenue=("LineTotal", "sum"),
                 Orders=("Invoice", "nunique"))
            .sort_values("Value", ascending=False))

    if cust_style == "Top customers":
        n = st.slider("Customers to show", 5, 30, 10, key="cust_n")
        data = cust.head(n).sort_values("Value")
        cust_fig = px.bar(data, x="Value", y="Customer", orientation="h",
                          color="Value", color_continuous_scale=SEQ_SCALE_2)
        cust_fig.update_traces(marker_cornerradius=6,
                               hovertemplate=f"<b>%{{y}}</b><br>{MEASURE_NOUN}: {PREFIX}%{{x:,.0f}}<extra></extra>")
        cust_fig.update_coloraxes(showscale=False)
        cust_fig = style_chart(cust_fig, height=max(400, n * 30))
        cust_fig.update_xaxes(title="", tickprefix=PREFIX, tickformat=",.0f")
        cust_fig.update_yaxes(title="", type="category")
        note = None
    elif cust_style == "Pareto":
        pos = cust[cust["Value"] > 0].reset_index(drop=True)
        pos["Cum"] = pos["Value"].cumsum() / pos["Value"].sum() * 100
        pos["Rank"] = np.arange(1, len(pos) + 1)
        cust_fig = go.Figure()
        cust_fig.add_trace(go.Bar(x=pos["Rank"], y=pos["Value"], name=MEASURE_NOUN,
                                  marker_color=palette["accent"],
                                  hovertemplate=f"Rank %{{x}}<br>{PREFIX}%{{y:,.0f}}<extra></extra>"))
        cust_fig.add_trace(go.Scatter(x=pos["Rank"], y=pos["Cum"], name="Cumulative %", yaxis="y2",
                                      line=dict(color=palette["accent_3"], width=3),
                                      hovertemplate="Top %{x} customers: %{y:.1f}%<extra></extra>"))
        cust_fig = style_chart(cust_fig, height=440)
        cust_fig.update_layout(yaxis2=dict(overlaying="y", side="right", range=[0, 105],
                                           ticksuffix="%", showgrid=False))
        cust_fig.update_xaxes(title="Customers ranked by value")
        cust_fig.update_yaxes(title="", tickprefix=PREFIX, tickformat=",.0f")
        top20 = max(1, int(len(pos) * 0.2))
        share = pos["Value"].head(top20).sum() / pos["Value"].sum() * 100
        note = f"<b>Top 20% of customers</b> ({top20:,}) generate {share:.0f}% of the {MEASURE_NOUN.lower()}."
    else:
        inv = (view.assign(InvoiceStr=view["Invoice"].astype(str))
               .loc[lambda d: ~d["InvoiceStr"].str.upper().str.startswith("C")]
               .groupby("InvoiceStr")["LineTotal"].sum())
        cap = inv.quantile(0.98)
        cust_fig = px.histogram(inv[inv <= cap], nbins=50, color_discrete_sequence=[palette["accent_2"]])
        cust_fig.update_traces(marker_line_width=0,
                               hovertemplate="Order value: £%{x}<br>Invoices: %{y}<extra></extra>")
        cust_fig = style_chart(cust_fig, height=420)
        cust_fig.update_layout(showlegend=False, bargap=0.05)
        cust_fig.update_xaxes(title="Invoice value (£, top 2% hidden)", tickprefix="£")
        cust_fig.update_yaxes(title="Invoices")
        note = f"<b>Median invoice:</b> £{inv.median():,.0f} · <b>Mean:</b> £{inv.mean():,.0f}."

    show(cust_fig)
    if note:
        insight(note)


# ── Data ─────────────────────────────────────────────────────────────────────

@st.fragment
def render_data():
    section_header("Transaction explorer", "Search and export the rows behind the dashboard.")
    search = st.text_input("Search product description", placeholder="e.g. heart, lantern, mug…",
                           icon=":material/search:")
    table = view
    if search:
        table = table[table["Description"].astype(str).str.contains(search, case=False, na=False)]

    preview_columns = ["InvoiceDate", "Invoice", "Country", "StockCode",
                       "Description", "Quantity", "LineTotal"]
    st.caption(f"{len(table):,} rows match · showing the first 500.")
    st.dataframe(
        table[preview_columns].head(500), hide_index=True, width="stretch",
        column_config={
            "InvoiceDate": st.column_config.DatetimeColumn("Date", format="DD MMM YYYY, HH:mm"),
            "LineTotal": st.column_config.NumberColumn("Line total", format="£%.2f"),
        },
    )
    st.download_button(
        "Download filtered data (CSV)",
        data=table[preview_columns].to_csv(index=False).encode("utf-8"),
        file_name="retail_filtered.csv",
        mime="text/csv",
        icon=":material/download:",
    )


with tab_trend:
    render_trends()
with tab_geo:
    render_geo()
with tab_prod:
    render_products()
with tab_pattern:
    render_patterns()
with tab_cust:
    render_customers()
with tab_data:
    render_data()
