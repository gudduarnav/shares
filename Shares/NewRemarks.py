try:
    import PySimpleGUI as sg
except ImportError as ex:
    print("Install PySimpleGUI. Exception:", str(ex))
    exit(1)

from Database import Database
from datetime import datetime


class NewRemarks:
    def __init__(self, db=None):
        self.db : Database = db

        if self.db is None:
            self.db = Database()

        self.w : sg.Window = None
        self.newWindow()

    def closeWindow(self):
        if self.w is not None:
            self.w.close()
            self.w = None

    def newWindow(self):
        self.closeWindow()

        layout = [
            [sg.Text("Date:"),
             sg.InputText(default_text=datetime.now().strftime("%d/%m/%Y"), key="DATE"),
             sg.CalendarButton(button_text="Select Date", key="SELECTDATE", format=("%d/%m/%Y"))],
            [
                sg.Text("Particulars:"),
                sg.Multiline(default_text="", autoscroll=True, size=(64, 4), key="REMARKS")
            ],
            [ sg.Button("SAVE"), sg.Button("EXIT")]
        ]

        self.w = sg.Window(title="New Remarks", layout=layout)
        while True:
            event, values = self.w.read()
            if event == sg.WIN_CLOSED:
                break
            elif event == "EXIT":
                break
            elif event == "SAVE":
                try:
                    dd, mm, yy = map(int, values["DATE"].split("/"))
                    rem = values["REMARKS"]

                    if self.db.newRemarks(dd, mm, yy, rem):
                        sg.PopupOK("Remark saved successfully", title="REMARKS ADDED")
                        self.newWindow()
                        break
                    else:
                        sg.PopupOK("Remark cannot be saved", title="SAVE FAILED")
                except Exception as ex:
                    sg.PopupOK(str(ex), title="Exception")

        self.closeWindow()

def main():
    NewRemarks()


if __name__ == "__main__":
    main()

