try:
    import PySimpleGUI as sg
except ImportError as ex:
    print("Install PySimpleGUI. Exception:", str(ex))
    exit(1)


from Database import Database

class SelectFinancialYear:
    def __init__(self, db = None):
        if db is None:
            db = Database()

        self.db = db
        self.w = None
        self.year = 0
        self.newWindow()

    def closeWindow(self):
        if self.w is not None:
            self.w.close()
            self.w = None

    def newWindow(self):
        self.closeWindow()

        lYear = self.db.getFinancialYearList()
        if len(lYear) < 1:
            self.year = 0
            return

        layout = [
            [sg.Text("Financial Year:"), sg.DropDown(values=lYear, default_value=lYear[-1], size=(5, 1), readonly=True)],
            [sg.Button("SELECT"), sg.Button("CANCEL")]
        ]

        self.w = sg.Window(title="Select Financial Year", layout=layout)
        while True:
            event, values = self.w.read()
            if event=="CANCEL" or event==sg.WIN_CLOSED:
                self.year = 0
                break
            elif event=="SELECT":
                try:
                    self.year = int(values[0])
                    break
                except:
                    pass

        self.closeWindow()

    def getYear(self):
        return self.year


def main():
    f = SelectFinancialYear()
    print(f.getYear())

if __name__ == "__main__":
    main()