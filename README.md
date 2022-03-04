# DGQT Trading Strategy

<img src="https://github.com/KevinyWu/KevinyWu/blob/main/images/dgqt.png" alt="drawing" width="250"/>

My strategy for the UChicago Derivatives Group Quant Trading paper trading project, backtested with data from 2010-2020 for 6E, CL, ES, GC, NQ, and ZC.

**Strategy**
- Parameters: `{'lookback': days, 'thresh_rsi': threshold RSI, 'thresh_so': threshold stochastic oscillator}`
- `{14, 80, 80}, {14, 80.5, 81}, {14, 81, 82}`
- For each parameter set:
    - Sell if for past `N` days: `RSI > R and SO > S`
    - Buy if for past `N` days: `RSI < 100-R and SO < 100-S`
    - Otherwise do nothing
    
**Determining weight of parameter sets within a commodity**
- Compute annual Sharpe ratio for each parameter set
- Take parameter sets with Sharpe greater than 0.45
- Use risk-parity method to allocate equal risk to each parameter set

**Determining weight of commodities**
- Compute annual Sharpe ratio for each commodity
- Take the markets with Sharpe greater than 0.45, or the top three if less reach the threshold of 0.45
- Use risk-parity method to allocate equal risk to each parameter set
- Allocate more weight to more liquid markets to decrease slippage
- Scale the weight of parameter sets within each commodity appropriately
