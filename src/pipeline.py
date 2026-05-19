import os
import glob
import pandas as pd

from dashboard_export import export_dashboard_data

from data_loader import fetch_prices

from cointegration import (
    find_cointegrated_pairs,
    compute_spread,
    compute_zscore,
)

from signals import generate_signals

from backtest import (
    compute_returns,
    performance_metrics,
    generate_trade_log,
)

RESULTS_DIR = "results"

os.makedirs(RESULTS_DIR, exist_ok=True)


def clear_results_directory():

    files = glob.glob(
        os.path.join(RESULTS_DIR, "*")
    )

    for file_path in files:

        try:

            if os.path.isfile(file_path):
                os.remove(file_path)

        except Exception as e:

            print(f"Failed removing {file_path}: {e}")


def run_pipeline(
    tickers,
    train_start,
    train_end,
    test_start,
    test_end,
    zscore_window,
    entry_z,
    stop_z,
    pvalue_thresh,
    transaction_cost,
):

    # ─────────────────────────────────────────────
    # FETCH DATA
    # ─────────────────────────────────────────────

    prices = fetch_prices(
        tickers,
        str(train_start),
        str(test_end),
    )

    # Remove fully empty columns
    # Track original tickers
    requested_tickers = tickers.copy()

    # Remove fully empty columns
    prices = prices.dropna(
        axis=1,
        how="all",
    )

    # Detect invalid / delisted tickers
    valid_tickers = prices.columns.tolist()

    invalid_tickers = [
        t for t in requested_tickers
        if t not in valid_tickers
    ]

    # Require at least 2 valid tickers
    if len(valid_tickers) < 2:

        clear_results_directory()

        return {
            "success": False,
            "error_type": "invalid_tickers",
            "invalid_tickers": invalid_tickers,
            "pairs": pd.DataFrame(),
            "prices": prices,
            "sig_pairs": pd.DataFrame(),
        }

    # ─────────────────────────────────────────────
    # TRAINING WINDOW
    # ─────────────────────────────────────────────

    train_prices = prices[
        prices.index < str(test_start)
    ]

    if train_prices.empty:

        clear_results_directory()
        
        return {
            "success": False,
            "pairs": pd.DataFrame(),
            "prices": prices,
            "sig_pairs": pd.DataFrame(),
        }

    # ─────────────────────────────────────────────
    # COINTEGRATION SCAN
    # ─────────────────────────────────────────────

    pairs = find_cointegrated_pairs(
        train_prices,
        pvalue_threshold=pvalue_thresh,
    )

    # Completely failed scan
    if pairs.empty:

        clear_results_directory()
        
        return {
            "success": False,
            "pairs": pairs,
            "prices": prices,
            "sig_pairs": pd.DataFrame(),
        }   

    # Significant pairs only
    sig_pairs = pairs[
        pairs["cointegrated"] == True
    ]

    # No valid pairs
    # No valid pairs
    if sig_pairs.empty:

        # Save scan results anyway
        pairs.to_csv(
            f"{RESULTS_DIR}/cointegration_results.csv",
            index=False,
        )

        # Remove strategy artifacts only
        strategy_files = [
            "equity_curve.csv",
            "trade_log.csv",
            "dashboard_data.json",
        ]

        for file_name in strategy_files:

            file_path = os.path.join(
                RESULTS_DIR,
                file_name,
            )

            if os.path.exists(file_path):
                os.remove(file_path)

        return {
            "success": False,
            "pairs": pairs,
            "prices": prices,
            "sig_pairs": sig_pairs,
        }

    # ─────────────────────────────────────────────
    # BEST PAIR
    # ─────────────────────────────────────────────

    best = sig_pairs.iloc[0]

    t1 = best["ticker_1"]
    t2 = best["ticker_2"]

    hedge_ratio = best["hedge_ratio"]

    # ─────────────────────────────────────────────
    # SPREAD + ZSCORE
    # ─────────────────────────────────────────────

    spread = compute_spread(
        prices,
        t1,
        t2,
        hedge_ratio,
    )

    zscore = compute_zscore(
        spread,
        window=zscore_window,
    )

    # ─────────────────────────────────────────────
    # SIGNALS
    # ─────────────────────────────────────────────

    signals = generate_signals(
        zscore,
        entry_z=entry_z,
        stop_z=stop_z,
    )

    test_signals = signals[
        signals.index >= str(test_start)
    ]

    # ─────────────────────────────────────────────
    # BACKTEST
    # ─────────────────────────────────────────────

    results = compute_returns(
        prices,
        t1,
        t2,
        hedge_ratio,
        test_signals,
        transaction_cost,
    )

    # Empty backtest protection
    if results.empty:

        clear_results_directory()

        return {
            "success": False,
            "pairs": pairs,
            "prices": prices,
            "sig_pairs": pd.DataFrame(),
        }   

    # ─────────────────────────────────────────────
    # ADD SERIES
    # ─────────────────────────────────────────────

    results["spread"] = spread.reindex(
        results.index
    )

    results["z_score"] = zscore.reindex(
        results.index
    )

    # ─────────────────────────────────────────────
    # EQUITY CURVES
    # ─────────────────────────────────────────────

    results["strategy_equity"] = (
        1 + results["strategy_return"]
    ).cumprod()

    results["bh_equity"] = (
        1 + results["bh_return"]
    ).cumprod()

    # ─────────────────────────────────────────────
    # METRICS
    # ─────────────────────────────────────────────

    metrics = {

        "strategy": performance_metrics(
            results["strategy_return"]
        ),

        "buy_hold": performance_metrics(
            results["bh_return"]
        ),
    }

    # ─────────────────────────────────────────────
    # TRADE LOG
    # ─────────────────────────────────────────────

    trade_log = generate_trade_log(
        results["signal"],
        results["strategy_equity"],
    )

    # ─────────────────────────────────────────────
    # SAVE FILES
    # ─────────────────────────────────────────────

    pairs.to_csv(
        f"{RESULTS_DIR}/cointegration_results.csv",
        index=False,
    )

    trade_log.to_csv(
        f"{RESULTS_DIR}/trade_log.csv",
        index=False,
    )

    results.to_csv(
        f"{RESULTS_DIR}/equity_curve.csv"
    )

    export_dashboard_data(
        results=results,
        prices=prices,
        sig_pairs=sig_pairs,
        best=best,
        t1=t1,
        t2=t2,
        hedge_ratio=hedge_ratio,
        metrics=metrics,
        output_path=f"{RESULTS_DIR}/dashboard_data.json",
    )

    # ─────────────────────────────────────────────
    # RETURN PACKAGE
    # ─────────────────────────────────────────────

    return {

    "success": True,

    "results": results,

    "pairs": pairs,

    "sig_pairs": sig_pairs,

    "best": best,

    "metrics": metrics,

    "trade_log": trade_log,

    "prices": prices,

    "t1": t1,

    "t2": t2,

    "hedge_ratio": hedge_ratio,
    }