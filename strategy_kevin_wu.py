from helpers import *

import numpy as np
import pandas as pd


# Computes RSI
def rsi(market, params):

    # Makes list of closing prices
    df = load_data(market)
    lb = params['lookback']
    prices = np.array(df['Close'])

    # Makes lists of gains (upPrices) and losses (downPrices)
    i = 0
    upPrices = []
    downPrices = []
    while i < len(prices):
        if i == 0:
            upPrices.append(0)
            downPrices.append(0)
        else:
            if (prices[i] - prices[i - 1]) > 0:
                upPrices.append(prices[i] - prices[i - 1])
                downPrices.append(0)
            else:
                downPrices.append(prices[i] - prices[i - 1])
                upPrices.append(0)
        i += 1

    # Calculate the average gain and loss   
    x = 0
    avg_gain = []
    avg_loss = []
    while x < len(upPrices):
        if x < lb + 1:
            avg_gain.append(0)
            avg_loss.append(0)
        else:
            sumGain = 0
            sumLoss = 0
            y = x - lb
            while y <= x:
                sumGain += upPrices[y]
                sumLoss += downPrices[y]
                y += 1
            avg_gain.append(sumGain/lb)
            avg_loss.append(abs(sumLoss/lb))
        x += 1

    # Calculates RS and RSI
    p = 0
    RS = []
    RSI = []
    while p < len(prices):
        if p < lb + 1:
            RS.append(0)
            RSI.append(0)
        else:
            RSvalue = (avg_gain[p]/avg_loss[p])
            RS.append(RSvalue)
            RSI.append(100 - (100/(1 + RSvalue)))
        p += 1

    return upPrices, downPrices, avg_gain, avg_loss, RS, RSI


# Computes Stochastic Oscillator
def stochastic_oscillator(market, params):
    
    # Makes list of close, open, high, low prices
    df = load_data(market)
    lb = params['lookback']
    array_close = np.array(df['Close'])
    array_open = np.array(df['Open'])
    array_high = np.array(df['High'])
    array_low = np.array(df['Low'])

    # Calculate highest of k periods
    y = 0
    z = 0
    # kperiods are lookback starting from 0 index
    kperiods = lb - 1
    array_highest = []
    for x in range(0, array_high.size - kperiods):
        z = array_high[y]
        for j in range(0, kperiods):
            if z < array_high[y + 1]:
                z = array_high[y + 1]
            y = y + 1
        array_highest.append(z)
        y = y - (kperiods - 1)

    # Calculate lowest of k periods
    y = 0
    z = 0
    array_lowest = []
    for x in range(0, array_low.size - kperiods):
        z = array_low[y]
        for j in range(0, kperiods):
            if z > array_low[y + 1]:
                z = array_low[y + 1]
            y = y + 1
        array_lowest.append(z)
        y = y - (kperiods - 1)

    # Calculate K values
    Kvalue = []
    for x in range(kperiods, array_close.size):
       k = ((array_close[x] - array_lowest[x - kperiods]) * 100/(array_highest[x - kperiods] - array_lowest[x - kperiods]))
       Kvalue.append(k)

    # Calculate D values
    y = 0
    dperiods = 3
    Dvalue = [None,None]
    mean = 0
    for x in range(0,len(Kvalue) - dperiods + 1):
        sum = 0
        for j in range(0, dperiods):
            sum = Kvalue[y] + sum
            y = y + 1
        mean = sum/dperiods
        Dvalue.append(mean)
        y = y - (dperiods - 1)
    
    # Add zeros to the front to match table height
    for x in range(lb - 1):
        array_highest.insert(0, 0)
        array_lowest.insert(0, 0)
        Kvalue.insert(0, 0)
        Dvalue.insert(0, 0)
        
    return array_highest, array_lowest, Kvalue, Dvalue


# Assign an integer key to each parameter set you want to trade.
PARAMS = {
    1: {'lookback': 14, 'thresh_rsi': 80, 'thresh_so': 80},
    2: {'lookback': 14, 'thresh_rsi': 80.5, 'thresh_so': 81},  
    3: {'lookback': 14, 'thresh_rsi': 81, 'thresh_so': 82}
}


# List weight per parameter-set key per market.
# Individual weights must be positive.
# Sum of all weights must be 1.
MARKET_WEIGHTS = {
    'ES': {1: 0.18, 2: 0.175, 3: 0.175},
    'NQ': {1: 0.16, 2: 0.16, 3: 0.15},
    '6E': {1: 0.00, 2: 0.00, 3: 0.00},
    'CL': {1: 0.00, 2: 0.00, 2: 0.00},    
    'GC': {1: 0.00, 2: 0.00, 3: 0.00},
    'ZC': {1: 0.00, 2: 0.00, 3: 0.00}
}
check_valid_weights(MARKET_WEIGHTS, PARAMS)


# Executes trade logic
def trade_logic(market, params):

    df = load_data(market)
    thresh_rsi = params['thresh_rsi']
    thresh_so = params['thresh_so']
    lb = params['lookback']
    
    ### RSI ############################################################
    upPrices, downPrices, avg_gain, avg_loss, RS, RSI = rsi(market, params)
    df['Gain'] = upPrices
    df['Loss'] = downPrices
    df['AvgGain'] = avg_gain
    df['AvgLoss'] = avg_loss
    df['RS'] = RS
    df['RSI'] = RSI
    
    ### SO #############################################################
    highest, lowest, Kvalue, Dvalue = stochastic_oscillator(market, params)
    df['Highest'] = highest
    df['Lowest'] = lowest
    df['K value'] = Kvalue
    df['D value'] = Dvalue
    
    ### LOGIC ##########################################################

    # Determine positions taken    
    position = [0] * len(df)
    for i in range(lb, len(df)):
        if Dvalue[i] != None:
            # Sell
            if RSI[i] > thresh_rsi and Dvalue[i] > thresh_so:
                position[i] = -1
            # Buy
            if RSI[i] < 100 - thresh_rsi and Dvalue[i] < 100 - thresh_so:
                position[i] = 1
    df['Position'] = position

    # Calculate PnLs
    df['Raw PnL'] = df['Position'] * (df['Close'].shift(-1) - df['Close'])

    ####################################################################

    return df, sharpe(df)