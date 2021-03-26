try:
    import PySimpleGUI as sg
except ImportError as ex:
    print("Install PySimpleGUI. Exception:", str(ex))
    exit(1)

from FinancialYear import SelectFinancialYear
from Database import Database
from datetime import datetime



class SelectDate:
    def __init__(self):
        self.selected = False
        self.start_date = None
        self.stop_date = None

        now = datetime.now().date().strftime("%d/%m/%Y")

        layout = [
            [sg.Text("Start Date:"), sg.InputText(default_text=now, size=(12,1), key="START"), sg.CalendarButton("Select Start Date", format=("%d/%m/%Y"), key="STARTDATE")],
            [sg.Text("Stop Date:"), sg.InputText(default_text=now, size=(12,1), key="STOP"), sg.CalendarButton("Select Stop Date", format=("%d/%m/%Y"), key="STOPDATE")],
            [sg.Button("OK"), sg.Button("CANCEL")]
        ]

        w = sg.Window(title="Select Date Range", layout=layout)

        while True:
            event, values = w.read()
            if event == sg.WIN_CLOSED:
                break
            elif event == "OK":
                try:
                    self.start_date = list(map(int, values["START"].split("/")))
                    self.stop_date = list(map(int, values["STOP"].split("/")))
                    break
                except:
                    pass
            elif event == "CANCEL":
                break

        w.close()

    def getStartDate(self):
        return self.start_date

    def getStopDate(self):
        return self.stop_date


class EditTransaction:
    def __init__(self, db=None, prev=None, statement=None):
        self.exited = False
        self.statement = statement

        if db is None:
            db = Database()

        self.db:Database = db

        if prev is not None:
            self.exited = prev.isExit()
        if self.exited:
            return

        if self.statement is None:
            return


        price_per = 0.0
        try:
            price_per = statement["amt"]/statement["qty"]
        except:
            pass

        layout = [
            [sg.Text("Transaction ID:"),
             sg.Text(statement["id"], size=(32,1)),
             sg.Text("on"),
             sg.Text(statement["transdate"], size=(10,1), key="DATE")
             ],
            [sg.Text(statement["symbolid"], size=(32,1)),
             sg.Text(statement["exchange"], size=(5,1)),
             sg.Text(statement["name"], size=(32,1))],
            [sg.Text("Transaction Type:"), sg.Text(statement["type"], size=(5,1))],
            [sg.Text("Remarks:"), sg.Text(statement["remarks"], size=(70,1), key="REMARKS")],
            [sg.Text("Price:"), sg.Text("{}".format(round(price_per, 2))),
             sg.Text("QTY:"), sg.Text("{}".format(statement["qty"])),
             sg.Text("AMOUNT:"), sg.Text("{}".format(round(statement["amt"], 2)))],
            [sg.Button("DELETE"), sg.Button("SKIP"), sg.Button("EXIT")]
        ]

        w = sg.Window(title="Edit Transaction", layout=layout, size=(600, 200))

        while True:
            event, values = w.read()

            if event == sg.WIN_CLOSED:
                break
            elif event == "EXIT":
                self.exited = True
                break
            elif event == "SKIP":
                break
            elif event == "DELETE":
                s = "Confirm DELETE of transaction #{} on {}".format(statement["id"], statement["transdate"])
                values = sg.PopupYesNo(s)
                if "Y" in values.upper():
                    if self.db.deleteTransactionID(statement["type"], statement["id"]):
                        sg.PopupOK("Transaction #{} on {}\nDELETED SUCCESSFULLY".format(statement["id"], statement["transdate"]))
                        break

        w.close()

    def isExit(self):
        return self.exited




class ListTransactions:
    def __init__(self, db = None):
        if db is None:
            db = Database()

        self.db : Database = db
        self.w : sg.Window = None
        dates = SelectDate()
        if dates.getStartDate() is None or dates.getStopDate() is None:
            return

        self.start_date = dates.getStartDate()
        self.stop_date = dates.getStopDate()
        self.newWindow()

    def closeWindow(self):
        if self.w is not None:
            self.w.close()
            self.w = None

    def newWindow(self):
        self.closeWindow()

        l = self.db.getTransactionBetween(self.start_date[0], self.start_date[1], self.start_date[2],
                                          self.stop_date[0], self.stop_date[1], self.stop_date[2])

        table_data = list()
        if len(l) < 1:
            sg.PopupOK("NO TRANSACTIONS YET")
            return

        running_total_qty = 0
        running_total_amt = 0.0
        running_total_price = 0.0

        for row in l:
            if "B" in row["type"]:
                running_total_amt = running_total_amt + row["amt"]
                running_total_qty = running_total_qty + row["qty"]
            else:
                running_total_amt = running_total_amt - row["amt"]
                if "S" in row["type"]:
                    running_total_qty = running_total_qty - row["qty"]
            try:
                if running_total_qty == 0:
                    running_total_price = running_total_amt
                elif running_total_qty < 0:
                    running_total_price = running_total_amt/ -running_total_qty
                else:
                    running_total_price = running_total_amt/running_total_qty

            except:
                pass

            transdate = ""
            try:
                s = list(map(int, row["transdate"].split("/")))
                transdate = "{:02}/{:02}/{:04}".format(s[2], s[1], s[0])
            except:
                pass

            price_per = 0.0
            try:
                if "D" in row["type"]:
                    price_per = row["amt"]
                elif "B" in row["type"] or "S" in row["type"]:
                    if row["qty"] == 0:
                        price_per = row["amt"]
                    elif row["qty"] < 0:
                        price_per = row["amt"]/-row["qty"]
                    else:
                        price_per = row["amt"]/row["qty"]
            except:
                pass

            table_data.append(
                [
                    row["id"],
                    transdate,
                    row["type"],
                    row["exchange"],
                    row["name"],
                    row["remarks"],
                    round(price_per, 2),
                    row["qty"],
                    round(row["amt"],2),
                    round(running_total_price, 2),
                    running_total_qty,
                    round(running_total_amt, 2)

                ]
            )

        layout = [
            [sg.Table(values=table_data, headings=[
                "ID", "DATE", "TYPE", "Exchange", "Name", "Remarks",
                "PRICE", "QTY", "AMOUNT",
                "Bal. Price", "Bal. QTY", "Bal. AMT"],
                      vertical_scroll_only=False,
                      auto_size_columns=True, display_row_numbers=True,
                      bind_return_key=True,
                      key="__TABLE__")]
        ]

        self.w = sg.Window(title="Transactions between {}/{}/{} and {}/{}/{}".format(
            self.start_date[0], self.start_date[1], self.start_date[2],
            self.stop_date[0], self.stop_date[1], self.stop_date[2]
            ), layout=layout, size=(1320, 700),
                           auto_size_text=True,
                           finalize=True)
        self.w["__TABLE__"].expand(True, True)
        self.w["__TABLE__"].table_frame.pack(expand=True, fill="both")
        while True:
            event, values = self.w.read()
            if event == sg.WIN_CLOSED:
                break
            elif event == "__TABLE__":
                self.handleTable(values["__TABLE__"], l)
                self.newWindow()
                break


        self.closeWindow()

    def handleTable(self, values, statements):
        w = None
        for value in values:
            statement = statements[value]
            w = EditTransaction(db=self.db, prev=w, statement=statement)

def main():
    #s = SelectDate()
    #print("start=", s.getStartDate())
    #print("stop=", s.getStopDate())

    l = ListTransactions()


if __name__ == "__main__":
    main()



