try:
    import PySimpleGUI as sg
except ImportError as ex:
    print("Install PySimpleGUI. Exception:", str(ex))
    exit(1)

from Database import Database
from EditSymbols import EditSymbols

class ListSymbols:
    def __init__(self, db = None):
        if db is None:
            db = Database()

        self.db = db
        self.w: sg.Window = None

        self.newWindow()

    def closeWindow(self):
        if self.w is not None:
            self.w.close()
            self.w = None


    def newWindow(self):
        self.closeWindow()

        layout = list()
        syms = self.db.listSymbols()

        symlist = list()
        for keys, values in syms.items():
            symlist.append([keys, values["exchange"], values["name"]])

        layout.append([
            sg.Table(values=symlist, headings=["ID", "Exchange", "Company"],
                     auto_size_columns=True,  display_row_numbers=True,
                     vertical_scroll_only=False, bind_return_key=True,
                     key="__TABLE__")
        ])

        self.w = sg.Window(title="Symbol List", layout=layout, size=(800,600), auto_size_text=True, finalize=True)
        self.w["__TABLE__"].expand(True, True)
        self.w["__TABLE__"].table_frame.pack(expand=True, fill="both")

        while True:
            event, values = self.w.read()
            if event == sg.WIN_CLOSED:
                break
            elif event=="__TABLE__":
                self.handleTableRows(values["__TABLE__"], list(syms.keys()))
                self.closeWindow()
                self.newWindow()
                break

        self.closeWindow()

    def handleTableRows(self, selected_rows, ids):
        editSym = None
        for row in selected_rows:
            editSym = EditSymbols(db=self.db, symbolid=ids[row], prev=editSym)






def main():
    ListSymbols()


if __name__ == "__main__":
    main()

