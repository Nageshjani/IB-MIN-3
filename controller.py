from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
import threading
import time
import pandas as pd
from collections import defaultdict
from datetime import datetime
from functions.myFunctions import Contracts_Download,contract_event, findDeltas,printDeltas,countoptionChainGreeks
from functions.stocksIv import downloadStcoksIV,e
from client.streaming.streaming import streamOptChain,streamStockLtp,streamDeltas,streamBid,streamAsk
from client.streaming.streaming import streaming_event,greeks_event,stream_delta_event,stream_bid_event,stream_ask_event
from parameters import *


from settings import RECORDS_DIR, logger, TZ
 


# tickers = ["AMZN","INTC","AAPL","MSFT","JNJ","JPM","CVX","PG","MA"]

class TradingApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self,self)

        self.data = {}
        self.df_data = {}
        self.underlyingPrice = {}
        self.CALL_DELTA=DELTA
        self.PUT_DELTA=DELTA
        self.options=[]
        self.optionChainGreeks={}
        self.bidask=[]
        self.bidaskData={}
        self.optionDeltas=[]
        self.greekMain={}
        self.d_bid={}
        self.d_ask={}
        self.histData = {}
        self.stocksIv={}
        self.tickers=tickers
        
        for ticker in tickers:
            self.optionChainGreeks[ticker]=defaultdict()
            self.optionChainGreeks[ticker]['C']=defaultdict()
            self.optionChainGreeks[ticker]['P']=defaultdict()
        


    def historicalData(self, reqId, bar):
            if reqId not in self.histData:
                self.histData[reqId] = [{"Date":bar.date,"Open":bar.open,"High":bar.high,"Low":bar.low,"Close":bar.close,"Volume":bar.volume}]
            else:
                self.histData[reqId].append({"Date":bar.date,"Open":bar.open,"High":bar.high,"Low":bar.low,"Close":bar.close,"Volume":bar.volume})
    def historicalDataEnd(self, reqId: int, start: str, end: str):    
            super().historicalDataEnd(reqId, start, end)
            # print("HistoricalDataEnd. ReqId:", reqId, "from", start, "to", end)
            e.set()




    #reqId < 100:
    def tickPrice(self, reqId, tickType, price, attrib):
        super().tickPrice(reqId, tickType, price, attrib)
        # print('tickType:',tickType,'price:',price)
        if tickType == 4:
            if reqId < 100:
                    self.underlyingPrice[tickers[reqId]] = price
                    # print('wrapper price',price)
                    # streaming_event.set()  # set the event to notify that we have received the last price
                    

        if reqId>=1000 and reqId<1100: 
            if tickType == 1:
                local_symbol=self.optionDeltas[reqId-1000]
                if price:     
                        # print(reqId,'bid',price) 
                        self.d_bid[local_symbol]  =price   
                        stream_bid_event.set()  

        if reqId>=1100 and reqId<2000 :
            if tickType == 2:
                local_symbol=self.optionDeltas[reqId-1100]
                if price:     
                        # print(reqId,'ask',price) 
                        self.d_ask[local_symbol]  =price   
                        stream_ask_event.set()     
                    
    def stop_streaming(self,reqId):
        super().cancelMktData(reqId)
        #print('streaming stopped for ',reqId)            
                
        
    def error(self, reqId, errorCode: int, errorString: str, advancedOrderRejectJson = ""):
             super().error(reqId, errorCode, errorString, advancedOrderRejectJson)
             logger.debug(f'Error . Id : {reqId} ,{errorCode}, {errorString}')
             if advancedOrderRejectJson:
                 print("Error. Id:", reqId, "Code:", errorCode, "Msg:", errorString, "AdvancedOrderRejectJson:", advancedOrderRejectJson)
             else:
                 print("Error. Id:", reqId, "Code:", errorCode, "Msg:", errorString)        
    
    
    def contractDetails(self, reqId, contractDetails):
        if reqId not in self.data:
            self.data[reqId] = [{"expiry":contractDetails.contract.lastTradeDateOrContractMonth,
                                 "strike":contractDetails.contract.strike,
                                 "call/put":contractDetails.contract.right,
                                 "symbol":contractDetails.contract.localSymbol}]
        else:
            self.data[reqId].append({"expiry":contractDetails.contract.lastTradeDateOrContractMonth,
                                     "strike":contractDetails.contract.strike,
                                     "call/put":contractDetails.contract.right,
                                     "symbol":contractDetails.contract.localSymbol})
    
    def contractDetailsEnd(self, reqId):
        super().contractDetailsEnd(reqId)
        #print("ContractDetailsEnd. ReqId:", reqId)
        self.df_data[tickers[reqId]] = pd.DataFrame(self.data[reqId])
        
        # fileName=tickers[reqId]+'.csv'
        # csvFile=self.df_data[tickers[reqId]].to_csv(fileName)
        contract_event.set()
    def tickOptionComputation(self, reqId, tickType, tickAttrib,impliedVol, delta, optPrice, pvDividend,gamma, vega, theta, undPrice):
            
            super().tickOptionComputation(reqId, tickType, tickAttrib, impliedVol, delta,optPrice, pvDividend, gamma, vega, theta, undPrice)
            #print('ticktype: ',tickType,'redId: ',reqId)
            if tickType == 11: 
                if delta and impliedVol and optPrice and gamma  and vega and theta:
                            greek={'delta':delta,'impliedVol':impliedVol,'optPrice':optPrice,'gamma':gamma,'vega':vega,'theta':theta,'bid':None,'ask':None }

                            if reqId >=500 and reqId<1000:
                                    local_symbol=self.options[reqId-500]
                                    ticker=local_symbol.split()[0]
                                    right = local_symbol.split()[1][6]
                                    self.optionChainGreeks[ticker][right][local_symbol]=greek
                                    greeks_event.set()

                            if reqId>=5000 and reqId<=6000: 
                                            
                                            local_symbol=self.optionDeltas[reqId-5000]
                                            if local_symbol in  self.d_bid and local_symbol in self.d_ask:
                                                    greek['bid']=self.d_bid[local_symbol]
                                                    greek['ask']=self.d_ask[local_symbol]

                                            self.greekMain[local_symbol]=greek
                                            stream_delta_event.set()


                                        



