import streamlit as st
import pandas as pd
import numpy as np
import json
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path

st.set_page_config(
    page_title="Statistical Arbitrage Dashboard",
    layout="wide",
)



# ---------------------------------------------------
# LOAD DATA WITH ERROR HANDLING
# ---------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "results" / "dashboard_data.json"
TRADE_LOG_PATH = BASE_DIR / "results" / "trade_log.csv"

try:
    # Attempt to read the JSON file
    with open(DATA_PATH, "r") as f:
        data = json.load(f)
        
    # Attempt to read the CSV file
    trade_log = pd.read_csv(TRADE_LOG_PATH)

    # Reconstruct DataFrame if files exist and are populated
    results = pd.DataFrame({
        "date": pd.to_datetime(data["dates"]),
        "strategy_equity": data["strategy_equity"],
        "bh_equity": data["bh_equity"],
        "z_score": data["z_score"],
        "signal": data["signal"],
    })
    results.set_index("date", inplace=True)

except (json.JSONDecodeError, FileNotFoundError, pd.errors.EmptyDataError, KeyError):
    # If JSON is blank/missing or trade_log is empty, catch the error and show a clean UI alert
    st.title("Statistical Arbitrage Dashboard")
    st.warning("⚠️ No cointegrated pairs found in the latest backtest execution.")
    st.info("Run your backtest script (`main.py`) with alternative datasets or parameters to generate signals.")
    st.stop()  # Safely halts further dashboard execution so the app doesn't crash on empty variables

# ---------------------------------------------------
# SIDEBAR
# ---------------------------------------------------

st.sidebar.title("Strategy Overview")

st.sidebar.markdown(f"""
### Pair
`{data['pair']}`

### Strategy Type
Statistical Arbitrage

### Signal Model
Mean Reversion

### Cointegration Test
Engle-Granger

### Universe
{len(data['tickers'])} Assets

### Date Range
{results.index.min().date()}
to
{results.index.max().date()}
""")


# ---------------------------------------------------
# HEADER
# ---------------------------------------------------

st.title("Statistical Arbitrage Dashboard")

st.markdown(f"""
### Pair: `{data['pair']}`

Out-of-sample backtest using Engle-Granger cointegration and
mean-reversion z-score trading signals.
""")

# ---------------------------------------------------
# METRICS
# ---------------------------------------------------

sm = data["strategy_metrics"]
bm = data["bh_metrics"]

trade_count = len(trade_log)

avg_trade_pnl = 0
if trade_count > 0:
    avg_trade_pnl = trade_log["pnl"].mean()

st.markdown("### Trade Statistics")

t1, t2 = st.columns(2)

t1.metric(
    "Total Trades",
    trade_count,
)

t2.metric(
    "Average Trade PnL",
    f"{avg_trade_pnl:.4f}",
)

st.subheader("Performance Metrics")

top1, top2, top3, top4 = st.columns(4)

top1.metric(
    "Selected Pair",
    data["pair"],
)

top2.metric(
    "Hedge Ratio",
    f"{data['hedge_ratio']:.4f}",
)

top3.metric(
    "Cointegration p-value",
    f"{data['p_value']:.4f}",
)

top4.metric(
    "Trading Days",
    len(results),
)

st.markdown("### Strategy vs Buy & Hold")

metric_cols = st.columns(7)

metrics_display = [
    ("CAGR", "cagr", "%"),
    ("Annual Return", "ann_return", "%"),
    ("Volatility", "ann_vol", "%"),
    ("Sharpe", "sharpe", ""),
    ("Sortino", "sortino", ""),
    ("Max Drawdown", "max_drawdown", "%"),
    ("Calmar", "calmar", ""),
]

for col, (label, key, suffix) in zip(metric_cols, metrics_display):

    strat_val = sm[key]
    bh_val = bm[key]

    delta = strat_val - bh_val

    col.metric(
        label=label,
        value=f"{strat_val:.2f}{suffix}",
        delta=f"{delta:.2f}{suffix} vs B&H"
    )


st.divider()

# ---------------------------------------------------
# EQUITY CURVE
# ---------------------------------------------------

fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=results.index,
        y=results["strategy_equity"],
        mode="lines",
        name="Pairs Strategy",
        line=dict(width=3),
    )
)

fig.add_trace(
    go.Scatter(
        x=results.index,
        y=results["bh_equity"],
        mode="lines",
        name=f"{data['t1']} Buy & Hold",
        line=dict(dash="dash"),
    )
)

fig.update_layout(
    title="Strategy Equity Curve vs Buy & Hold Benchmark",    
    height=450,
    xaxis_title="Date",
    yaxis_title="Portfolio Value",
    template="plotly_dark",
)

st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------
# Z SCORE + SIGNALS
# ---------------------------------------------------

zfig = go.Figure()

zfig.add_trace(
    go.Scatter(
        x=results.index,
        y=results["z_score"],
        mode="lines",
        name="Z-Score",
    )
)

zfig.add_hline(y=2, line_dash="dash")
zfig.add_hline(y=-2, line_dash="dash")
zfig.add_hline(y=0)

long_entries = results[results["signal"] == 1]
short_entries = results[results["signal"] == -1]

zfig.add_trace(
    go.Scatter(
        x=long_entries.index,
        y=long_entries["z_score"],
        mode="markers",
        marker=dict(size=8),
        name="Long Signal",
    )
)

zfig.add_trace(
    go.Scatter(
        x=short_entries.index,
        y=short_entries["z_score"],
        mode="markers",
        marker=dict(size=8),
        name="Short Signal",
    )
)

zfig.update_layout(
    title="Mean-Reversion Z-Score Signals",
    height=400,
    template="plotly_dark",
)

st.plotly_chart(zfig, use_container_width=True)

# ---------------------------------------------------
# LOWER PANELS
# ---------------------------------------------------

left, right = st.columns(2)

# ---------------------------------------------------
# PAIRS TABLE
# ---------------------------------------------------

with left:
    st.subheader("Cointegrated Pairs")

    pairs_df = pd.DataFrame(data["all_pairs"])

    st.dataframe(
        pairs_df,
        use_container_width=True,
        hide_index=True,
    )

# ---------------------------------------------------
# CORRELATION HEATMAP
# ---------------------------------------------------

with right:
    st.subheader("Correlation Heatmap")

    corr = np.array(data["corr_matrix"])

    heatmap = px.imshow(
        corr,
        x=data["tickers"],
        y=data["tickers"],
        text_auto=True,
        aspect="auto",
        color_continuous_scale="RdBu",
    )

    heatmap.update_layout(
        height=450,
        template="plotly_dark",
    )

    st.plotly_chart(heatmap, use_container_width=True)

# ---------------------------------------------------
# TRADE LOG
# ---------------------------------------------------

st.subheader("Trade Log")

st.dataframe(
    trade_log,
    use_container_width=True,
)