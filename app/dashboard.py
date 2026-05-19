"""
app/dashboard.py — Pairs Trading StatArb · Streamlit App
Live interactive cointegration scanner + backtest dashboard
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.abspath(os.path.join(current_dir, "..", "src"))

if src_path not in sys.path:
    sys.path.insert(0, src_path)

from pipeline import run_pipeline

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Pairs Trading StatArb",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background-color: #0e1117; }
    .main-title {
        font-size: 2.2rem; font-weight: 700; letter-spacing: -0.03em;
        background: linear-gradient(135deg, #378ADD 0%, #1D9E75 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    .subtitle { color: #6b7280; font-size: 0.95rem; margin-top: 0.2rem; margin-bottom: 1.5rem; }
    .metric-card {
        background: #161b22; border: 1px solid #21262d;
        border-radius: 10px; padding: 1rem 1.25rem; text-align: center;
    }
    .metric-label { color: #6b7280; font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.08em; }
    .metric-val { font-size: 1.6rem; font-weight: 700; margin: 0.2rem 0 0; }
    .metric-sub { font-size: 0.78rem; color: #6b7280; margin-top: 0.1rem; }
    .green { color: #1D9E75; } .red { color: #E24B4A; } .blue { color: #378ADD; } .amber { color: #EF9F27; }
    .pair-badge {
        display: inline-block; background: #1a2744; color: #378ADD;
        border: 1px solid #2a3f6f; border-radius: 6px;
        padding: 0.25rem 0.75rem; font-weight: 600; font-size: 1rem;
    }
    .section-header { color: #e6edf3; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.1em; font-weight: 600; margin-bottom: 0.5rem; }
    .stAlert { border-radius: 8px; }
    div[data-testid="stSidebarContent"] { background: #0d1117; }
    div[data-testid="metric-container"] { background: #161b22; border-radius: 10px; padding: 0.75rem 1rem; border: 1px solid #21262d; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar: inputs ────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    st.markdown("---")

    st.markdown("**Universe**")
    default_tickers = "KO, PEP, XOM, CVX, JPM, BAC, GLD, SLV, V, MA"
    ticker_input = st.text_area(
        "Tickers (comma-separated)",
        value=default_tickers,
        height=100,
        help="Enter any valid stock/ETF tickers. Needs at least 2.",
    )

    st.markdown("**Date range**")
    col1, col2 = st.columns(2)
    with col1:
        train_start = st.date_input("Train start", value=pd.to_datetime("2018-01-01"))
    with col2:
        train_end = st.date_input("Train end", value=pd.to_datetime("2021-12-31"))

    col3, col4 = st.columns(2)
    with col3:
        test_start = st.date_input("Test start", value=pd.to_datetime("2022-01-01"))
    with col4:
        test_end = st.date_input("Test end", value=pd.to_datetime("2024-01-01"))

    st.markdown("**Strategy parameters**")
    zscore_window = st.slider("Z-score window (days)", 20, 120, 60, 5)
    entry_z = st.slider("Entry threshold (σ)", 1.0, 3.5, 2.0, 0.25)
    stop_z = st.slider("Stop-loss threshold (σ)", entry_z + 0.5, 5.0, 3.5, 0.25)
    pvalue_thresh = st.slider("Cointegration p-value cutoff", 0.01, 0.10, 0.05, 0.01)
    tc = st.slider("Transaction cost (bps per leg)", 0, 30, 10, 1) / 10000

    st.markdown("---")
    run_btn = st.button("🚀  Run analysis", use_container_width=True, type="primary")

# ── Landing state ──────────────────────────────────────────────────────────────
if not run_btn and "results" not in st.session_state:
    st.markdown('<p class="main-title">Pairs Trading · StatArb</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Statistical mean-reversion · Engle-Granger cointegration · Out-of-sample backtest</p>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Step 1</div>
            <div class="metric-val blue">Scan</div>
            <div class="metric-sub">Add tickers, set date range in the sidebar</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Step 2</div>
            <div class="metric-val blue">Detect</div>
            <div class="metric-sub">Engle-Granger tests all pairs for cointegration</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Step 3</div>
            <div class="metric-val blue">Backtest</div>
            <div class="metric-sub">Long/short signals on z-score, evaluated out-of-sample</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    **How it works**

    This tool scans a universe of tickers for *cointegrated pairs* — stocks whose prices are statistically
    linked over time. When the spread between them deviates beyond a z-score threshold, it signals a trade:
    go long the cheaper leg, short the expensive one, and profit when they converge.

    - **Train / test split** — cointegration is estimated on the training window only, signals fired on the held-out test set
    - **Rolling z-score** — spread normalised by its rolling mean and std to generate entry/exit signals
    - **Transaction costs** — configurable per-leg cost applied on every position change
    - **Benchmark** — strategy equity compared against buy-and-hold of the first leg
    """)

    st.info("👈  Configure your universe and parameters in the sidebar, then hit **Run analysis**.")
    st.stop()