def run():
    def websocket_con():
        app.run()
        time.sleep(3) 

    app = TradingApp()  
    app.connect(CON_ADRESS, TWS_ID, clientId=CLIENT_ID)  
    con_thread = threading.Thread(target=websocket_con, daemon=True)
    con_thread.start()

    time.sleep(3) 
    




    streamThread = threading.Thread(target=streamStockLtp, args=(app,tickers,))
    streamThread.start()
    time.sleep(3)
    

    # print('start Downloading stockIvs!')
    logger.debug('start Downloading stockIvs!')
    downloadStcoksIV(app,tickers)

    # print('start Downloading Option Contracts!')
    logger.debug('start Downloading Option Contracts!')
    Contracts_Download(app,tickers)
    # countoptionChainGreeks(app,tickers)


    # print('start Streaming optionGreeks!')
    logger.debug('start Streaming optionGreeks!')
    optGreeksStreamThread = threading.Thread(target=streamOptChain,args=(app,))
    optGreeksStreamThread.start()
    time.sleep(60) 



            
        
    findDeltasThread=threading.Thread(target=findDeltas,args=(app,tickers,)) 
    findDeltasThread.start()
    time.sleep(10)    



    options = app.optionDeltas
    streamDeltasThread = threading.Thread(target=streamDeltas,args=(app,))
    streamDeltasThread.start()
    time.sleep(10) 



                    
            
    printDeltasThread = threading.Thread(target=printDeltas,args=(app,tickers,))
    printDeltasThread.start()
    time.sleep(10) 


    

    streamBidAskThread = threading.Thread(target=streamBid,args=(app,))
    streamBidAskThread.start()
    time.sleep(3) 



                


    streamAskThread = threading.Thread(target=streamAsk,args=(app,))
    streamAskThread.start()
    time.sleep(3) 
