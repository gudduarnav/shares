try:
    import PySimpleGUI as sg
except ImportError as ex:
    print("Install PySimpleGUI. Exception:", str(ex))
    exit(1)

from FinancialYear import SelectFinancialYear
from Database import Database
from helpers import getFinancialYearDate
from exchange.factory import createExchangeFromString
from time import time
from datetime import datetime

class ShowLiveShares:
    def __init__(self, db = None):
        self.db : Database = None
        if self.db is None:
            self.db = Database()

        liveSymbols = self.db.getAllLiveSymbols()
        idList = list()
        classSymbols = dict()

        max_counter = len(liveSymbols)
        print("Symbols found", max_counter)

        if len(list(liveSymbols.keys())) < 1:
            sg.PopupOK("No Symbol is AADED. Please add atleast 1 live symbol and retry")
            return

        total = self.db.getTotalHoldingbySymbol()

        table_data = list()
        for keys, vals in liveSymbols.items():
            idList.append(keys)
            classSymbols[keys] = None
            onecompany = total[keys]
            holding_qty = onecompany["buyqty"] - onecompany["sellqty"]
            holding_amt = onecompany["buyamount"] - onecompany["sellamount"]
            holding_amt_div = holding_amt - onecompany["divamount"]

            holding_price = 0.0
            holding_price_div = 0.0

            try:
                holding_price = holding_amt/holding_qty
            except:
                pass

            try:
                holding_price_div = holding_amt_div/holding_qty
            except:
                pass

            oneitem = [
                str(datetime.now()),
                onecompany["exchange"],
                onecompany["name"],
                holding_qty,
                round(holding_amt,2), round(holding_amt_div,2),
                round(holding_price, 2), round(holding_price_div, 2),
                0.0, 0.0, 0.0,
                "    ",
                0.00
            ]
            table_data.append(oneitem)


        counter = 0

        layout = [
            [sg.Table(values=table_data, headings=[
                "DATE",
                "Exchange", "Company",
                "QTY",
                "Amount", "Amount DIV",
                "Price", "Price DIV",
                "BUY PRICE", "SELL PRICE", "AVE PRICE",
                "ACTION",
                "RATIO"],
                      auto_size_columns=True, select_mode=None, display_row_numbers=True,
                      vertical_scroll_only= False,
                      key="__TABLE__")]
        ]

        w = sg.Window(title="Live Share Prices", layout=layout, size=(1320, 600), auto_size_text=True,
                           finalize=True)
        w["__TABLE__"].expand(True, True)
        w["__TABLE__"].table_frame.pack(expand=True, fill="both")

        while True:
            event, values = w.read(timeout=5)
            if event == sg.WIN_CLOSED:
                break
            else:
                presentID = idList[counter]
                presentCLASS = classSymbols[presentID]
                if presentCLASS is None:
                    classSymbols[presentID] = createExchangeFromString(liveSymbols[presentID])
                    presentCLASS = classSymbols[presentID]

                if presentCLASS is not None:
                    if presentCLASS.updatePrices():
                        last_buyprice = table_data[counter][8]
                        last_sellprice = table_data[counter][9]
                        last_aveprice = table_data[counter][10]

                        _buyprice = presentCLASS.getBuyPrice()
                        _sellprice = presentCLASS.getSellPrice()
                        _aveprice = presentCLASS.getAvePrice()

                        d_buyprice = round(abs(last_buyprice - _buyprice),2)
                        d_sellprice = round(abs(last_sellprice - _sellprice),2)
                        d_aveprice = round(abs(last_aveprice - _aveprice),2)
                        d_price = round(d_buyprice**2 + d_sellprice**2+d_aveprice**2, 2)
                        d_epsilon = 0.05
                        if d_price>d_epsilon:
                            timenow = datetime.now()
                            table_data[counter][0] = str(timenow)

                            table_data[counter][8] = round(_buyprice, 2)
                            table_data[counter][9] = round(_sellprice,2)
                            table_data[counter][10] = round(_aveprice, 2)

                            price_per = table_data[counter][6]
                            price_per_div = table_data[counter][7]

                            guess_buy_price = price_per
                            guess_sell_price = max([price_per, price_per_div])

                            if _sellprice > guess_sell_price and table_data[counter][3]>0:
                                table_data[counter][11] = "SELL"
                            elif _buyprice < guess_buy_price:
                                table_data[counter][11] = "BUY "
                            else:
                                table_data[counter][11] = "   "

                            ratio_p = table_data[counter][12]
                            try:
                                ratio_p = table_data[counter][10]/guess_sell_price
                            except:
                                pass
                            table_data[counter][12] = round(ratio_p, 2)

                            w["__TABLE__"].update(values = table_data)
                            w.TKroot.title("Live Share Prices ({})".format(timenow))

                counter =counter + 1
                counter = counter % max_counter

        w.close()





def main():
    ShowLiveShares()

if __name__ == "__main__":
    main()

