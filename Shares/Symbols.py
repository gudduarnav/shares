from Database import Database

try:
    import PySimpleGUI as sg
except ImportError as ex:
    print("Install PySimpleGUI. Exception:", str(ex))
    exit(1)

# New Symbol
class NewSymbol:
    def __init__(self, db=None):
        self.exchange = ""
        self.company = ""

        if db is None:
            db = Database()

        layout = [
            [sg.Text("Enter Exchange Name:"), sg.Combo(["NSE", "BSE"], default_value="NSE", size=(5, 1), readonly=True)],
            [sg.Text("Enter Company Name:"), sg.InputText(default_text="",size=(32,1))],
            [sg.Button("SAVE"), sg.Button("CANCEL")]
        ]
        window = sg.Window("Create New Symbol", layout)

        while True:
            event, values = window.read()
            if event == "CANCEL" or event == sg.WIN_CLOSED:
                break
            elif event == "SAVE":
                exchange = values[0]
                company = values[1]

                if db.addSymbol(exchange, company):
                    self.exchange = exchange
                    self.company = company
                    sg.PopupOK("{} {} added successfully".format(self.exchange, self.company),
                               title="SYMBOL ADDED", keep_on_top=True)
                    break
                else:
                    sg.PopupOK("{} {} CANNOT BE ADDED.".format(self.exchange, self.company),
                              "The entry may exist or database error",
                              title="SYMBOL FAILED", keep_on_top=True)

        window.close()

    def getExchange(self):
        return self.exchange

    def getCompany(self):
        return self.company


# Select a symbol
class SelectSymbol:
    def __init__(self, db=None):
        self.exchange = ""
        self.company = ""
        self.id = ""

        if db is None:
            db = Database()

        window = self._getWindow(db)

        while True:
            event, values = window.read()

            if event == "CANCEL" or event == sg.WIN_CLOSED:
                break
            elif event == "OK":
                v = values[0].split("-")
                if len(v) == 2:
                    self.id, self.exchange, self.company = db.getIDforSymbol(exchange=v[0], company=v[1])
                    break
            elif event == "ADD NEW SYMBOL":
                NewSymbol(db)
                window.close()
                window = self._getWindow(db)

        window.close()

    def _getWindow(self, db):
        l_sym = list()


        for exc, val in db.getAllSymbols().values():
            l_sym.append("{}-{}".format(exc, val))

        layout = [
            [sg.Text("Symbol:"), sg.Combo(l_sym, readonly=True)],
            [sg.Button("OK"), sg.Button("CANCEL"), sg.Button("ADD NEW SYMBOL")]
        ]
        window = sg.Window("Select Symbol", layout)
        return window

    def getID(self):
        return self.id

    def getExchange(self):
        return self.exchange

    def getCompany(self):
        return  self.company


def main():
    #w = NewSymbol()
    w = SelectSymbol()
    print(w.getID(), w.getExchange(), w.getCompany())

if __name__ == "__main__":
    main()


