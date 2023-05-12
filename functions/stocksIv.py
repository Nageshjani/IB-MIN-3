from ibapi.contract import Contract
import threading
import pandas as pd
from functions.myFunctions import calc_historical_volatility,calc_implied_volatility
from settings import RECORDS_DIR, logger, TZ

e=threading.Event()
def downloadStcoksIV(app,tickers):
    #EXCHANGE=SMART
    try:

        def usTechStk(symbol,sec_type="STK",currency="USD",exchange="SMART"):
            contract = Contract()
            contract.symbol = symbol
            contract.secType = sec_type
            contract.currency = currency
            contract.exchange = exchange
            return contract 
    except:
        # print('Error : (downloadStockIv): Invalid Contract')
        logger.debug('Error : (downloadStockIv): Invalid Contract')
    
    def histData(req_num,contract,duration,candle_size):
        try:
            app.reqHistoricalData(reqId=req_num, 
                                contract=contract,
                                endDateTime='',
                                durationStr=duration,
                                barSizeSetting=candle_size,
                                whatToShow='TRADES',
                                useRTH=1,
                                formatDate=1,
                                keepUpToDate=0,
                                chartOptions=[])
        except:
            # print('Error :(stockIv) Histdata ')
            logger.debug('Error :(stockIv) Histdata ')
        
    
    def dataDataframe(app,symbols, symbol):
        try:
            df = pd.DataFrame(app.histData[symbols.index(symbol)])
            df.set_index("Date",inplace=True)
            return df
        except:
            # print(f'Error (dataframe) No histdata for {symbol}')
            logger.debug(f'Error (dataframe) No histdata for {symbol}')
    

    
    for ticker in tickers:
        e.clear()
        histData(tickers.index(ticker),usTechStk(ticker),'6 M', '1 day')
        e.wait()
        # time.sleep(10) 
         
    for ticker in tickers:
        try:
            df = dataDataframe(app,tickers,ticker)
            hv=calc_historical_volatility(df)
            iv=calc_implied_volatility(df,hv)
            app.stocksIv[ticker]=iv	 
        except:
            # print(f'Error Stociv {ticker}')
            logger.debug(f'Error Stociv {ticker}')


    if len(app.stocksIv)==len(tickers):
        # print('3. Success(StocksIV)')
        logger.debug('3. Success(StocksIV)')
    else:
        # print('3. Error(StocksIV)')
        logger.debug('3. Error(StocksIV)')
    
    
    