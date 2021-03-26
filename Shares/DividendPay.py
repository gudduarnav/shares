try:
    import PySimpleGUI as sg
except ImportError as ex:
    print("Install PySimpleGUI. Exception:", str(ex))
    exit(1)

from Database import Database
from Symbols import SelectSymbol
from datetime import datetime

class DividendPayments:
    def __init__(self, db=None):
        if db is None:
            db = Database()

        self.db = db
        self.w = None
        self.sym = None
        self.newWindow()


    def closeWindow(self):
        if self.w is not None:
            self.w.close()
            self.w = None

    def newWindow(self):
        self.closeWindow()

        if self.sym is None:
            self.sym = SelectSymbol()

        now = datetime.now()
        if self.sym.getID() is None:
            return
        elif len(self.sym.getID()) != 32:
            return

        layout = [
            [sg.Text(self.sym.getExchange(), size=(5,1)), sg.Text(self.sym.getCompany(), size=(32,1))],
            [sg.Text("ID:"), sg.InputText(default_text=self.sym.getID(), readonly=True, size=(32,1)),
             sg.Button("Change Symbol", key="__CHANGE__")],
            [sg.Text("Date:"),
             sg.InputText(default_text="{:02}".format(now.day), size=(2,1), key="__DD__"), sg.Text("/"),
             sg.InputText(default_text="{:02}".format(now.month), size=(2,1), key="__MM__"), sg.Text("/"),
             sg.InputText(default_text="{:04}".format(now.year), size=(4,1), key="__YY__")],
            [sg.Text("Remarks:"), sg.InputText(default_text="", size=(64,1), key="__REMARKS__")],
            [sg.Text("Amount:"), sg.InputText(default_text="", size=(10,1), key="__AMOUNT__")],
            [sg.Text("Total Dividend:"), sg.InputText(default_text="{}".format(self.db.getDividendForThisYear()), size=(10,1), readonly=True, key="__TOTAL__")],
            [sg.Button("SAVE"), sg.Button("EXIT")]
        ]

        self.w = sg.Window(title="DIVIDEND PAYMENTS", layout=layout)

        while True:
            event, values = self.w.read()

            if event == "EXIT" or event == sg.WIN_CLOSED:
                break
            elif event == "SAVE":
                self.saveEntry(event, values)
                self.newWindow()
                break
            elif event == "__CHANGE__":
                sym1 = SelectSymbol()
                if len(sym1.getID()) == 32:
                    self.sym = sym1
                    self.newWindow()
                    break

        self.w.close()


    def saveEntry(self, event, values):
        _exchange = self.sym.getExchange()
        _company = self.sym.getCompany()
        _id = self.sym.getID()

        dd = 0
        mm = 0
        yy = 0

        try:
            dd = int(values["__DD__"])
            mm = int(values["__MM__"])
            yy = int(values["__YY__"])
        except:
            pass

        remarks = values["__REMARKS__"]

        amt = 0
        try:
            amt = float(values["__AMOUNT__"])
        except:
            pass


        total_prev = self.db.getDividendForThisYear()
        total_new = total_prev + amt
        profit_percent = 0
        try:
            profit_percent = (total_new-total_prev)*100.0/total_prev
        except:
            pass

        remarks = values["__REMARKS__"]


        if len(_id) != 32:
            sg.PopupOK("Invalid ID", title="Dividend Invalid Symbol", keep_on_top=True)
            return

        if dd<1 or dd>31 or mm<1 or mm>12 or yy<1 or yy>(datetime.now().year+1):
            sg.PopupOK("Date is Not VALID", title="Dividend Date Invalid", keep_on_top=True)

        if amt <= 0.0:
            sg.PopupOK("Amount is ZERO", title="Dividend Zero", keep_on_top=True)

        layout = [
            [sg.Text(_exchange, size=(5,1)), sg.Text(_company, size=(32,1))],
            [sg.Text("ID:"), sg.Text(_id, size=(32,1))],
            [sg.Text("DATE:"), sg.Text("{:02}/{:02}/{:04}".format(dd, mm, yy))],
            [sg.Text("REMARKS:"), sg.Text(remarks)],
            [sg.Text("Dividend Amount:"), sg.Text(str(amt), size=(10,1))],
            [sg.Text("Previous Total:"), sg.Text(str(total_prev), size=(10,1))],
            [sg.Text("Final Total:"), sg.Text(str(total_new), size=(10,1))],
            [sg.Text("Profit Percent:"), sg.Text(str(profit_percent), size=(10,1))],
            [sg.Button("YES"), sg.Button("NO")]
        ]

        w = sg.Window(title="CONFIRM DIVIDEND?", layout=layout)
        while True:
            ev, val = w.read()
            if ev == "NO" or ev == sg.WIN_CLOSED:
                break
            elif ev == "YES":
                _transid = self.db.addDividend(dd,mm,yy,_id, remarks, amt)
                if _transid is None:
                    sg.PopupOK("Cannot Save the dividend entry", "DIVIDEND ENTRY FAILED")
                else:
                    sg.PopupOK("Dividend entry saved\nTransaction ID: {}".format(_transid), title="DIVIDEND ENTRY SAVED")
                break
        w.close()






def main():
    DividendPayments()

if __name__=="__main__":
    main()