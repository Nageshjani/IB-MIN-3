from ibapi.contract import Contract
from parameters import EXPIRY

#IMPORTANT: Make sure the Expiry Date and Exchange 
def usTechOpt(symbol,sec_type="OPT",currency="USD",exchange="BOX"):
    contract = Contract()
    contract.symbol = symbol
    contract.secType = sec_type
    contract.currency = currency
    contract.exchange = exchange
    contract.lastTradeDateOrContractMonth =EXPIRY
    return contract

def usTechStk(symbol,sec_type="STK",currency="USD",exchange="ISLAND"):
    contract = Contract()
    contract.symbol = symbol
    contract.secType = sec_type
    contract.currency = currency
    contract.exchange = exchange
    return contract 



def specificOpt(local_symbol,sec_type="OPT",currency="USD",exchange="BOX"):
    contract = Contract()
    contract.symbol = local_symbol.split()[0]
    contract.secType = sec_type
    contract.currency = currency
    contract.exchange = exchange
    contract.right = local_symbol.split()[1][6]
    contract.lastTradeDateOrContractMonth ="20"+ local_symbol.split()[1][:6]
    contract.strike = float(local_symbol.split()[1][7:])/1000
    return contract    



