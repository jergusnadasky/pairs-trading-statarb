# Statistical Arbitrage Dashboard

A quantitative finance project focused on statistical arbitrage, cointegration testing, and mean-reversion trading strategies. The system identifies statistically related equity pairs, generates trading signals using z-scores, backtests the strategy against a benchmark, and visualizes results through an interactive Streamlit dashboard.

The goal of the project was to build a research workflow similar to what would be used in a quantitative research or systematic trading environment while keeping the architecture modular and reproducible.

---

![alt text](https://github.com/jergusnadasky/pairs-trading-statarb/blob/main/img/statarb_demo.png "Demo Image")


# Project Overview

This project analyzes historical equity price data to identify pairs of securities that maintain a long-term statistical relationship. When the relationship deviates beyond a threshold, the strategy enters a long/short position expecting the spread to revert back toward its historical mean.

The project includes:

- historical market data collection
- cointegration testing
- spread construction
- z-score signal generation
- backtesting with transaction costs
- benchmark comparison
- portfolio analytics
- interactive dashboard visualization

Historical market data is downloaded using `yfinance`.

---

# Why Adjusted Close Prices Are Used

The strategy uses **Adjusted Close** prices instead of raw close prices because adjusted prices account for:

- stock splits
- dividends
- corporate actions

This preserves consistency in historical returns and prevents distortions in spreads and backtests.

Adjusted close prices are the standard for end-of-day quantitative backtesting because they represent the actual economic value of holding the asset over time.

The project intentionally ignores:

- intraday highs/lows
- open prices
- volume

because the strategy is based on daily statistical relationships rather than intraday execution.

---

# Pair Selection Process

Given a universe of tickers, the project evaluates every possible pair combination:

$$
\binom{n}{2}
$$

Each pair is tested using the Engle-Granger cointegration test.

The system evaluates pair quality using:

| Metric | Purpose |
|---|---|
| p-value | Statistical significance |
| Cointegration score | Strength of relationship |
| Hedge ratio | Spread construction |
| R² | Linear relationship quality |
| Half-life | Speed of mean reversion |

Pairs are filtered using:

- p-value < 0.05
- half-life constraints
- spread stability

The statistically strongest pair is selected for backtesting.

---

# Spread and Z-Score Modeling

The spread between two assets is constructed as:

$$
S_t = P_{1,t} - \beta P_{2,t}
$$

where:

- $P_1$ and $P_2$ are asset prices
- $\beta$ is the hedge ratio estimated from regression

The spread is standardized using a rolling z-score:

$$
Z_t = \frac{S_t - \mu}{\sigma}
$$

Trading logic:

| Condition | Action |
|---|---|
| Z-score > +2 | Short spread |
| Z-score < -2 | Long spread |
| Z-score near 0 | Exit position |

The strategy assumes the spread will revert toward its historical mean.

---

# Backtesting Workflow

Running:

```bash
python src/main.py
```

executes the full pipeline:

1. Downloads market data from Yahoo Finance
2. Finds cointegrated pairs
3. Selects the strongest pair
4. Computes spread and z-score
5. Generates trading signals
6. Runs the backtest
7. Computes portfolio metrics
8. Exports dashboard-ready analytics
9. Launches the dashboard

Generated outputs include:

```text
results/
├── cointegration_results.csv
├── equity_curve.csv
├── trade_log.csv
├── dashboard_data.json
```

---

# Dashboard Features

The Streamlit dashboard visualizes the complete research pipeline through interactive analytics and portfolio visualizations.

## Equity Curve Comparison

Compares:

- statistical arbitrage strategy performance
- buy-and-hold benchmark performance

using interactive Plotly visualizations.

## Z-Score Signal Visualization

Displays:

- spread deviations
- long/short trading signals
- entry and exit thresholds
- mean-reversion behavior

## Cointegrated Pair Reporting

Shows:

- statistically significant pairs
- p-values
- hedge ratios
- pair-selection results

for all valid combinations in the ticker universe.

## Correlation Heatmap

The dashboard includes a correlation heatmap to visualize relationships across the full asset universe.

The heatmap helps:

- identify sector clustering
- observe highly correlated securities
- compare relationships outside of cointegration
- inspect the structure of the dataset

The heatmap is generated using the correlation matrix of adjusted close returns.

## Trade Log

Displays trade-level execution information including:

- entry dates
- exit dates
- trade direction
- portfolio impact

---

# Performance Metrics

The project computes several portfolio and risk metrics commonly used in quantitative finance and systematic trading research.

| Metric | Description |
|---|---|
| CAGR | Compound annual growth rate |
| Annual Return | Average yearly return |
| Annual Volatility | Standard deviation of returns |
| Sharpe Ratio | Return adjusted for volatility |
| Sortino Ratio | Return adjusted for downside volatility |
| Max Drawdown | Largest peak-to-trough decline |
| Calmar Ratio | Return relative to drawdown |
| Win Rate | Percentage of positive return periods |

The dashboard compares these metrics against a buy-and-hold benchmark.

---

# Dashboard Data Export

The project exports all dashboard-ready analytics into:

```text
results/dashboard_data.json
```

This JSON file stores:

- selected pair information
- spread values
- z-scores
- trading signals
- strategy returns
- benchmark returns
- equity curves
- portfolio metrics
- correlation matrices
- pair selection results

Separating dashboard data generation from dashboard rendering keeps the research pipeline modular and easier to extend.

---

# Technologies Used

## Quantitative Finance / Statistics

- Statistical Arbitrage
- Cointegration Testing
- Mean Reversion Modeling
- Time-Series Analysis
- Econometrics
- Portfolio Analytics
- Risk Modeling

## Python Libraries

- pandas
- numpy
- statsmodels
- plotly
- streamlit
- yfinance

---

# Skills Demonstrated

- Quantitative research
- Statistical modeling
- Financial time-series analysis
- Econometric testing
- Backtesting system development
- Portfolio analytics
- Data visualization
- Python-based financial engineering
- Interactive dashboard development
