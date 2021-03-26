try:
    import PySimpleGUI as sg
except ImportError as ex:
    print("Install PySimpleGUI. Exception:", str(ex))
    exit(1)

from FinancialYear import SelectFinancialYear
from Database import Database
from datetime import datetime

class HoldingNow:
    def __init__(self, db = None):
        if db is None:
            db = Database()

        self.db: Database = db
        self.w: sg.Window = None
        self.newWindow()


    def closeWindow(self):
        if self.w is not None:
            self.w.close()
            self.w = None

    def newWindow(self):
        self.closeWindow()

        holdings = self.db.getTotalHoldingbySymbol()

        l = list()

        total_buyqty = 0
        total_sellqty = 0
        total_buyamt = 0.0
        total_sellamt = 0.0
        total_divamt = 0.0
        total_holding_amt_noprofit = 0.0

        for key, values in holdings.items():
            id = key
            exchange = values["exchange"]
            name = values["name"]
            buyqty = values["buyqty"]
            buyamt = values["buyamount"]
            sellqty = values["sellqty"]
            sellamt = values["sellamount"]
            divamt = values["divamount"]

            total_buyqty = total_buyqty + buyqty
            total_sellqty = total_sellqty + sellqty
            total_buyamt = total_buyamt + buyamt
            total_sellamt = total_sellamt + sellamt
            total_divamt = total_divamt + divamt

            holding_qty = buyqty - sellqty
            holding_amt = buyamt - sellamt
            holding_amt_div = buyamt - sellamt - divamt

            holding_price = 0.0
            holding_price_div = 0.0

            try:
                if holding_qty == 0:
                    holding_price = -sellamt/sellqty
                else:
                    holding_price = holding_amt / holding_qty
            except:
                pass

            try:
                if holding_qty == 0:
                    holding_price_div = -(sellamt+divamt)/sellqty
                else:
                    holding_price_div = holding_amt_div / holding_qty
            except:
                pass

            holding_amount_noprofit = 0.0
            holding_price_noprofit = 0.0
            try:
                holding_amount_noprofit = buyamt - sellqty * buyamt / buyqty
                if buyamt == sellamt:
                    holding_price_noprofit = holding_amount_noprofit
                else:
                    holding_price_noprofit = holding_amount_noprofit / holding_qty
            except:
                pass

            total_holding_amt_noprofit = total_holding_amt_noprofit + holding_amount_noprofit

            l.append(
                [
                    id, exchange, name, holding_qty,
                    round(holding_price,2), round(holding_amt,2),
                    round(holding_price_div,2), round(holding_amt_div,2),
                    round(holding_price_noprofit, 2), round(holding_amount_noprofit, 2)
                ]
            )

        total_holding_qty = total_buyqty - total_sellqty
        total_holding_amt = total_buyamt - total_sellamt
        total_holding_amt_div = total_buyamt - total_sellamt - total_divamt
        total_holding_price = 0.0
        total_holding_price_div = 0.0
        try:
            if total_holding_qty == 0:
                total_holding_price = total_holding_amt
            else:
                total_holding_price = total_holding_amt / total_holding_qty
        except:
            pass

        try:
            if total_holding_qty == 0:
                total_holding_price_div = total_holding_amt_div
            else:
                total_holding_price_div = total_holding_amt_div / total_holding_qty
        except:
            pass


        total_holding_price_noprofit = 0.0
        try:
            if total_holding_qty == 0:
                total_holding_price_noprofit = total_holding_amt_noprofit
            else:
                total_holding_price_noprofit = total_holding_amt_noprofit / total_holding_qty
        except:
            pass



        l.append(
            [
                "", "", "TOTAL:", total_holding_qty,
                round(total_holding_price,2), round(total_holding_amt,2),
                round(total_holding_price_div,2), round(total_holding_amt_div,2),
                round(total_holding_price_noprofit, 2), round(total_holding_amt_noprofit, 2)
            ]
        )


        layout = [
            [sg.Table(values=l, headings=[
                "ID", "Exchange", "Company",
                "Holding QTY",
                "Price", "Amount",
                "Price (with Div)", "Amount (with Div)",
                "Holding Price", "Holding AMT"],
                      auto_size_columns=True, select_mode=None, display_row_numbers=True,
                      vertical_scroll_only= False,
                      key="__TABLE__")]
        ]

        self.w = sg.Window(title="Holding TODAY {}".format(datetime.now()), layout=layout, size=(1320, 700), auto_size_text=True,
                           finalize=True)
        self.w["__TABLE__"].expand(True, True)
        self.w["__TABLE__"].table_frame.pack(expand=True, fill="both")
        while True:
            event, values = self.w.read()
            if event == sg.WIN_CLOSED :
                break

        self.closeWindow()



def main():
    HoldingNow()

if __name__=="__main__":
    main()
