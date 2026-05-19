import os
import glob


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
from dashboard_export import export_dashboard_data

TICKERS = [
    "KO",
    "PEP",
    "XOM",
    "CVX",
    "V",
    "MA",
    "JPM",
    "BAC",
]

START = "2018-01-01"
END = "2025-01-01"


prices = fetch_prices(TICKERS, START, END)

pairs = find_cointegrated_pairs(prices)

pairs.to_csv("results/cointegration_results.csv", index=False)

sig_pairs = pairs[
    (pairs["cointegrated"] == True) &
    (pairs["half_life"] > 5) &
    (pairs["half_life"] < 60)
]

if len(sig_pairs) == 0:
    print("No statistically significant pairs found.")
    
    results_dir = os.path.join(".", "results")
    
    # Check if the directory exists to avoid FileNotFoundError
    if os.path.exists(results_dir):
        # Gather all file paths inside the results directory
        files_to_clear = glob.glob(os.path.join(results_dir, "*"))
        
        for file_path in files_to_clear:
            # Check if it's a file rather than a subdirectory
            if os.path.isfile(file_path):
                try:
                    # Opening a file in 'w' mode instantly empties it without deleting it
                    with open(file_path, 'w') as f:
                        pass
                except Exception as e:
                    print(f"Failed to clear {os.path.basename(file_path)}: {e}")
    else:
        print(f"Directory {results_dir} not found; skipping clearance step.")
        
    exit()

best = sig_pairs.iloc[0]

t1 = best["ticker_1"]
t2 = best["ticker_2"]
hedge_ratio = best["hedge_ratio"]
half_life = best["half_life"]

print("\n-----------------------------------")
print("Statistical Arbitrage Pipeline")
print("-----------------------------------")
print(f"Selected pair: {t1}/{t2}")
print(f"Half-life: {half_life}")
print("Generating dashboard analytics...")

spread = compute_spread(prices, t1, t2, hedge_ratio)

zscore = compute_zscore(spread, half_life)

signals = generate_signals(zscore)

results = compute_returns(
    prices,
    t1,
    t2,
    hedge_ratio,
    signals,
)

results["z_score"] = zscore
results["spread"] = spread

metrics = {
    "strategy": performance_metrics(
        results["strategy_return"]
    ),
    "buy_hold": performance_metrics(
        results["bh_return"]
    ),
}

trade_log = generate_trade_log(
    results["signal"],
    results["equity_curve"],
)

trade_log.to_csv("results/trade_log.csv", index=False)

results.to_csv("results/equity_curve.csv")

export_dashboard_data(
    results=results,
    prices=prices,
    sig_pairs=sig_pairs,
    best=best,
    t1=t1,
    t2=t2,
    hedge_ratio=hedge_ratio,
    metrics=metrics,
)

print("Dashboard export complete.")
print("Run: streamlit run app/dashboard.py")
