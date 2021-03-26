try:
    import PySimpleGUI as sg
except ImportError as ex:
    print("Install PySimpleGUI. Exception:", str(ex))
    exit(1)

from Database import Database

class EditSymbols:
    def __init__(self, db:Database=None, symbolid=None, prev = None):
        self.exited = False
        if prev is not None:
            self.exited = prev.isExit()
        if self.exited:
            print("Skipped symbol", symbolid)
            return

        if db is None:
            db = Database()

        if symbolid is None:
            return

        self.id = symbolid
        self.db = db
        self.w:sg.Window = None

        self.symList = self.db.getAllSymbols()
        if self.id not in self.symList.keys():
            print("ERROR", self.id, "not in", self.symList.keys())
            return

        self.newWindow()

    def closeWindow(self):
        if self.w is not None:
            self.w.close()
            self.w = None

    def newWindow(self):
        self.closeWindow()

        thisSym = self.symList[self.id]

        layout = [
            [sg.Text("ID:"), sg.Text(self.id, size=(32,1))],
            [sg.Text(thisSym[0], size=(5,1)), sg.Text(thisSym[1], size=(32,1))],
            [sg.Text("Change Exchange:"),
             sg.DropDown(values=self.db.getExchangeList(), default_value=thisSym[0], size=(5,1), readonly=True, key="__NEWEXCHANGE__")],
            [sg.Text("Change Name:"), sg.InputText(default_text=thisSym[1], size=(32,1), key="__NEWNAME__")],
            [sg.Button("Update"), sg.Button("Delete"), sg.Button("Skip"), sg.Button("Exit")]
        ]

        self.w = sg.Window(title="Update Symbol", layout=layout, size=(400,150))

        while True:
            event, values = self.w.read()

            if event == sg.WIN_CLOSED:
                break
            elif event == "Update":
                if self.onUpdate(newexchange=values["__NEWEXCHANGE__"], newname=values["__NEWNAME__"]):
                    break
            elif event == "Delete":
                if self.onDelete():
                    break
            elif event == "Skip":
                break
            elif event == "Exit":
                self.exited = True
                break

        self.closeWindow()


    def isExit(self):
        return self.exited

    def onUpdate(self, newexchange, newname):
        if self.id is None:
            return True

        try:
            layout = [
                [ sg.Text("ID:"), sg.Text(self.id, size=(32,1))],
                [ sg.Text(self.symList[self.id][0], size=(5,1)),
                  sg.Text(self.symList[self.id][1], size=(32,1))],
                [sg.Text("will be changed to")],
                [sg.Text(newexchange, size=(5, 1)),
                 sg.Text(newname, size=(32, 1))],
                [sg.Text("Confirm Delete (YES/NO)?")],
                [sg.Button("YES"), sg.Button("NO")]
            ]
            w = sg.Window(title="Confirm Delete of Symbol {}".format(self.id),
                          layout=layout)

            while True:
                event, values = w.read()
                if event == sg.WIN_CLOSED or event == "NO":
                    w.close()
                    return False
                elif event == "YES":
                    self.db.updateSymbol(self.id, newexchange, newname)
                    w.close()
                    sg.PopupOK("Symbol updated SUCCESSFULLY")
                    return True
        except Exception as ex:
            sg.PopupOK("ERROR during SYMBOL UPDATE:", str(ex))
            return False

        return True

    def onDelete(self):
        if self.id is None:
            return True

        layout = [
            [ sg.Text("ID:"), sg.Text(self.id, size=(32,1))],
            [ sg.Text(self.symList[self.id][0], size=(5,1)),
              sg.Text(self.symList[self.id][1], size=(32,1))],
            [sg.Text("Confirm Delete (YES/NO)?")],
            [sg.Button("YES"), sg.Button("NO")]
        ]
        w = sg.Window(title="Confirm Delete of Symbol {}".format(self.id),
                      layout=layout)

        while True:
            event, values = w.read()
            if event == sg.WIN_CLOSED or event == "NO":
                w.close()
                return False
            elif event == "YES":
                self.db.deleteSymbol(id= self.id)
                w.close()
                sg.PopupOK("Symbol deleted SUCCESSFULLY")
                return True

        return True