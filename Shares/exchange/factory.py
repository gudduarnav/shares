import exchange.IndiaMarket as IndiaMarket
import exchange.exchangedriver as exchangedriver
from exchange.googlequote import GoogleQuote

def createExchange(exchange, name):
    if exchange.upper() == "NSE":
        return IndiaMarket.NSEMarket(symbol=name)
    elif exchange.upper() == "BSE":
        return IndiaMarket.BSEMarket(symbol=name)
    else:
        #return exchangedriver.ExchangeDriver(symbol=name)
        return GoogleQuote(symbol="{}:{}".format(exchange, name))

def createExchangeFromString(s:str):
    s1 = ["", ""]
    driver= exchangedriver.ExchangeDriver(symbol="INVALID")

    if s is not None:
        s1 = s.strip().split(":")
        if len(s1)==2:
            driver = createExchange(s1[0], s1[1])

    return driver
