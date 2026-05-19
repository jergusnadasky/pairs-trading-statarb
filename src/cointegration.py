import numpy as np
import pandas as pd
import statsmodels.api as sm

from itertools import combinations
from statsmodels.tsa.stattools import coint


def estimate_half_life(spread):

    spread_lag = spread.shift(1).dropna()
    spread_ret = spread.diff().dropna()

    spread_lag = spread_lag.loc[
        spread_ret.index
    ]

    # Prevent crashes on bad data
    if len(spread_lag) < 2:
        return 999

    try:

        beta = np.polyfit(
            spread_lag,
            spread_ret,
            1,
        )[0]

        # Prevent divide-by-zero
        if beta == 0:
            return 999

        half_life = -np.log(2) / beta

        # Reject nonsensical values
        if np.isnan(half_life) or np.isinf(half_life):
            return 999

        return max(
            5,
            int(round(abs(half_life))),
        )

    except Exception:

        return 999


def find_cointegrated_pairs(
    prices,
    pvalue_threshold=0.05,
):

    tickers = prices.columns.tolist()

    results = []

    for t1, t2 in combinations(tickers, 2):

        try:

            s1 = prices[t1].dropna()
            s2 = prices[t2].dropna()

            common = s1.index.intersection(
                s2.index
            )

            s1 = s1.loc[common]
            s2 = s2.loc[common]

            # Need enough overlapping data
            if len(common) < 100:
                continue

            # Skip constant series
            if s1.nunique() < 2 or s2.nunique() < 2:
                continue

            # Cointegration test
            score, pvalue, _ = coint(
                s1,
                s2,
            )

            # OLS hedge ratio
            model = sm.OLS(
                s1,
                sm.add_constant(s2),
            ).fit()

            hedge_ratio = model.params.iloc[1]

            r_squared = model.rsquared

            spread = (
                s1
                - hedge_ratio * s2
            )

            half_life = estimate_half_life(
                spread
            )

            results.append(
                {
                    "ticker_1": t1,
                    "ticker_2": t2,
                    "p_value": pvalue,
                    "score": score,
                    "hedge_ratio": hedge_ratio,
                    "r_squared": r_squared,
                    "half_life": half_life,
                    "cointegrated": (
                        pvalue < pvalue_threshold
                    ),
                }
            )

        except Exception as e:

            print(
                f"Skipping pair {t1}/{t2}: {e}"
            )

            continue

    # ─────────────────────────────────────────────
    # SAFE EMPTY RETURN
    # ─────────────────────────────────────────────

    if len(results) == 0:

        return pd.DataFrame(
            columns=[
                "ticker_1",
                "ticker_2",
                "p_value",
                "score",
                "hedge_ratio",
                "r_squared",
                "half_life",
                "cointegrated",
            ]
        )

    return (
        pd.DataFrame(results)
        .sort_values("p_value")
        .reset_index(drop=True)
    )


def compute_spread(
    prices,
    t1,
    t2,
    hedge_ratio,
):

    return (
        prices[t1]
        - hedge_ratio * prices[t2]
    )


def compute_zscore(
    spread,
    window,
):

    rolling_mean = (
        spread
        .rolling(window)
        .mean()
    )

    rolling_std = (
        spread
        .rolling(window)
        .std()
    )

    zscore = (
        spread - rolling_mean
    ) / rolling_std

    return zscore