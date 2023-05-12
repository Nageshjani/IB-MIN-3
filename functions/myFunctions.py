
import threading
import time
import pandas as pd
from collections import defaultdict
import numpy as np
import math
from scipy.stats import norm
from scipy.optimize import brentq
from datetime import datetime
from client.contracts.myContracts import usTechOpt
from settings import RECORDS_DIR, logger, TZ
from parameters import *



def atm_call_option(contract_df,stock_price):
    
    df=contract_df
    df_call=df[df['call/put']=="C"]
    df_call=df_call.sort_values(by='symbol')
    symbolList=list(df_call['symbol'])
    
    #STEP -1 ATM
    atm=None
    atm_index=None
    LTP=stock_price
    for local_symbol in symbolList:
        strike=float(local_symbol.split()[1][7:])/1000
        if strike>LTP:
            break
        atm=strike
        atm_index=symbolList.index(local_symbol)

    ticker=local_symbol.split()[0]
    # print(ticker,'Atm:',atm)
    logger.debug(f'{ticker} ATM : {atm}')
    call_local_symbols=symbolList[atm_index-5:atm_index+5]
    return call_local_symbols


def atm_put_option(contract_df,stock_price):
    df=contract_df
    df_put=df[df['call/put']=="P"]
    df_put=df_put.sort_values(by='symbol')
    symbolList=list(df_put['symbol'])
    
    #STEP -1 ATM
    atm=None
    atm_index=None
    LTP=stock_price
    for local_symbol in symbolList:
        strike=float(local_symbol.split()[1][7:])/1000
        if strike>LTP:
            break
        atm=strike
        atm_index=symbolList.index(local_symbol)

    # print('atm:',atm)
    put_local_symbols=symbolList[atm_index-5:atm_index+5]
    return put_local_symbols



contract_event = threading.Event()
def Contracts_Download(app,tickers):
    for ticker in tickers:
        contract_event.clear() 
        try:
            app.reqContractDetails(tickers.index(ticker), usTechOpt(ticker)) 
        except:
            # print(f'Error (Contracts_Download) : {ticker}')
            logger.debug(f'Error (Contracts_Download) : {ticker}')
        contract_event.wait() 
        
        app.options+=atm_call_option(app.df_data[ticker],app.underlyingPrice[ticker])
        app.options+= atm_put_option(app.df_data[ticker],app.underlyingPrice[ticker])

    
    if len(app.options)==len(tickers)*2*10:
        # print('4. Success(options)')
        logger.debug('4. Success(options)')
    else:
        # print('4. Error(options)')
        logger.debug('4. Error(options)')

def calc_historical_volatility(hist_data):
    hist_data['log_return'] = np.log(hist_data['Close']/hist_data['Close'].shift(1))

    # Calculate daily volatility
    hist_data['daily_volatility'] = hist_data['log_return'].rolling(window=21).std() * math.sqrt(252)

    # Calculate annualized volatility
    hist_volatility = hist_data['daily_volatility'].iloc[-1] * 100 * math.sqrt(252)

    return hist_volatility


