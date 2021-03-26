try:
    import PySimpleGUI as sg
except ImportError as ex:
    print("Install PySimpleGUI. Exception:", str(ex))
    exit(1)

from glob import glob
import os

selectedFilename = None


class SelectFile:
    def __init__(self, inputDir="./data"):
        self.inputDir = inputDir
        self.w : sg.Window = None
        self.filename : str = None
        self.newWindow()

    def closeWindow(self):
        if self.w is not None:
            self.w.close()
            self.w = None

    def newWindow(self):
        self.closeWindow()

        files = glob(self.inputDir+"/*.db", recursive=True)
        files = sorted(files, key=os.path.getctime, reverse=True)
        files = sorted(files, key=os.path.getmtime, reverse=True)

        files_name = list()
        for file in files:
            lname = os.path.split(file)
            files_name.append(lname[-1].replace(".db",""))

        if len(files_name) < 1:
            files_name.append("shares")

        layout = [
            [sg.Text("Database Name:"), sg.DropDown(values=files_name, default_value=files_name[0], size=(64,1), key="__FILENAME__")],
            [sg.Button("SELECT"), sg.Button("EXIT")]
        ]

        self.w = sg.Window(title="SELECT DATABASE", layout=layout, size=(600, 80))
        while True:
            event, values = self.w.read()
            if event == sg.WIN_CLOSED:
                break
            elif event == "EXIT":
                exit(1)
                break
            elif event == "SELECT":
                filename = values["__FILENAME__"]
                pathname = os.path.join(self.inputDir, filename+".db")
                if self.warnNewFile(pathname, filename):
                    self.filename = pathname
                    break
        self.closeWindow()


    def warnNewFile(self, filename, onlyname):
        if os.path.isfile(filename):
            return True

        if len(onlyname)<3:
            sg.PopupOK("Filename is INVALID")
            return False

        layout = [
            [sg.Text("Database:"), sg.Text(filename, size=(len(filename)+10,1))],
            [sg.Text("The database is NEW. Confirm creation of this new database (YES/NO)?")],
            [sg.Button("YES"), sg.Button("NO")]
        ]

        w = sg.Window(title="Confirm NEW DATABASE {}".format(filename), layout=layout, size=(600,100))

        bcreate = False
        while True:
            event, values = w.read()
            if event == sg.WIN_CLOSED:
                break
            elif event == "NO":
                break
            elif event == "YES":
                bcreate = True
                break

        w.close()
        return bcreate

    def getDatabaseFilename(self):
        return self.filename

def getDatabaseFilename():
    global selectedFilename
    if selectedFilename is not None:
        return selectedFilename

    s = SelectFile()
    selectedFilename = s.getDatabaseFilename()
    if selectedFilename is None:
        sg.PopupOK("No/INVALID Database filename selected. Program will exit")
        exit(1)

    return selectedFilename



def main():
    print(getDatabaseFilename())

if __name__=="__main__":
    main()
