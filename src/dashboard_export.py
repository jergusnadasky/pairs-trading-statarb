import json


def export_dashboard_data(
    results,
    prices,
    sig_pairs,
    best,
    t1,
    t2,
    hedge_ratio,
    metrics,
    output_path="results/dashboard_data.json",
):
    """
    Export all dashboard data into a single JSON file.
    """

    def to_list(series):
        out = []

        for x in series:
            try:
                out.append(round(float(x), 4))
            except:
                out.append(None)

        return out

    dates = [str(d.date()) for d in results.index]

    out = {
        "pair": f"{t1}/{t2}",
        "t1": t1,
        "t2": t2,
        "hedge_ratio": round(float(hedge_ratio), 4),
        "p_value": round(float(best["p_value"]), 4),
        "dates": dates,
        "z_score": to_list(results["z_score"]),
        "spread": to_list(results["spread"]),
        "signal": to_list(results["signal"]),
        "strategy_equity": to_list(results["equity_curve"]),
        "bh_equity": to_list(results["bh_equity"]),
        "strategy_return": to_list(results["strategy_return"]),
        "bh_return": to_list(results["bh_return"]),
        "all_pairs": sig_pairs[
            [
                "ticker_1",
                "ticker_2",
                "p_value",
                "hedge_ratio",
            ]
        ].to_dict(orient="records"),
        "strategy_metrics": metrics["strategy"],
        "bh_metrics": metrics["buy_hold"],
    }

    corr = prices.corr().round(3)

    out["tickers"] = prices.columns.tolist()
    out["corr_matrix"] = corr.values.tolist()
    out["corr_labels"] = prices.columns.tolist()

    with open(output_path, "w") as f:
        json.dump(out, f)

    print(f"Dashboard JSON exported -> {output_path}")