def calc_implied_volatility(df, hist_volatility):
    S = df['Close'].iloc[-1]
    K = S
    T = 30/365
    r = 0.01
    C = S * 0.01

    def black_scholes_iv(sigma):
        d1 = (np.log(S/K) + (r + sigma**2/2)*T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        return S * norm.cdf(d1) - K * np.exp(-r*T) * norm.cdf(d2) - C

    iv = brentq(lambda x: black_scholes_iv(x) - C, 0.001, 5.0)
    iv *= hist_volatility / (np.sqrt(T) * S)
    return iv


def countoptionChainGreeks(app,tickers):
    flag=True
     
    for ticker in tickers:
        if len(app.optionChainGreeks[ticker]['C'])+len(app.optionChainGreeks[ticker]['P'])!=20:
            # print(f'5. Error(optionChainGreeks) :  {ticker}')
            logger.debug(f'5. Error(optionChainGreeks) :  {ticker}')
            flag==False
    if flag==True:
        #  print('5. Success(optionChainGreeks)')
         logger.debug('5. Success(optionChainGreeks)')








def findDeltas(app,tickers):
     
     while True:
        
        app.optionDeltas=[]
        for ticker in tickers:
            if app.optionChainGreeks[ticker]['C'] and app.optionChainGreeks[ticker]['P']:

                callGreeks=app.optionChainGreeks[ticker]['C']
                putGreeks=app.optionChainGreeks[ticker]['P']
                resCallLocalSymbol=None
                resPutLocalSymbol=None

                minn=float('inf')
                for local_symbol in  callGreeks:
                    try:
                        delta=callGreeks[local_symbol]['delta']
                        if abs(delta-app.CALL_DELTA) <minn:
                            minn=abs(delta-app.CALL_DELTA)
                            resCallLocalSymbol=local_symbol
                    except:
                        logger.debug('Error (findDeltas/callgreek) : no delta for given localsymbol')
                       
                
                minn=float('inf')
                for local_symbol in  putGreeks:
                    try:
                        delta=putGreeks[local_symbol]['delta']
                        delta=-(delta)
                        if abs(delta-app.PUT_DELTA) <minn:
                            minn=abs(delta-app.PUT_DELTA)
                            resPutLocalSymbol=local_symbol
                    except:
                        logger.debug('Error (findDeltas/putgreek) : no delta for given localsymbol')


                
                if resCallLocalSymbol and resPutLocalSymbol:
                    app.optionDeltas.append(resCallLocalSymbol)
                    app.optionDeltas.append(resPutLocalSymbol)
        

        logger.debug(f'findDeltas {app.optionDeltas}')
        time.sleep(15)







def printDeltas(app,tickers):
        logger.debug('Inside printDeltas')
        while True: 
            
            #print('printDelta',app.optionDeltas)
            keysList=list(app.greekMain.keys())
            i=0
            while i<len(keysList):
                try:

                    now=datetime.now()
                    t=now.strftime("%H:%M:%S")
                    if app.greekMain[keysList[i]] and app.greekMain[keysList[i+1]]:
                        callGreek=app.greekMain[keysList[i]]
                        putGreek=app.greekMain[keysList[i+1]]
                        netIv=round(callGreek['impliedVol']-putGreek['impliedVol'],4)
                        ticker=app.optionDeltas[i].split()[0]
                        callask=callGreek['ask']
                        callbid=callGreek['bid']
                        putask=putGreek['ask']
                        putbid=putGreek['bid']
                        stockIv=app.stocksIv[ticker]
                        stkOptIv=round(stockIv-((callGreek['impliedVol']+putGreek['impliedVol'])/2),4)
                        if AVG_IVS:
                            callgreeks=app.optionChainGreeks[ticker]['C']
                            putgreeks=app.optionChainGreeks[ticker]['P']
                            callIv=0
                            putIv=0
                            for local_symbol in callgreeks:
                                callIv=callIv+callgreeks[local_symbol]['impliedVol']
                            for local_symbol in putgreeks:
                                putIv=putIv+putgreeks[local_symbol]['impliedVol']
                            CallPutIv=round((callIv+putIv)/2,4)
                            print(f'{ticker} | {t} | NetIv {netIv} | C/Bid: {callbid} | C/Ask: {callask} | P/Bid: {putbid} | P/Ask: {putask} | stkoptIv: {stkOptIv} |  AvgIv: {CallPutIv}')
                            logger.debug(f'{ticker} | {t} | NetIv {netIv} | C/Bid: {callbid} | C/Ask: {callask} | P/Bid: {putbid} | P/Ask: {putask} | stkoptIv: {stkOptIv} |  AvgIv: {CallPutIv}')
                        else:
                            print(ticker,'|',t,'|','NetIv: ',netIv,'|','C/Bid: ',callbid,'|','C/Ask: ',callask,'|','P/Bid: ',putbid,'|','P/Ask: ',putask,'|','stkOptIv',stkOptIv)
                            logger.debug(f'{ticker} | {t} | NetIv {netIv} | C/Bid: {callbid} | C/Ask: {callask} | P/Bid {putbid} | P/Ask {putask} | stkoptIv {stkOptIv}' )
                except:
                    logger.debug('Threading Mixed but nothing To be worried')
                i=i+2
            
            if len(app.greekMain)<len(tickers)*2:
                time.sleep(10)
            else:
                time.sleep(1)


                