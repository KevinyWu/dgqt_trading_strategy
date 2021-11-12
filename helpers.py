import numpy as np
import pandas as pd


def check_valid_weights(weights, param_sets, pairs=False):

    markets = ['ES','NQ','6E','CL','GC','ZC']
    total_weight = 0

    for market, param_weights in weights.items():

        if pairs:
            if (market[0] not in markets) or (market[1] not in markets):
                raise Exception('Improper Weights: Invalid Markets!')
        else:
            if market not in markets:
                raise Exception('Improper Weights: Invalid Markets!')
            markets.remove(market)

        keys = list(param_sets.keys())
        for param_key, weight in param_weights.items():

            if param_key not in keys:
                raise Exception('Improper Weights: Invalid Param Keys!')
            keys.remove(param_key)

            if weight < 0:
                raise Exception('Improper Weights: Negative Weight!')
            total_weight += weight

    if not np.isclose(total_weight, 1):
        raise Exception(f'Improper Weights: Weights Sum To {total_weight}!')


def load_data(market, market2=None):

    df = pd.read_csv(f'data/{market}.csv', index_col='Date')
    df.index = pd.to_datetime(df.index, infer_datetime_format=True)
    
    if market2:
        df2 = pd.read_csv(f'data/{market2}.csv', index_col='Date')
        df2.index = pd.to_datetime(df2.index, infer_datetime_format=True)
        df = pd.merge(df, df2, on='Date', suffixes=(f' {market}', f' {market2}'))
    
    return df


def sharpe(pnl, lookback=0, pairs=False):
    
    if pairs:
        spliced_cols = [c for c in pnl.columns if 'Spliced' in c]
        pnl['Spliced'] = pnl[spliced_cols[0]] + pnl[spliced_cols[1]]
    
    returns = pnl['Raw PnL'] / pnl['Spliced']
    return np.sqrt(252) * returns.mean() / returns.std(ddof=0)