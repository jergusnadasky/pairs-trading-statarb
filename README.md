# Statistical Arbitrage Dashboard

A quantitative finance project focused on statistical arbitrage, cointegration testing, and mean-reversion trading strategies. The system identifies statistically related equity pairs, generates trading signals using z-scores, backtests the strategy against a benchmark, and visualizes results through an interactive Streamlit dashboard.

The goal of the project was to build a research workflow similar to what would be used in a quantitative research or systematic trading environment while keeping the architecture modular, reproducible, and deployment-ready.

🔗 The app is deployed at: https://cointegration-lab.streamlit.app/

---

![alt text](https://github.com/jergusnadasky/pairs-trading-statarb/blob/main/img/statarb_demo.png "Demo Image")

---

# Project Purpose and Research Goals

This project is designed as a quantitative research and statistical arbitrage platform focused on identifying and evaluating mean-reverting relationships between financial assets.

Rather than attempting to simply "beat the market," the system is intended to simulate the type of workflow used in quantitative research and systematic trading environments. The platform allows researchers to test whether statistically related securities exhibit exploitable pricing inefficiencies and whether those inefficiencies persist out-of-sample.

The dashboard and analytics pipeline help answer research questions such as:

* Do certain assets maintain stable long-term statistical relationships?
* Are spread deviations temporary or persistent?
* Can cointegration produce tradable mean-reversion signals?
* How sensitive are results to entry thresholds and rolling windows?
* Does the strategy remain effective after transaction costs?
* Does market-neutral exposure reduce volatility and drawdowns?
* How does the strategy compare against directional buy-and-hold exposure on a risk-adjusted basis?

The project emphasizes:

* out-of-sample evaluation
* reproducible quantitative research workflows
* modular financial engineering architecture
* risk-adjusted portfolio analytics
* realistic backtesting assumptions
* interactive exploratory analysis

The system provides insights useful for:

* quantitative researchers
* systematic trading research
* statistical arbitrage experimentation
* financial engineering education
* time-series analysis studies
* portfolio risk analysis

A core insight demonstrated by the project is that lower raw returns do not necessarily imply a weaker strategy. Market-neutral statistical arbitrage systems are often designed to reduce directional market exposure, suppress volatility, and limit drawdowns rather than maximize outright equity growth.

---

# Project Overview

This project analyzes historical equity price data to identify pairs of securities that maintain a long-term statistical relationship. When the relationship deviates beyond a threshold, the strategy enters a long/short position expecting the spread to revert back toward its historical mean.

The project includes:

* historical market data collection
* cointegration testing
* spread construction
* z-score signal generation
* out-of-sample backtesting
* transaction cost modeling
* benchmark comparison
* portfolio analytics
* interactive dashboard visualization
* dashboard-ready data export

Historical market data is downloaded using `yfinance`.

---

# Why Adjusted Close Prices Are Used

The strategy uses **Adjusted Close** prices instead of raw close prices because adjusted prices account for:

* stock splits
* dividends
* corporate actions

This preserves consistency in historical returns and prevents distortions in spreads and backtests.

Adjusted close prices are the standard for end-of-day quantitative backtesting because they represent the actual economic value of holding the asset over time.

The project intentionally ignores:

* intraday highs/lows
* open prices
* volume

because the strategy is based on daily statistical relationships rather than intraday execution.

---

# Train/Test Methodology

The system separates historical data into:

* a **training window** used for pair discovery and cointegration estimation
* a **testing window** used exclusively for out-of-sample backtesting

This prevents look-ahead bias and more closely resembles a real quantitative research workflow.

The training window is used to estimate:

* cointegration relationships
* hedge ratios
* spread properties
* mean-reversion behavior

The testing window is then used to:

* generate trading signals
* evaluate strategy performance
* compare against a benchmark
* measure out-of-sample robustness

This separation helps ensure that backtest results better reflect unseen market conditions rather than overfitting historical data.

---

# Pair Selection Process

Given a universe of tickers, the project evaluates every possible pair combination:

$$
\binom{n}{2}
$$

Each pair is tested using the Engle-Granger cointegration test.

The system evaluates pair quality using:

| Metric              | Purpose                     |
| ------------------- | --------------------------- |
| p-value             | Statistical significance    |
| Cointegration score | Strength of relationship    |
| Hedge ratio         | Spread construction         |
| R²                  | Linear relationship quality |
| Half-life           | Speed of mean reversion     |

Pairs are filtered using:

* p-value thresholds
* half-life constraints
* spread stability
* minimum historical overlap requirements

Among statistically significant pairs, the pair with the strongest cointegration relationship (lowest p-value) is selected for out-of-sample backtesting.

---

# Spread and Z-Score Modeling

The spread between two assets is constructed as:

$$
S_t = P_{1,t} - \beta P_{2,t}
$$

where:

* $P_1$ and $P_2$ are asset prices
* $\beta$ is the hedge ratio estimated from regression

The spread is standardized using a rolling z-score:

$$
Z_t = \frac{S_t - \mu}{\sigma}
$$

Trading logic:

| Condition      | Action        |
| -------------- | ------------- |
| Z-score > +2   | Short spread  |
| Z-score < -2   | Long spread   |
| Z-score near 0 | Exit position |

The strategy assumes the spread will revert toward its historical mean.

---

# Backtesting Workflow

The project is designed as an interactive research dashboard rather than a static script.

Launch the application with:

```bash
streamlit run app/dashboard.py
```

The dashboard allows the user to:

1. Select a custom universe of tickers
2. Configure training and testing windows
3. Adjust z-score thresholds
4. Modify transaction costs
5. Run cointegration analysis interactively

The backend pipeline then:

1. Downloads historical market data from Yahoo Finance
2. Cleans and validates ticker data
3. Runs Engle-Granger cointegration tests
4. Selects statistically significant pairs
5. Computes spread and z-score series
6. Generates long/short trading signals
7. Runs an out-of-sample backtest
8. Computes portfolio and risk metrics
9. Exports dashboard-ready analytics

Generated outputs include:

```text
results/
├── cointegration_results.csv
├── equity_curve.csv
├── trade_log.csv
├── dashboard_data.json
```

---

# Transaction Cost Modeling

Transaction costs are modeled as proportional costs applied on each position change across both legs of the trade.

This helps produce more realistic backtest results and prevents overstating profitability.

The transaction cost parameter is fully configurable through the dashboard interface.

---

# Dashboard Features

The Streamlit dashboard visualizes the complete research pipeline through interactive analytics and portfolio visualizations.

## Interactive Research Workflow

Users can dynamically configure:

* ticker universes
* train/test windows
* z-score thresholds
* stop-loss thresholds
* transaction costs
* cointegration significance thresholds

This allows rapid experimentation with different statistical arbitrage setups.

## Equity Curve Comparison

Compares:

* statistical arbitrage strategy performance
* buy-and-hold benchmark performance

using interactive Plotly visualizations.

## Z-Score Signal Visualization

Displays:

* spread deviations
* long/short trading signals
* entry and exit thresholds
* mean-reversion behavior

## Cointegrated Pair Reporting

Shows:

* statistically significant pairs
* p-values
* hedge ratios
* pair-selection results
* all tested pair combinations

for the selected ticker universe.

## Correlation Heatmap

The dashboard includes a correlation heatmap to visualize relationships across the full asset universe.

The heatmap helps:

* identify sector clustering
* observe highly correlated securities
* compare relationships outside of cointegration
* inspect the structure of the dataset

The heatmap is generated using the correlation matrix of adjusted close returns.

## Trade Log

Displays trade-level execution information including:

* entry dates
* exit dates
* trade direction
* portfolio impact
* realized trade-level PnL

## Robust Data Validation

The dashboard validates ticker availability before running the statistical pipeline.

The system:

* detects invalid or delisted tickers
* removes unavailable assets
* prevents failed backtests from crashing the application
* provides user-facing error messages for missing market data

This improves deployment robustness and user experience.

---

# Performance Metrics

The project computes several portfolio and risk metrics commonly used in quantitative finance and systematic trading research.

| Metric            | Description                             |
| ----------------- | --------------------------------------- |
| CAGR              | Compound annual growth rate             |
| Annual Return     | Average yearly return                   |
| Annual Volatility | Standard deviation of returns           |
| Sharpe Ratio      | Return adjusted for volatility          |
| Sortino Ratio     | Return adjusted for downside volatility |
| Max Drawdown      | Largest peak-to-trough decline          |
| Calmar Ratio      | Return relative to drawdown             |
| Win Rate          | Percentage of positive return periods   |

The dashboard compares these metrics against a buy-and-hold benchmark.

---

# Dashboard Data Export

The project exports all dashboard-ready analytics into:

```text
results/dashboard_data.json
```

This JSON file stores:

* selected pair information
* spread values
* z-scores
* trading signals
* strategy returns
* benchmark returns
* equity curves
* portfolio metrics
* pair selection results

Separating dashboard data generation from dashboard rendering keeps the research pipeline modular and easier to extend.

---

# Running Locally

Clone the repository:

```bash
git clone https://github.com/jergusnadasky/pairs-trading-statarb.git
cd pairs-trading-statarb
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate the environment.

### Windows

```bash
venv\Scripts\activate
```

### macOS / Linux

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Launch the dashboard:

```bash
streamlit run app/dashboard.py
```

---

# Technologies Used

## Quantitative Finance / Statistics

* Statistical Arbitrage
* Cointegration Testing
* Mean Reversion Modeling
* Time-Series Analysis
* Econometrics
* Portfolio Analytics
* Risk Modeling
* Out-of-Sample Evaluation

## Python Libraries

* pandas
* numpy
* statsmodels
* plotly
* streamlit
* yfinance

---

# Skills Demonstrated

* Quantitative research
* Statistical modeling
* Financial time-series analysis
* Econometric testing
* Backtesting system development
* Portfolio analytics
* Risk-adjusted performance analysis
* Data visualization
* Python-based financial engineering
* Interactive dashboard development
* Modular software architecture
* Robust error handling
* Deployment-oriented application design
