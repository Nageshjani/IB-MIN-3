import threading
from client.contracts.myContracts import specificOpt,usTechStk
import time
from settings import RECORDS_DIR, logger, TZ





streaming_event = threading.Event()
def streamStockLtp(app,tickers):
    # print('inside sstreamStockLtp')
    logger.debug('inside sstreamStockLtp')
    
    for ticker in tickers:
        # streaming_event.clear()  
        try:  
            app.reqMktData(reqId=tickers.index(ticker), 
                                contract=usTechStk(ticker),
                                genericTickList="",
                                snapshot=False,
                                regulatorySnapshot=False,
                                mktDataOptions=[])
            time.sleep(2)
        except:
            #  print(f'Error (streamLtp) reqId:{tickers.index(ticker)}')
             logger.debug(f'Error (streamLtp) reqId:{tickers.index(ticker)}')
        
        # streaming_event.wait()
        time.sleep(2)


    # print(app.underlyingPrice)
    if len(tickers)==len(app.underlyingPrice):
        # print('2. Success(LTP) ')
        logger.debug('2. Success(LTP) ')
    else:
        l1=list(app.underlyingPrice.keys())
        l2=tickers
        result = [x for x in l2 if x not in l1]
        # print('2. Success(LTP) ')
        # print('2. Missing Ltps : ',result)
        logger.debug('2. Success(LTP) ')
        logger.debug(f'2. Missing Ltps : {result}')





# greeks_event = threading.Event()
def streamOptChain(app):
        # print('inside streamOptChain')
        while True:
            opt_symbols=app.options
            try:
                for opt in opt_symbols:
                        # greeks_event.clear()
                        # print(500+opt_symbols.index(opt))
                        try:
                             
                            app.reqMktData(reqId=500+opt_symbols.index(opt), 
                                        contract=specificOpt(opt),
                                        genericTickList="106",
                                        snapshot=False,
                                        regulatorySnapshot=False,
                                        mktDataOptions=[])
                            # greeks_event.wait() 
                            # app.stop_streaming(500+opt_symbols.index(opt))
                            time.sleep(1)
                        
                        except:
                            #  print(f'Error: (streamOptChain) reqId :  {500+opt_symbols.index(opt)}')
                             logger.debug(f'Error: (streamOptChain) reqId :  {500+opt_symbols.index(opt)}')
            except:
                #  print('Error (streamOptChain)')
                 logger.debug('Error (streamOptChain)')
            
           
            time.sleep(300)








stream_delta_event=threading.Event()
def streamDeltas(app):
        #print('Inside StreamDeltas)
        while True:
            opt_symbols=app.optionDeltas
            if len(app.optionDeltas)>=2 and  len(app.optionDeltas)%2==0:
                try:
                    for opt in opt_symbols:
                        stream_delta_event.clear()
                        try:
                            app.reqMktData(reqId=5000+opt_symbols.index(opt), 
                                        contract=specificOpt(opt),
                                        genericTickList="106",
                                        snapshot=False,
                                        regulatorySnapshot=False,
                                        mktDataOptions=[])
            
                            stream_delta_event.wait()
                            app.stop_streaming(5000+opt_symbols.index(opt))
                        except:
                            #  print(f'Error: (streamDeltas) reqId :  {5000+opt_symbols.index(opt)}')
                             logger.debug(f'Error: (streamDeltas) reqId :  {5000+opt_symbols.index(opt)}')
                except:
                    #  print('Error (streamDeltas)')
                     logger.debug('Error (streamDeltas)')

                     
            #print('Main Greek',app.greekMain)
            if len(app.optionDeltas)==(len(app.tickers)):
                 break

            time.sleep(30)
        
        
        
        opt_symbols=app.optionDeltas
        def f():
            for opt in opt_symbols:
                try:
                    app.reqMktData(reqId=5000+opt_symbols.index(opt), 
                                contract=specificOpt(opt),
                                genericTickList="106",
                                snapshot=False,
                                regulatorySnapshot=False,
                                mktDataOptions=[])

                    
                    time.sleep(2)
                except:
                    logger.debug(f'Error: (streamDeltas) reqId :  {5000+opt_symbols.index(opt)}')
        f()
        


stream_bid_event=threading.Event()
def streamBid(app):
        
    while True:
        # print('Inside streambidask')
        
        opt_symbols=app.optionDeltas
        if len(app.optionDeltas)>=2 and  len(app.optionDeltas)%2==0:
            for opt in opt_symbols:
                    stream_bid_event.clear()
                    try:
                            
                        app.reqMktData(reqId=1000+opt_symbols.index(opt), 
                                    contract=specificOpt(opt),
                                    genericTickList="",
                                    snapshot=False,
                                    regulatorySnapshot=False,
                                    mktDataOptions=[])
        
                        stream_bid_event.wait()
                        app.stop_streaming(1000+opt_symbols.index(opt))
                    except:
                            logger.debug(f'Error: (streamBid) reqId :  {1000+opt_symbols.index(opt)}')
                            
        if len(app.optionDeltas)==(len(app.tickers)):
                 break
  
        time.sleep(20)
    
    
    opt_symbols=app.optionDeltas
    def f():
        for opt in opt_symbols:
                try:
                    app.reqMktData(reqId=1000+opt_symbols.index(opt), 
                                contract=specificOpt(opt),
                                genericTickList="",
                                snapshot=False,
                                regulatorySnapshot=False,
                                mktDataOptions=[])
                    time.sleep(2)
                except:
                    logger.debug(f'Error: (streamBid) reqId :  {1000+opt_symbols.index(opt)}')
    f()
                            







# 20/S
stream_ask_event=threading.Event()
def streamAsk(app):
        
        while True:
           
            opt_symbols=app.optionDeltas
            if len(app.optionDeltas)>=2 and len(app.optionDeltas)%2==0:
                for opt in opt_symbols:
                        try:
                            stream_ask_event.clear()
                            app.reqMktData(reqId=1100+opt_symbols.index(opt), 
                                        contract=specificOpt(opt),
                                        genericTickList="",
                                        snapshot=False,
                                        regulatorySnapshot=False,
                                        mktDataOptions=[])
            
                            stream_ask_event.wait()
                            app.stop_streaming(1100+opt_symbols.index(opt))
                        except:
                            logger.debug(f'Error: (streamAsk) reqId :  {1100+opt_symbols.index(opt)}')
                

            if len(app.optionDeltas)==(len(app.tickers)):
                 break
            time.sleep(20)
        
        opt_symbols=app.optionDeltas
        def f():
                for opt in opt_symbols:
                    try:   
                        app.reqMktData(reqId=1100+opt_symbols.index(opt), 
                                    contract=specificOpt(opt),
                                    genericTickList="",
                                    snapshot=False,
                                    regulatorySnapshot=False,
                                    mktDataOptions=[])
                        time.sleep(2)
                    except:
                         logger.debug(f'Error: (streamAsk) reqId :  {1100+opt_symbols.index(opt)}')
                                 
        f()