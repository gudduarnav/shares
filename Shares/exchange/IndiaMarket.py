
from exchange.exchangedriver import ExchangeDriver

try:
    from nsetools import Nse
except ImportError as ex:
    print("Install nsetool (pip install nsetools). Exception:", str(ex))
    exit(1)

try:
    from bsedata.bse import BSE

except ImportError as ex:
    print("Install nsetool (pip install nsetools). Exception:", str(ex))
    exit(1)


import threading
import random

nse: Nse = None
bse: BSE = None


class NSEMarket(ExchangeDriver):
    def __init__(self, symbol):
        super().__init__(symbol=symbol)
        self.buy_price = 0.0
        self.sell_price = 0.0
        self.ave_price = 0.0

        self.doRun = False
        self.locking = threading.Lock()

        global nse
        if nse is None:
            nse = Nse()
            print(nse)

        self.q = None
        self.updatePrices()

    def _threadFunc(self):
        _status = False
        self.locking.acquire()
        try:
            _status = self.doRun
        finally:
            self.locking.release()

        if _status:
            return

        self.locking.acquire()
        try:
            self.doRun = True
        finally:
            self.locking.release()

        global nse

        buyamt = 0.0
        buyqty = 0.0
        sellamt = 0.0
        sellqty = 0.0
        buy_price = 0.0
        sell_price = 0.0
        ave_price = 0.0
        try:
            self.q = nse.get_quote(self.getSymbol())


            for index in range(1,6):
                buy_price = self.q["buyPrice{}".format(index)]
                buy_qty = self.q["buyQuantity{}".format(index)]
                if buy_price is not None and buy_qty is not None:
                    buyamt = buyamt + buy_qty*buy_price
                    buyqty = buyqty + buy_qty

                sell_price = self.q["sellPrice{}".format(index)]
                sell_qty = self.q["sellQuantity{}".format(index)]
                if sell_price is not None and sell_qty is not None:
                    sellamt = sellamt + sell_qty*sell_price
                    sellqty = sellqty + sell_qty

            try:
                buy_price = buyamt/buyqty
            except:
                pass

            try:
                sell_price = sellamt/sellqty
            except:
                pass

            try:
                ave_price = (buyamt+sellamt)/(buyqty+sellqty)
            except:
                pass

        except:
            pass

        self.locking.acquire()
        try:
            if buy_price is not None: self.buy_price = buy_price
            if sell_price is not None: self.sell_price = sell_price
            if ave_price is not None: self.ave_price = ave_price

            self.doRun = False
        finally:
            self.locking.release()


    def updatePrices(self):
        try:
            thread= threading.Thread(target=self._threadFunc)
            thread.start()
            return True
        except:
            return False


    def getBuyPrice(self):
        v = 0.0
        self.locking.acquire()
        try:
            v = self.buy_price
        finally:
            self.locking.release()
        return v

    def getSellPrice(self):
        v = 0.0
        self.locking.acquire()
        try:
            v = self.sell_price
        finally:
            self.locking.release()
        return v

    def getAvePrice(self):
        v = 0.0
        self.locking.acquire()
        try:
            v = self.ave_price
        finally:
            self.locking.release()
        return v


class BSEMarket(ExchangeDriver):
    def __init__(self, symbol):
        super().__init__(symbol=symbol)
        self.buy_price = 0.0
        self.sell_price = 0.0
        self.ave_price = 0.0

        self.doRun = False
        self.locking = threading.Lock()

        global bse
        if bse is None:
            bse = BSE()
            print(bse)

        self.q = None
        self.updatePrices()


    def _threadFunc(self):
        _status = False
        self.locking.acquire()
        try:
            _status = self.doRun
        finally:
            self.locking.release()

        if _status:
            return

        self.locking.acquire()
        try:
            self.doRun = True
        finally:
            self.locking.release()

        global bse

        buyamt = 0.0
        buyqty = 0.0
        sellamt = 0.0
        sellqty = 0.0
        buy_price = 0.0
        sell_price = 0.0
        ave_price = 0.0
        try:
            global bse
            self.q = bse.getQuote(self.getSymbol())
            buy_list = self.q["buy"]
            sell_list = self.q["sell"]

            for index in range(1, 6):
                buy_a = buy_list[str(index)]
                buy_price = float(buy_a["price"])
                buy_qty = float(buy_a["quantity"])
                if buy_price is not None and buy_qty is not None:
                    buyamt = buyamt + buy_qty * buy_price
                    buyqty = buyqty + buy_qty

                sell_a = sell_list[str(index)]
                sell_price = float(sell_a["price"])
                sell_qty = float(sell_a["quantity"])
                if sell_price is not None and sell_qty is not None:
                    sellamt = sellamt + sell_qty * sell_price
                    sellqty = sellqty + sell_qty


            try:
                buy_price = buyamt/buyqty
            except:
                pass

            try:
                sell_price = sellamt/sellqty
            except:
                pass

            try:
                ave_price = (buyamt+sellamt)/(buyqty+sellqty)
            except:
                pass

        except:
            pass

        self.locking.acquire()
        try:
            if buy_price is not None: self.buy_price = buy_price
            if sell_price is not None: self.sell_price = sell_price
            if ave_price is not None: self.ave_price = ave_price
            self.doRun = False
        finally:
            self.locking.release()

    def updatePrices(self):
        try:
            thread = threading.Thread(target=self._threadFunc)
            thread.start()
            return True
        except:
            return False

    def getBuyPrice(self):
        v = 0.0
        self.locking.acquire()
        try:
            v = self.buy_price
        finally:
            self.locking.release()
        return v

    def getSellPrice(self):
        v = 0.0
        self.locking.acquire()
        try:
            v = self.sell_price
        finally:
            self.locking.release()
        return v

    def getAvePrice(self):
        v = 0.0
        self.locking.acquire()
        try:
            v = self.ave_price
        finally:
            self.locking.release()
        return v
