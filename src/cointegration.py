import numpy as np
import pandas as pd
import statsmodels.api as sm

from itertools import combinations
from statsmodels.tsa.stattools import coint



def estimate_half_life(spread):
    spread_lag = spread.shift(1).dropna()
    spread_ret = spread.diff().dropna()

    spread_lag = spread_lag.loc[spread_ret.index]

    beta = np.polyfit(spread_lag, spread_ret, 1)[0]

    half_life = -np.log(2) / beta

    return max(5, int(round(half_life)))



def find_cointegrated_pairs(prices, pvalue_threshold=0.05):
    tickers = prices.columns.tolist()

    results = []

    for t1, t2 in combinations(tickers, 2):
        s1 = prices[t1].dropna()
        s2 = prices[t2].dropna()

        common = s1.index.intersection(s2.index)

        s1 = s1.loc[common]
        s2 = s2.loc[common]

        if len(common) < 100:
            continue

        score, pvalue, _ = coint(s1, s2)

        model = sm.OLS(s1, sm.add_constant(s2)).fit()

        hedge_ratio = model.params.iloc[1]
        r_squared = model.rsquared

        spread = s1 - hedge_ratio * s2

        half_life = estimate_half_life(spread)

        results.append(
            {
                "ticker_1": t1,
                "ticker_2": t2,
                "p_value": pvalue,
                "score": score,
                "hedge_ratio": hedge_ratio,
                "r_squared": r_squared,
                "half_life": half_life,
                "cointegrated": pvalue < pvalue_threshold,
            }
        )

    return pd.DataFrame(results).sort_values("p_value")



def compute_spread(prices, t1, t2, hedge_ratio):
    return prices[t1] - hedge_ratio * prices[t2]



def compute_zscore(spread, window):
    rolling_mean = spread.rolling(window).mean()
    rolling_std = spread.rolling(window).std()

    zscore = (spread - rolling_mean) / rolling_std

    return zscore