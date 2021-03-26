try:
    import PySimpleGUI as sg
except ImportError as ex:
    print("Install PySimpleGUI. Exception:", str(ex))
    exit(1)

from FinancialYear import SelectFinancialYear
from Database import Database
from helpers import getFinancialYearDate
from Symbols import SelectSymbol


class EditLiveSymbols:
    def __init__(self, db = None):
        self.db : Database = db
        if self.db is None:
            self.db = Database()

        self.w : sg.Window = None
        self.sym : SelectSymbol = None
        self.newWindow()

    def selectSym(self):
        sym = SelectSymbol()
        if len(sym.getID()) == 32:
            self.sym = sym
            return True

        return False

    def closeWindow(self):
        if self.w is not None:
            self.w.close()
            self.w = None


    def newWindow(self):
        self.closeWindow()

        if self.sym is None:
            if not self.selectSym():
                return

        driver_string = "{}:{}".format(self.sym.getExchange(), self.sym.getCompany())
        try:
            driver_string = driver_string.replace(" ", "")
        except:
            pass

        try:
            allsym = self.db.getAllLiveSymbols()
            driver_string = allsym[self.sym.getID()]
        except:
            pass


        layout = [
            [sg.Text("ID:"), sg.InputText(default_text=self.sym.getID(), readonly=True, key="ID"), sg.Button("Change Symbol", key="CHANGESYMBOL")],
            [sg.Text(self.sym.getExchange(), size=(5,1)), sg.Text(self.sym.getCompany(), size=(32,1))],
            [sg.Text("DRIVER:"),
             sg.InputText(default_text=driver_string, size=(64,1), key="DRIVER")],
            [sg.Button("SAVE"), sg.Button("DELETE"), sg.Button("EXIT")]
        ]

        self.w = sg.Window(title="Live Symbols", layout=layout)

        while True:
            event, values = self.w.read()

            if event == sg.WIN_CLOSED:
                break
            elif event == "EXIT":
                break
            elif event == "CHANGESYMBOL":
                if self.selectSym():
                    self.newWindow()
                    break
                else:
                    sg.PopupOK("Invalid Symbol or No Symbol Selected\nLast Symbol will be used")
            elif event == "DELETE":
                val = sg.PopupYesNo("#{} {}:{} will be DELETED.\nConfirm?".format(self.sym.getID(), self.sym.getExchange(), self.sym.getCompany()))
                if "y" in val.lower():
                    if self.db.deleteLiveSymbol(self.sym.getID()):
                        sg.PopupOK("#{} {}:{} will be DELETED".format(self.sym.getID(), self.sym.getExchange(), self.sym.getCompany()))
                    else:
                        sg.PopupOK("#{} {}:{} cannot be DELETED".format(self.sym.getID(), self.sym.getExchange(), self.sym.getCompany()))
                    self.newWindow()
                    break
            elif event == "SAVE":
                _id = values["ID"]
                _driver = values["DRIVER"]

                val = sg.PopupYesNo("#{} {}:{} => {} will be SAVED.\nConfirm?".format(_id, self.sym.getExchange(), self.sym.getCompany(), _driver))
                if "y" in val.lower():
                    if self.db.saveLiveSymbol(id=_id, driver=_driver):
                        sg.PopupOK("#{} {}:{} => {} was UPDATED".format(_id, self.sym.getExchange(), self.sym.getCompany(), _driver))
                    else:
                        sg.PopupOK("#{} {}:{} => {} cannot be UPDATED".format(_id, self.sym.getExchange(), self.sym.getCompany(), _driver))
                    self.newWindow()
                    break

        self.closeWindow()

def main():
    EditLiveSymbols()

if __name__ == "__main__":
    main()

