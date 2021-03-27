try:
    import PySimpleGUI as sg
except ImportError as ex:
    print("Install PySimpleGUI. Exception:", str(ex))
    exit(1)

from Database import Database
from BuySellOptions import BuySellOptions
from DividendPay import DividendPayments
from Holdings import  Holdings
import HoldingTotalBySymbol
import HoldingTotalBySymbolYear
import ListSymbols
import HoldingNow
import EditTransaction
import EditLiveSymbols
import ShowLiveShares
import NewRemarks
import ListRemarks
import savetoexcel


class MainClass:
    def __init__(self, db=None):
        if db is None:
            db = Database()
        self.db = db

        layout = [
            [
                sg.Button("Buy or Sell Shares", key="__BUYSELL__"),
                sg.Button("Dividend Payments", key="__DIV__")
            ],
            [
                sg.Button("Show Total Holdings", key="__TOTALHOLDINGS__")
            ],
            [
                sg.Button("Show Total Holdings by SYMBOLS", key = "__TOTALHOLDINGSSYMBOLS__"),
                sg.Button("Show Total Holdings by SYMBOLS and Financial Year", key="__TOTALHOLDINGSSYMBOLSYEAR__"),
                sg.Button("HOLDING NOW", key="__HOLDINGNOW__")
            ],
            [
                sg.Button("List/Edit Symbols", key="__EDITSYM__"),
                sg.Button("List/Edit Transactions", key="__EDITTRANS__")
            ],
            [
              sg.Text("-"*170)
            ],
            [
              sg.Button("EDIT/SAVE/UPDATE LIVE SYMBOLS", key="EDITLIVE"),
              sg.Button("LIVE UPDATE", key="LIVEVIEW")
            ],
            [
              sg.Text("-"*170)
            ],
            [
              sg.Button("New Remarks", key="NEWREMARKS"),
              sg.Button("Show All Remarks", key="SHOWREMARKSALL"),
                sg.Button("Show Remarks by DATE", key="SHOWREMARKS")
            ],
            [
              sg.Text("-"*170)
            ],
            [
              sg.Button("SAVE TO FILE: All Transactions", key="SAVEALL"),
              sg.Button("SAVE TO FILE: Transactions between date", key="SAVEDATE"),
              sg.Button("SAVE TO FILE: Holdings/Buy/Sell", key="SAVEHOLDINGS")
            ],
            [
              sg.Text("-"*170)
            ],
            [sg.Button("Exit", key="__EXIT__")]
        ]

        window = sg.Window(title="Shares and Securities", layout=layout)
        while True:
            event, values = window.read()
            if not self.handleEvent(event, values):
                break

        window.close()

    def handleEvent(self, event, values):
        if event == "__EXIT__" or event == sg.WIN_CLOSED:
            return False
        elif event == "__BUYSELL__":
            BuySellOptions(db=self.db)
            return True
        elif event == "__DIV__":
            DividendPayments(db = self.db)
            return True
        elif event == "__TOTALHOLDINGS__":
            Holdings(db = self.db)
            return True
        elif event == "__TOTALHOLDINGSSYMBOLS__":
            HoldingTotalBySymbol.HoldingTotalBySymbol(db=self.db)
            return True
        elif event == "__TOTALHOLDINGSSYMBOLSYEAR__":
            HoldingTotalBySymbolYear.HoldingTotalBySymbol(db=self.db)
            return True
        elif event == "__HOLDINGNOW__":
            HoldingNow.HoldingNow(db=self.db)
            return True
        elif event == "__EDITSYM__":
            ListSymbols.ListSymbols(db=self.db)
            return True
        elif event == "__EDITTRANS__":
            EditTransaction.ListTransactions(db=self.db)
            return True
        elif event == "EDITLIVE":
            EditLiveSymbols.EditLiveSymbols(db = self.db)
            return True
        elif event == "LIVEVIEW":
            ShowLiveShares.ShowLiveShares(db = self.db)
            return True
        elif event == "NEWREMARKS":
            NewRemarks.NewRemarks(db = self.db)
            return True
        elif event == "SHOWREMARKS":
            ListRemarks.ListRemarks(v=False, db=self.db)
            return True
        elif event == "SHOWREMARKSALL":
            ListRemarks.ListRemarks(v=True, db=self.db)
            return True
        elif event == "SAVEALL":
            savetoexcel.saveAllTransactions(db=self.db)
            return True
        elif event == "SAVEDATE":
            savetoexcel.saveTransactionsSelectDate(db=self.db)
            return True
        elif event == "SAVEHOLDINGS":
            savetoexcel.saveAllHoldings(db=self.db)
            return True
def main():
    MainClass()

if __name__ == "__main__":
    main()