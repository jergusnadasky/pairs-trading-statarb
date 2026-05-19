import pandas as pd
import numpy as np



def compute_returns(
    prices,
    t1,
    t2,
    hedge_ratio,
    signals,
    transaction_cost=0.001,
):
    p1 = prices[t1]
    p2 = prices[t2]

    r1 = p1.pct_change()
    r2 = p2.pct_change()

    # Spread return for pairs trade
    spread_return = r1 - hedge_ratio * r2

    # Strategy return using lagged signal
    strategy_return = signals.shift(1) * spread_return

    # Transaction costs
    trades = signals.diff().abs().fillna(0)

    costs = trades * transaction_cost * 2

    strategy_return = strategy_return - costs

    strategy_return = strategy_return.fillna(0)

    # Strategy equity curve
    equity_curve = (1 + strategy_return).cumprod()

    # Buy & hold benchmark (using first ticker)
    bh_return = r1.fillna(0)

    bh_equity = (1 + bh_return).cumprod()

    out = pd.DataFrame(
        {
            "strategy_return": strategy_return,
            "equity_curve": equity_curve,
            "signal": signals,
            "bh_return": bh_return,
            "bh_equity": bh_equity,
        }
    )

    return out

def generate_trade_log(signals, returns):
    trades = []

    current_trade = None

    for idx in signals.index:
        sig = signals.loc[idx]

        if current_trade is None and sig != 0:
            current_trade = {
                "entry_date": idx,
                "side": sig,
                "entry_equity": returns.loc[idx],
            }

        elif current_trade is not None and sig == 0:
            current_trade["exit_date"] = idx
            current_trade["exit_equity"] = returns.loc[idx]
            current_trade["pnl"] = (
                current_trade["exit_equity"]
                - current_trade["entry_equity"]
            )

            trades.append(current_trade)
            current_trade = None

    return pd.DataFrame(trades)

def performance_metrics(returns):
    daily = returns.dropna()

    cumulative = (1 + daily).cumprod()

    years = len(daily) / 252

    cagr = cumulative.iloc[-1] ** (1 / years) - 1

    annual_return = daily.mean() * 252

    annual_vol = daily.std() * np.sqrt(252)

    sharpe = 0
    if annual_vol != 0:
        sharpe = annual_return / annual_vol

    downside = daily[daily < 0]

    downside_vol = downside.std() * np.sqrt(252)

    sortino = 0
    if downside_vol != 0:
        sortino = annual_return / downside_vol

    rolling_max = cumulative.cummax()

    drawdown = (cumulative - rolling_max) / rolling_max

    max_drawdown = drawdown.min()

    calmar = 0
    if max_drawdown != 0:
        calmar = cagr / abs(max_drawdown)

    win_rate = (daily > 0).mean() * 100

    return {
        # Dashboard-compatible keys
        "ann_return": round(annual_return * 100, 2),
        "ann_vol": round(annual_vol * 100, 2),
        "sharpe": round(sharpe, 3),
        "max_drawdown": round(max_drawdown * 100, 2),
        "win_rate": round(win_rate, 2),

        # Extra quant metrics
        "cagr": round(cagr * 100, 2),
        "sortino": round(sortino, 2),
        "calmar": round(calmar, 2),
    }
    
    