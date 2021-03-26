try:
    import PySimpleGUI as sg
except ImportError as ex:
    print("Install PySimpleGUI. Exception:", str(ex))
    exit(1)

from FinancialYear import SelectFinancialYear
from Database import Database

class HoldingTotalBySymbol:
    def __init__(self, db:Database = None):
        if db is None:
            db = Database()

        self.db : Database = db

        asset = self.db.getTotalHoldingbySymbol()
        tabledata = list()
        total_buyqty = 0
        total_buyamt = 0.0

        total_sellqty = 0
        total_sellamt = 0.0

        total_divqty = 0
        total_divamt = 0.0

        for rowkey, rowvalue in asset.items():
            tablecol = [
                "", "", "",
                0.0, 0, 0.0,
                0.0, 0, 0.0,
                0.0, 0, 0.0]
            tablecol[0] = rowkey
            tablecol[1] = rowvalue["exchange"]
            tablecol[2] = rowvalue["name"]

            tablecol[4] = rowvalue["buyqty"]
            tablecol[5] = round(rowvalue["buyamount"],2)

            tablecol[7] = rowvalue["sellqty"]
            tablecol[8] = round(rowvalue["sellamount"], 2)

            tablecol[11] = round(rowvalue["divamount"], 2)

            try:
                tablecol[3] = round(tablecol[5] / tablecol[4], 2)
            except:
                pass

            try:
                tablecol[6] = round(tablecol[8]/tablecol[7], 2)
            except:
                pass

            try:
                tablecol[10] = tablecol[4] - tablecol[7]
                tablecol[9] = round(tablecol[11]/tablecol[10], 2)
            except:
                pass
            tabledata.append(tablecol)

            total_buyqty = total_buyqty + tablecol[4]
            total_buyamt = total_buyamt + tablecol[5]
            total_sellqty = total_sellqty + tablecol[7]
            total_sellamt = total_sellamt + tablecol[8]
            total_divqty = total_divqty + tablecol[10]
            total_divamt = total_divamt + tablecol[11]

        total_data = [
            "", "", "TOTAL:",
            0.0, total_buyqty, round(total_buyamt,2),
            0.0, total_sellqty, round(total_sellamt, 2),
            0.0, total_divqty, round(total_divamt, 2)
        ]

        try:
            total_data[3] = round(total_data[5]/total_data[4],2)
        except:
            pass

        try:
            total_data[6] = round(total_data[8]/total_data[7],2)
        except:
            pass

        try:
            total_data[9] = round(total_data[11]/total_data[10],2)
        except:
            pass

        tabledata.append(total_data)

        hold_data = [
            "", "", "HOLDING:",
            0.0, total_divqty, round(total_buyamt - total_sellamt, 2),
            round(total_data[6] - total_data[3], 2), total_sellqty, round((total_data[6] - total_data[3])*total_sellqty,2),
            total_data[9], total_data[10], total_data[11]
        ]

        try:
            hold_data[3] = round(hold_data[5]/hold_data[4], 2)
        except:
            pass


        tabledata.append(hold_data)

        profit_data = [
            "", "", "PROFIT:",
            round(total_data[3]-hold_data[3],2), hold_data[4], "",
            hold_data[6], hold_data[7], "",
            hold_data[9], hold_data[10], ""
        ]
        try:
            profit_data[5] = str(round(profit_data[3]*100.0/total_data[3], 2)) + "%"
        except:
            pass

        try:
            profit_data[8] = str(round(hold_data[6]*100.0/total_data[3],2)) + "%"
        except:
            pass

        try:
            profit_data[11] = str(round(total_data[11]*100.0/total_data[5],2)) + "%"
        except:
            pass

        tabledata.append(profit_data)


        layout = [
            [sg.Table(values=tabledata, headings=[
                "ID", "Exchange", "Company",
                "Buy Price", "Buy QTY", "Buy Amount",
                "Sell Price", "Sell QTY", "Sell Amount",
                "Div. Price", "Div. QTY", "Div. Amount"],
                      auto_size_columns=True, select_mode=None, display_row_numbers=True,
                      vertical_scroll_only= False,
                      key="__TABLE__")]
        ]

        w = sg.Window(title="Total Holdings by Symbols", layout=layout, size=(1240, 700), auto_size_text=True, finalize=True)
        w["__TABLE__"].expand(True, True)
        w["__TABLE__"].table_frame.pack(expand=True, fill="both")
        while True:
            event,values = w.read()
            if event == sg.WIN_CLOSED :
                break

        w.close()

def main():
    HoldingTotalBySymbol()

if __name__ == "__main__":
    main()
