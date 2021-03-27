try:
    import PySimpleGUI as sg
except ImportError as ex:
    print("Install PySimpleGUI. Exception:", str(ex))
    exit(1)

from Database import Database
from EditTransaction import SelectDate
from datetime import datetime

# Edit Transaction
class EditRemarks:
    def __init__(self, db=None, prev=None, id=None, details=None):
        self.isexit : bool= False
        self.db : Database = db
        self.id : str= id
        self.w : sg.Window = None
        self.details = details

        if prev is not None:
            self.isexit = prev.isexit
        if self.isexit:
            return

        if id is None:
            return

        if details is None:
            return

        if self.db is None:
            self.db = Database()

        self.newWindow()

    def closeWindow(self):
        if self.w is not None:
            self.w.close()

    def newWindow(self):
        self.closeWindow()

        dd = 0
        mm = 0
        yy = 0
        try:
            yy,mm,dd = map(int, self.details["date"].split("/"))
        except:
            pass

        layout = [
            [sg.Text("ID:"),
             sg.InputText(default_text=self.id, size=(32,1), readonly=True, key="ID")],
            [sg.Text("Date:"),
             sg.InputText(default_text="{:02}/{:02}/{:02}".format(dd,mm,yy), key="DATE"),
             sg.CalendarButton(button_text="Select Date", key="SELECTDATE", format=("%d/%m/%Y"))],
            [
                sg.Text("Particulars:"),
                sg.Multiline(default_text=self.details["particulars"], autoscroll=True, size=(64, 4), key="REMARKS")
            ],
            [
                sg.Button("SAVE"),
                sg.Button("DELETE"),
                sg.Button("SKIP"),
                sg.Button("EXIT")
            ]
        ]

        self.w = sg.Window(title="Edit Remarks #{}".format(self.id), layout=layout, size=(600,200))

        while True:
            event, values = self.w.read()
            if event == sg.WIN_CLOSED:
                break
            elif event == "SKIP":
                break
            elif event == "EXIT":
                self.isexit = True
                break
            elif event == "DELETE":
                if self.db.deleteRemarks(id=values["ID"]):
                    sg.PopupOK("Remarks #{} deleted successfully.".format(values["ID"]), title="REMARKS DELETED")
                    break
                else:
                    sg.PopupOK("Remarks #{} delete failed.".format(values["ID"]), title="REMARKS DELETE FAILED")
            elif event == "SAVE":
                _id = values["ID"]
                _dd = 0
                _mm = 0
                _yy = 0
                try:
                    _dd, _mm, _yy = map(int, values["DATE"].split("/"))
                except:
                    pass
                _rem = values["REMARKS"]

                if self.db.updateRemarks(_id, _dd, _mm, _yy, _rem):
                    sg.PopupOK("Remarks #{} updated successfully.".format(values["ID"]), title="REMARKS UPDATED")
                    break
                else:
                    sg.PopupOK("Remarks #{} update failed.".format(values["ID"]), title="REMARKS UPDATE FAILED")

        self.closeWindow()

# List all remarks
class ListRemarks:
    def __init__(self, v, db=None):
        self.db : Database = db

        if self.db is None:
            self.db = Database()

        self.w : sg.Window = None

        self.start = [1, 1, 1970]
        self.stop = [31, 12, (datetime.now().year + 1)]
        if not v:
            seld = SelectDate()
            if seld.getStopDate() is None or seld.getStopDate() is None:
                return

            self.start = seld.getStartDate()
            self.stop = seld.getStopDate()

        self.newWindow()

    def closeWindow(self):
        if self.w is not None:
            self.w.close()
            self.w = None

    def newWindow(self):
        self.closeWindow()
        start = self.start
        stop =  self.stop


        entries= self.db.getRemarks(start[0], start[1], start[2],
                                    stop[0], stop[1], stop[2])
        if len(entries)<1:
            sg.PopupOK("No REMARKS/PARTICULARS FOUND", title="NO REMARKS")
            return

        print(entries)
        table_data = list()

        for keys, vals in entries.items():
            yy,mm,dd = map(int, vals["date"].split("/"))

            table_data.append([
                keys,
                "{:02}-{:02}-{:04}".format(dd,mm,yy),
                vals["particulars"]
            ])

        layout = [
            [
                sg.Table(
                    values=table_data,
                    headings=["ID", "DATE", "REMARKS"],
                    auto_size_columns=False, display_row_numbers=True,
                    vertical_scroll_only=False, bind_return_key=True,
                    key="__TABLE__", col_widths=[32,12,80],
                    row_height=60, justification='left'
                )
            ]
        ]

        self.w = sg.Window(title="REMARKS",
                      layout=layout, size=(1240, 700), auto_size_text=True, finalize=True)
        self.w["__TABLE__"].expand(True, True)
        self.w["__TABLE__"].table_frame.pack(expand=True, fill="both")
        while True:
            event, values = self.w.read()
            if event == sg.WIN_CLOSED :
                break
            elif event == "__TABLE__":
                selected = values["__TABLE__"]
                key_list = list(entries.keys())
                edit_w = None
                for selected1 in selected:
                    _id = key_list[selected1]
                    edit_w = EditRemarks(db=self.db, prev=edit_w, id = _id, details=entries[_id])

                self.newWindow()
                break

        self.closeWindow()



def main():
    ListRemarks()


if __name__ == "__main__":
    main()
