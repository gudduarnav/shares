from exchange.factory import createExchangeFromString

from time import sleep
from datetime import datetime


n = createExchangeFromString("NSE:AXISBANK")
#n = createExchangeFromString("BSE:532215")
#n = createExchange("BSE", "532215")
#n = ind.NSEMarket(symbol="AXISBANK")

#n = ind.BSEMarket(symbol="532215")

while True:
    if n.updatePrices():
        print(datetime.now(),
              "buy=", round(n.getBuyPrice(),2),
              "sell=",round(n.getSellPrice(),2),
              "Ave=", round(n.getAvePrice(),2))
    sleep(5)