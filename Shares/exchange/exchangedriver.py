# root class for querying exchange rate

class ExchangeDriver:
    def __init__(self, symbol):
        self.symbol = symbol

    def getSymbol(self):
        return self.symbol

    def __str__(self):
        return self.symbol

    # return True if prices are updated
    # False means error
    def updatePrices(self):
        return True

    # return Buy price
    def getBuyPrice(self):
        return 0.0

    # Return Sell price
    def getSellPrice(self):
        return 0.0

    # Return Average Price
    def getAvePrice(self):
        return 0.0

