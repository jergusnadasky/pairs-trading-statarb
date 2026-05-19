# Statistical Arbitrage Dashboard

A quantitative finance project focused on statistical arbitrage, cointegration testing, and mean-reversion trading strategies. The system identifies statistically related equity pairs, generates trading signals using z-scores, backtests the strategy against a benchmark, and visualizes results through an interactive Streamlit dashboard.

The goal of the project was to build a research workflow similar to what would be used in a quantitative research or systematic trading environment while keeping the architecture modular and reproducible.

---

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

Historical price data is downloaded using the :contentReference[oaicite:0]{index=0}.

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

Given a universe of tickers, the project evaluates every possible pair:

\[
\binom{n}{2}
\]

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

\[
S_t = P_{1,t} - \beta P_{2,t}
\]

where:

- \(P_1\) and \(P_2\) are asset prices
- \(\beta\) is the hedge ratio estimated from regression

The spread is standardized using a rolling z-score:

\[
Z_t = \frac{S_t - \mu}{\sigma}
\]

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

executes the full pipeline:

Downloads market data from Yahoo Finance
Finds cointegrated pairs
Selects the strongest pair
Computes spread and z-score
Generates trading signals
Runs the backtest
Computes portfolio metrics
Exports dashboard-ready analytics
Launches the dashboard

Generated outputs include:

results/
├── cointegration_results.csv
├── equity_curve.csv
├── trade_log.csv
├── dashboard_data.json
Dashboard Features

The Streamlit dashboard visualizes the entire research pipeline.

Equity Curve Comparison

Compares:

statistical arbitrage strategy performance
buy-and-hold benchmark performance

using interactive Plotly charts.

Z-Score Signal Visualization

Displays:

spread deviations
long/short signals
entry thresholds
mean-reversion behavior
Cointegrated Pair Reporting

Shows:

candidate pairs
p-values
hedge ratios

for all statistically significant combinations.

Correlation Heatmap

The dashboard includes a correlation heatmap to visualize relationships across the entire ticker universe.

This helps:

identify sector clustering
observe highly correlated assets
compare pair relationships outside of cointegration
visually inspect the structure of the dataset

The heatmap is generated from the full correlation matrix of adjusted close returns.

Trade Log

Displays trade-level execution information including:

entry dates
exit dates
trade direction
portfolio impact
Performance Metrics

The project computes several portfolio and risk metrics commonly used in quantitative finance.

Metric	Description
CAGR	Compound annual growth rate
Annual Return	Average yearly return
Annual Volatility	Standard deviation of returns
Sharpe Ratio	Return adjusted for volatility
Sortino Ratio	Return adjusted for downside volatility
Max Drawdown	Largest peak-to-trough decline
Calmar Ratio	Return relative to drawdown
Win Rate	Percentage of positive return periods

The dashboard compares these metrics against a buy-and-hold benchmark.

Dashboard Data Export

The project exports all visualization-ready analytics into:

results/dashboard_data.json

This JSON file stores:

selected pair information
spread values
z-scores
trading signals
strategy returns
benchmark returns
equity curves
portfolio metrics
correlation matrices
pair selection results

Separating dashboard data generation from dashboard rendering keeps the research pipeline modular and easier to extend.

Technologies Used
Quantitative Finance / Statistics
Statistical Arbitrage
Cointegration Testing
Mean Reversion Modeling
Time-Series Analysis
Econometrics
Portfolio Analytics
Risk Modeling
Python Libraries
pandas
numpy
statsmodels
plotly
streamlit
yfinance
Skills Demonstrated
Quantitative research
Statistical modeling
Financial time-series analysis
Econometric testing
Backtesting system development
Portfolio analytics
Data visualization
Python-based financial engineering
Interactive dashboard development
