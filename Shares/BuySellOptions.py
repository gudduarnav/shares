try:
    import PySimpleGUI as sg
except ImportError as ex:
    print("Install PySimpleGUI. Exception:", str(ex))
    exit(1)

from Database import Database
from Symbols import SelectSymbol
from datetime import datetime

class BuySellOptions:
    def __init__(self,
                 db = None,
                 sym = None):
        if db is None:
            db = Database()
        if sym is None:
            sym = SelectSymbol()

        self.db = db
        self.sym = sym
        self.window : sg.Window = None

        self.__newWindow()

    def __closeWindow(self):
        if self.window is None:
            return
        self.window.close()
        self.window = None

    def __newWindow(self):
        self.__closeWindow()

        if self.sym.getID() is None:
            return

        if len(self.sym.getID()) != 32:
            return

        holdings = self.db.getHoldingBalance(symid=self.sym.getID())
        hold_qty = holdings[0]
        hold_amt = holdings[1]
        hold_price = 0.0
        try:
            hold_price = hold_amt/hold_qty
        except:
            pass

        now = datetime.now()
        layout = [
            [sg.Text("{} {}".format(self.sym.getExchange(), self.sym.getCompany()))],
            [sg.Text("ID:"), sg.InputText(default_text=self.sym.getID(), readonly=True, size=(32,1)), sg.Button("Change Symbol", key="__CHANGEID__")],
            [sg.Text("QTY:"), sg.InputText(default_text="", key="__QTY__", size=(10,1)),
             sg.Text("AMOUNT:"), sg.InputText(default_text="", key="__AMT__", size=(10,1)),
             sg.Button("PRICE", key="__CALCPRICE__"), sg.InputText(default_text="", readonly=True, key="__PRICE__", size=(10,1)),
             sg.Button("CALCULATOR", key="__CALC__")],
            [
                sg.Text("Date:"),
                sg.InputText(default_text=str(now.day),size=(2,1), key="__DD__"),
                sg.Text("/"),
                sg.InputText(default_text=str(now.month), size=(2,1), key="__MM__"),
                sg.Text("/"),
                sg.InputText(default_text=str(now.year), size=(4,1), key="__YY__")
            ],
            [sg.Text("HOLDING QTY:"), sg.InputText(default_text=str(hold_qty), key="__HOLDQTY__", size=(10,1), readonly=True),
             sg.Text("AMOUNT:"), sg.InputText(default_text=str(hold_amt), key="__HOLDAMT__", size=(10,1), readonly=True),
             sg.Text("PRICE:"), sg.InputText(default_text=str(hold_price), key="__HOLDPRICE__", size=(10,1), readonly=True)],
            [sg.Text("[IF BUY]  HOLDING QTY:"), sg.InputText(default_text="", key="__BUYHOLDQTY__", size=(10,1), readonly=True),
             sg.Text("AMOUNT:"), sg.InputText(default_text="", key="__BUYHOLDAMT__", size=(10,1), readonly=True),
             sg.Text("PRICE:"), sg.InputText(default_text="", key="__BUYHOLDPRICE__", size=(10,1), readonly=True)],
            [sg.Text("[IF SELL] HOLDING QTY:"), sg.InputText(default_text="", key="__SELLHOLDQTY__", size=(10,1), readonly=True),
             sg.Text("AMOUNT:"), sg.InputText(default_text="", key="__SELLHOLDAMT__", size=(10,1), readonly=True),
             sg.Text("PRICE:"), sg.InputText(default_text="", key="__SELLHOLDPRICE__", size=(10,1), readonly=True)],
            [sg.Button("BUY"), sg.Button("SELL"), sg.Button("EXIT"), sg.Text("", key="__STATUS__", size=(50,1))]
        ]

        self.window = sg.Window(title="Buy/Sell Equity (Shares)", layout=layout)

        self.__handleEvent(hold_qty, hold_amt)

    def __handleEvent(self, hold_qty, hold_amt):
        if self.window is None:
            return

        while True:
            event, values = self.window.read()

            if event == "EXIT" or event == sg.WIN_CLOSED:
                break
            elif event== "__CHANGEID__":
                sym1 = SelectSymbol()
                if sym1.id is None:
                    sg.PopupOK("You have not selected a Valid Symbol. So LAST SYMBOL is USED", title="INVALID SYMBOL")
                elif len(sym1.getID()) != 32:
                    sg.PopupOK("You have not selected a Valid Symbol. So LAST SYMBOL is USED", title="INVALID SYMBOL")
                else:
                    self.sym = sym1
                    self.__newWindow()
                    break
            elif event == "__CALCPRICE__":
                self.updateChangedPrice(event, values, hold_qty, hold_amt)
            elif event == "BUY":
                self.buyHolding(event,values,hold_qty, hold_amt)
                self.__newWindow()
                break
            elif event == "SELL":
                self.sellHolding(event, values, hold_qty, hold_amt)
                self.__newWindow()
                break
            elif event=="__CALC__":
                _status, _qty, _amt = self.calculator()
                if _status:
                    self.window["__QTY__"].update("{}".format(_qty))
                    self.window["__AMT__"].update("{}".format(round(_amt,2)))

        self.__closeWindow()

    def calculator(self):
        _status= False
        _amt = 0.0
        _qty = 0

        layout = [
            [sg.Text("QTY:"), sg.InputText(default_text="0", key="QTY"), sg.Button("<<-- CALCULATE --", key="BTNQTY")],
            [sg.Text("PRICE:"), sg.InputText(default_text="0.0", key="PRICE"), sg.Button("<<-- CALCULATE --", key="BTNPRICE")],
            [sg.Text("AMT:"), sg.InputText(default_text="0.0", key="AMT"), sg.Button("<<-- CALCULATE --", key="BTNAMT")],
            [sg.Button("OK"), sg.Button("CANCEL")]
        ]

        w = sg.Window(title="Calculator", layout=layout)
        while True:
            event, values = w.read()

            if event == sg.WIN_CLOSED or event == "CANCEL":
                break
            elif event == "OK":
                try:
                    _qty = int(values["QTY"])
                    _amt = float(values["AMT"])
                    _status = True
                    break
                except:
                    pass
            elif event == "BTNQTY":
                try:
                    price = float(values["PRICE"])
                    amt = float(values["AMT"])
                    qty = int(round(amt/price, 0))
                    w["QTY"].update(str(qty))
                except:
                    pass
            elif event == "BTNPRICE":
                try:
                    amt = float(values["AMT"])
                    qty = int(values["QTY"])
                    price = float(round(amt/qty, 2))
                    w["PRICE"].update(str(price))
                except:
                    pass
            elif event == "BTNAMT":
                try:
                    price = float(values["PRICE"])
                    qty = int(values["QTY"])
                    amt = float(round(price*qty, 2))
                    w["AMT"].update(str(amt))
                except:
                    pass

        w.close()

        # status, qty, amt
        return (_status, _qty, _amt)
    def updateChangedPrice(self, event, values, hold_qty, hold_amt):
        user_qty = 0
        user_amt = 0.0
        user_price = 0.0
        try:
            user_qty = int(values["__QTY__"])
        except:
            pass

        try:
            user_amt = float(values["__AMT__"])
        except:
            pass

        try:
            user_price = user_amt / user_qty
        except:
            pass


        buy_qty = hold_qty + user_qty
        buy_amt = hold_amt + user_amt
        buy_price = 0.0
        try:
            buy_price = buy_amt/buy_qty
        except:
            pass

        sell_qty = hold_qty - user_qty
        sell_amt = hold_amt - user_amt
        sell_price = 0.0
        try:
            sell_price = sell_amt / sell_qty
        except:
            pass

        self.window.Element(key="__PRICE__").Update(value="{}".format(user_price))

        self.window.Element(key="__BUYHOLDQTY__").Update(value=str(buy_qty))
        self.window.Element(key="__BUYHOLDAMT__").Update(value=str(buy_amt))
        self.window.Element(key="__BUYHOLDPRICE__").Update(value="{}".format(buy_price))

        self.window.Element(key="__SELLHOLDQTY__").Update(value=str(sell_qty))
        self.window.Element(key="__SELLHOLDAMT__").Update(value=str(sell_amt))
        self.window.Element(key="__SELLHOLDPRICE__").Update(value="{}".format(sell_price))

        if hold_qty > 0:
            self.window.Element(key="__STATUS__").Update(value="BUY and SELL allowed")
        elif hold_qty == 0:
            self.window.Element(key="__STATUS__").Update(value="BUY allowed")
        elif hold_qty < 0:
            self.window.Element(key="__STATUS__").Update(value="Negative Holding is INVALID")

    def buyHolding(self, event, values, hold_qty, hold_amt):
        symid = values[0]
        _exchange = self.sym.getExchange()
        _company = self.sym.getCompany()

        hold_price = 0.0
        try:
            hold_price = hold_amt/hold_qty
        except:
            pass


        user_qty = 0
        user_amt = 0.0
        user_price = 0.0
        try:
            user_qty = int(values["__QTY__"])
        except:
            pass

        try:
            user_amt = float(values["__AMT__"])
        except:
            pass

        try:
            user_price = user_amt / user_qty
        except:
            pass


        buy_qty = hold_qty + user_qty
        buy_amt = hold_amt + user_amt
        buy_price = 0.0


        if user_qty <= 0 or user_amt <= 0.0:
            sg.PopupOK("Number of Shares or the Amount for Buying cannot be Zero", title="INVALID BUYING OPTIONS")
            return

        try:
            buy_price = buy_amt/buy_qty
        except:
            pass

        discount_amt = hold_price - buy_price
        discount_percent = 0

        try:
            discount_percent = discount_amt * 100.0 / hold_price
        except:
            pass


        dd = 0
        mm = 0
        yy = 0
        try:
            dd = int(values["__DD__"])
            mm = int(values["__MM__"])
            yy = int(values["__YY__"])
        except:
            pass

        if (dd < 1 or dd > 31) or (mm<1 or mm > 12) or (yy<1 or yy > datetime.now().year):
            sg.PopupOK("Date Entered {}-{}-{} is INVALID".format(dd,mm,yy), title="INVALID BUYING DATE")
            return


        layout = [
            [sg.Text(self.sym.getExchange(), size=(5,1)), sg.Text(self.sym.getCompany(), size=(32,1))],
            [sg.Text("Symbol:"), sg.Text(symid, size=(32,1))],
            [sg.Text("{:02}/{:02}/{:04}: BUY {} shares for AMOUNT {} @ {} per share".format(dd,mm,yy,user_qty, user_amt, user_price))],
            [sg.Text("Before Buying holding was {} shares with AMOUNT {} @ {} per shares".format(hold_qty, hold_amt, hold_price))],
            [sg.Text("After Buying holding will be {} shares with AMOUNT {} @ {} per shares".format(buy_qty, buy_amt, buy_price))],
            [sg.Text("DISCOUNTED AMOUNT {}".format(discount_amt)), sg.Text("DISCOUNT Percent: {} %".format(discount_percent))],
            [sg.Text("Proceed with the BUY Option?")],
            [sg.Button("YES"), sg.Button("NO")]
        ]

        w = sg.Window(title="BUY EQUITY SHARES [Confirm]", layout=layout)

        while True:
            event, values = w.read()

            if event == sg.WIN_CLOSED or event == "NO":
                break
            elif event == "YES":
                _transid = self.db.addBuyOptions(dd,mm,yy, self.sym.getID(), user_qty, user_amt)
                if _transid is None:
                    sg.PopupOK("Cannot BUY SHARES", title="BUY FAILED")
                else:
                    sg.PopupOK("BUY SUCCESSFUL.\nTransaction ID: {}".format(_transid), title="BUY COMPLETE")
                break

        w.close()

    def sellHolding(self, event, values, hold_qty, hold_amt):
        symid = values[0]
        _exchange = self.sym.getExchange()
        _company = self.sym.getCompany()

        hold_price = 0.0
        try:
            hold_price = hold_amt/hold_qty
        except:
            pass


        user_qty = 0
        user_amt = 0.0
        user_price = 0.0
        try:
            user_qty = int(values["__QTY__"])
        except:
            pass

        try:
            user_amt = float(values["__AMT__"])
        except:
            pass

        try:
            user_price = user_amt / user_qty
        except:
            pass


        sell_qty = hold_qty - user_qty
        sell_amt = hold_amt - user_amt
        sell_price = 0.0


        if user_qty <= 0 or user_amt <= 0.0:
            sg.PopupOK("Number of Shares or the Amount for Buying cannot be Zero", title="INVALID BUYING OPTIONS")
            return

        try:
            sell_price = sell_amt/sell_qty
        except:
            pass

        profit = user_price - hold_price
        profit_percent = 0

        try:
            profit_percent = profit * 100.0 / hold_price
        except:
            pass


        dd = 0
        mm = 0
        yy = 0
        try:
            dd = int(values["__DD__"])
            mm = int(values["__MM__"])
            yy = int(values["__YY__"])
        except:
            pass

        if (dd < 1 or dd > 31) or (mm<1 or mm > 12) or (yy<1 or yy > datetime.now().year):
            sg.PopupOK("Date Entered {}-{}-{} is INVALID".format(dd,mm,yy), title="INVALID BUYING DATE")
            return


        layout = [
            [sg.Text(self.sym.getExchange(), size=(5,1)), sg.Text(self.sym.getCompany(), size=(32,1))],
            [sg.Text("Symbol:"), sg.Text(symid, size=(32,1))],
            [sg.Text("{:02}/{:02}/{:04}: SELL {} shares for AMOUNT {} @ {} per share".format(dd,mm,yy,user_qty, user_amt, user_price))],
            [sg.Text("Before Selling holding was {} shares with AMOUNT {} @ {} per shares".format(hold_qty, hold_amt, hold_price))],
            [sg.Text("After Selling holding will be {} shares with AMOUNT {} @ {} per shares".format(sell_qty, sell_amt, sell_price))],
            [sg.Text("PROFIT AMOUNT {} for {} shares @ {} per share".format(profit*user_qty, user_qty, profit)),
             sg.Text("PROFIT Percent: {} %".format(profit_percent))],
            [sg.Text("Proceed with the SELL Option?")],
            [sg.Button("YES"), sg.Button("NO")]
        ]

        w = sg.Window(title="SELL EQUITY SHARES [Confirm]", layout=layout)

        while True:
            event, values = w.read()

            if event == sg.WIN_CLOSED or event == "NO":
                break
            elif event == "YES":
                _transid = self.db.addSellOptions(dd,mm,yy, self.sym.getID(), user_qty, user_amt)
                if _transid is None:
                    sg.PopupOK("Cannot SELL SHARES", title="SELL FAILED")
                else:
                    sg.PopupOK("SELL SUCCESSFUL.\nTransaction ID: {}".format(_transid), title="SELL COMPLETE")
                break

        w.close()


def main():
    BuySellOptions()

if __name__ == "__main__":
    main()