# ── Run pipeline ──────────────────────────────────────────────
if run_btn or "results" in st.session_state:

    if run_btn:

        tickers = [
            t.strip().upper()
            for t in ticker_input.split(",")
            if t.strip()
        ]

        if len(tickers) < 2:
            st.error("Please enter at least 2 tickers.")
            st.stop()

        with st.spinner("Running statistical arbitrage pipeline..."):

            output = run_pipeline(
                tickers=tickers,
                train_start=train_start,
                train_end=train_end,
                test_start=test_start,
                test_end=test_end,
                zscore_window=zscore_window,
                entry_z=entry_z,
                stop_z=stop_z,
                pvalue_thresh=pvalue_thresh,
                transaction_cost=tc,
            )

        if not output["success"]:

            # Invalid / delisted tickers
            if output.get("error_type") == "invalid_tickers":

                invalids = output.get(
                    "invalid_tickers",
                    [],
                )

                st.error(
                    "One or more tickers could not be "
                    "downloaded from Yahoo Finance."
                )

                if invalids:

                    st.markdown(
                        f"### Invalid / Delisted Tickers\n"
                        f"{', '.join(invalids)}"
                    )

                st.info(
                    "Check ticker spelling or try "
                    "different symbols."
                )

            # No statistically significant pairs
            else:

                st.warning(
                    f"No cointegrated pairs found at "
                    f"p < {pvalue_thresh}. "
                    "Try relaxing the threshold or "
                    "adding more tickers."
                )

            # Optional: still show tested pairs
            pairs_df = output["pairs"]

            if not pairs_df.empty:

                st.markdown("### Tested Pairs")

                st.dataframe(
                    pairs_df[
                        ["ticker_1", "ticker_2", "p_value"]
                    ],
                    use_container_width=True,
                    hide_index=True,
                )

            st.stop()

        # ── Save valid results to session ───────────────────────────

        st.session_state["results"] = output["results"]
        st.session_state["pairs_df"] = output["pairs"]
        st.session_state["sig_pairs"] = output["sig_pairs"]
        st.session_state["best"] = output["best"]
        st.session_state["metrics"] = output["metrics"]
        st.session_state["trade_log"] = output["trade_log"]
        st.session_state["prices"] = output["prices"]
        st.session_state["t1"] = output["t1"]
        st.session_state["t2"] = output["t2"]
        st.session_state["hedge_ratio"] = output["hedge_ratio"]
        st.session_state["tickers"] = tickers

    # ── Pull from session ──────────────────────────────────────────────────────
    results = st.session_state["results"]
    pairs_df = st.session_state["pairs_df"]
    sig_pairs = st.session_state["sig_pairs"]
    best = st.session_state["best"]
    t1 = st.session_state["t1"]
    t2 = st.session_state["t2"]
    hedge_ratio = st.session_state["hedge_ratio"]
    metrics = st.session_state["metrics"]

    sm = metrics["strategy"]
    bm = metrics["buy_hold"]
    prices = st.session_state["prices"]
    tickers = st.session_state["tickers"]
    trade_log = st.session_state["trade_log"]

    # ── Header ────────────────────────────────────────────────────────────────
    st.markdown('<p class="main-title">Pairs Trading · StatArb</p>', unsafe_allow_html=True)
    hcol1, hcol2 = st.columns([3, 1])
    with hcol1:
        st.markdown(f'<p class="subtitle">Best pair: <span class="pair-badge">{t1} / {t2}</span>  ·  p-value: <b>{best["p_value"]:.4f}</b>  ·  hedge ratio: <b>{hedge_ratio:.4f}</b>  ·  {len(sig_pairs)} cointegrated pair(s) found</p>', unsafe_allow_html=True)
    with hcol2:
        st.markdown(f'<p style="text-align:right;color:#6b7280;font-size:0.82rem;padding-top:0.5rem;">Train: {train_start} → {train_end}<br>Test: {test_start} → {test_end}</p>', unsafe_allow_html=True)

    # ── Metrics ───────────────────────────────────────────────────────────────

    row1 = st.columns(4)
    row2 = st.columns(4)

    def color(v, up=True):

        if v > 0:
            return "green" if up else "red"

        if v < 0:
            return "red" if up else "green"

        return "blue"


    metric_cards = [

        # Row 1
        (
            row1[0],
            "CAGR",
            sm["cagr"],
            bm["cagr"],
            "%",
            True,
        ),

        (
            row1[1],
            "Ann. return",
            sm["ann_return"],
            bm["ann_return"],
            "%",
            True,
        ),

        (
            row1[2],
            "Ann. vol",
            sm["ann_vol"],
            bm["ann_vol"],
            "%",
            False,
        ),

        (
            row1[3],
            "Sharpe",
            sm["sharpe"],
            bm["sharpe"],
            "",
            True,
        ),

        # Row 2
        (
            row2[0],
            "Sortino",
            sm["sortino"],
            bm["sortino"],
            "",
            True,
        ),

        (
            row2[1],
            "Calmar",
            sm["calmar"],
            bm["calmar"],
            "",
            True,
        ),

        (
            row2[2],
            "Max drawdown",
            sm["max_drawdown"],
            bm["max_drawdown"],
            "%",
            True,
        ),

        (
            row2[3],
            "Win rate",
            sm["win_rate"],
            bm["win_rate"],
            "%",
            True,
        ),
    ]

    for col, label, sv, bv, unit, up in metric_cards:

        better = sv > bv if up else sv < bv

        arrow = "▲" if better else "▼"

        c = color(sv, up)

        col.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-val {c}">
                {sv:.2f}{unit}
            </div>
            <div class="metric-sub">
                {arrow} vs B&H {bv:.2f}{unit}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Equity curve ──────────────────────────────────────────────────────────
    st.markdown('<p class="section-header">Equity curve — out-of-sample</p>', unsafe_allow_html=True)

    fig_eq = go.Figure()
    fig_eq.add_trace(go.Scatter(
        x=results.index, y=(results["strategy_equity"] - 1) * 100,
        name=f"{t1}/{t2} strategy", line=dict(color="#378ADD", width=2),
        fill="tozeroy", fillcolor="rgba(55,138,221,0.07)"
    ))
    fig_eq.add_trace(go.Scatter(
        x=results.index, y=(results["bh_equity"] - 1) * 100,
        name=f"{t1} buy & hold", line=dict(color="#6b7280", width=1.5, dash="dash")
    ))
    fig_eq.add_hline(y=0, line_color="rgba(255,255,255,0.15)", line_width=1)
    fig_eq.update_layout(
        height=280, paper_bgcolor="#0e1117", plot_bgcolor="#0e1117",
        font=dict(color="#e6edf3", size=12), margin=dict(l=0, r=0, t=10, b=0),
        legend=dict(orientation="h", y=1.08, bgcolor="rgba(0,0,0,0)"),
        yaxis=dict(ticksuffix="%", gridcolor="#21262d", zeroline=False),
        xaxis=dict(gridcolor="#21262d"),
        hovermode="x unified"
    )
    st.plotly_chart(fig_eq, use_container_width=True)

    # ── Z-score + signals ─────────────────────────────────────────────────────
    st.markdown('<p class="section-header">Z-score & trading signals</p>', unsafe_allow_html=True)

    fig_z = go.Figure()
    long_mask = results["signal"] == 1
    short_mask = results["signal"] == -1

    fig_z.add_trace(go.Bar(
        x=results.index[long_mask], y=results.loc[long_mask, "z_score"],
        name="Long spread", marker_color="rgba(29,158,117,0.35)", showlegend=True
    ))
    fig_z.add_trace(go.Bar(
        x=results.index[short_mask], y=results.loc[short_mask, "z_score"],
        name="Short spread", marker_color="rgba(226,75,74,0.35)", showlegend=True
    ))
    fig_z.add_trace(go.Scatter(
        x=results.index, y=results["z_score"],
        name="Z-score", line=dict(color="#378ADD", width=1.8), mode="lines"
    ))
    for lvl, label in [(entry_z, f"+{entry_z}σ"), (-entry_z, f"-{entry_z}σ"), (0, "")]:
        fig_z.add_hline(y=lvl, line_color="#EF9F27" if lvl != 0 else "rgba(255,255,255,0.15)",
                        line_dash="dash" if lvl != 0 else "solid", line_width=1,
                        annotation_text=label, annotation_position="right",
                        annotation_font=dict(color="#EF9F27", size=11))

    fig_z.update_layout(
        height=240, paper_bgcolor="#0e1117", plot_bgcolor="#0e1117",
        font=dict(color="#e6edf3", size=12), margin=dict(l=0, r=0, t=10, b=0),
        legend=dict(orientation="h", y=1.1, bgcolor="rgba(0,0,0,0)"),
        yaxis=dict(ticksuffix="σ", gridcolor="#21262d", zeroline=False),
        xaxis=dict(gridcolor="#21262d"), barmode="overlay", hovermode="x unified"
    )
    st.plotly_chart(fig_z, use_container_width=True)

    # ── Bottom row: pairs table + heatmap ─────────────────────────────────────
    left, right = st.columns([1, 1.4])

    with left:
        st.markdown('<p class="section-header">Cointegrated pairs</p>', unsafe_allow_html=True)
        display_df = pairs_df[pairs_df["cointegrated"]][["ticker_1", "ticker_2", "p_value", "hedge_ratio"]].copy()
        display_df.columns = ["Leg 1", "Leg 2", "p-value", "Hedge ratio"]
        display_df["p-value"] = display_df["p-value"].map("{:.4f}".format)
        display_df["Hedge ratio"] = display_df["Hedge ratio"].map("{:.4f}".format)
        st.dataframe(display_df, hide_index=True, use_container_width=True,
                     column_config={"Leg 1": st.column_config.TextColumn(width="small"),
                                    "Leg 2": st.column_config.TextColumn(width="small")})

        st.markdown('<p class="section-header" style="margin-top:1rem">All pairs tested</p>', unsafe_allow_html=True)
        all_df = pairs_df[["ticker_1", "ticker_2", "p_value", "cointegrated"]].copy()
        all_df.columns = ["Leg 1", "Leg 2", "p-value", "Cointegrated"]
        all_df["p-value"] = all_df["p-value"].map("{:.4f}".format)
        st.dataframe(all_df, hide_index=True, use_container_width=True, height=200)

    with right:
        st.markdown('<p class="section-header">Correlation heatmap</p>', unsafe_allow_html=True)
        common_tickers = [t for t in tickers if t in prices.columns]
        if len(common_tickers) >= 2:
            corr = prices[common_tickers].corr()
            fig_heat = px.imshow(
                corr,
                text_auto=".2f",
                aspect="auto",
                color_continuous_scale="RdBu",
                zmin=0,
                zmax=1,
            )

            

            fig_heat.update_layout(
                height=340,
                paper_bgcolor="#0e1117",
                plot_bgcolor="#0e1117",
                font=dict(color="#e6edf3", size=11),
                margin=dict(l=0, r=0, t=0, b=0),
                coloraxis_showscale=False
            )

            fig_heat.update_traces(
                textfont_size=10
            )

            st.plotly_chart(
                fig_heat,
                use_container_width=True
            )

    # ── Spread chart ──────────────────────────────────────────────────────────
    with st.expander("📊  Raw spread over time"):
        fig_sp = go.Figure()
        full_spread = results["spread"]
        spread_mean = full_spread.mean()
        fig_sp.add_trace(go.Scatter(
            x=full_spread.index, y=full_spread,
            line=dict(color="#1D9E75", width=1.5), name="Spread"
        ))
        fig_sp.add_hline(y=spread_mean, line_color="#EF9F27", line_dash="dash", line_width=1,
                          annotation_text="mean", annotation_font=dict(color="#EF9F27"))
        fig_sp.update_layout(
            height=220, paper_bgcolor="#0e1117", plot_bgcolor="#0e1117",
            font=dict(color="#e6edf3", size=12), margin=dict(l=0, r=0, t=10, b=0),
            yaxis=dict(gridcolor="#21262d"), xaxis=dict(gridcolor="#21262d")
        )
        st.plotly_chart(fig_sp, use_container_width=True)

    # ── Trade Log Panel ───────────────────────────────────────────────────────
    st.markdown('<p class="section-header" style="margin-top:1.5rem">Trade Execution Log</p>', unsafe_allow_html=True)
    if not trade_log.empty:
        st.dataframe(trade_log, use_container_width=True, hide_index=True)
    else:
        st.info("No active historical trade entries found in results/trade_log.csv.")

    # ── Footer ────────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown(
        "<p style='text-align:center;color:#6b7280;font-size:0.8rem;'>"
        "Built with Python · statsmodels · Plotly · Streamlit &nbsp;|&nbsp; "
        "<a href='https://github.com/jergusnadasky/pairs-trading-statarb' style='color:#378ADD;'>GitHub →</a>"
        "</p>",
        unsafe_allow_html=True
    )