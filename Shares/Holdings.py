try:
    import PySimpleGUI as sg
except ImportError as ex:
    print("Install PySimpleGUI. Exception:", str(ex))
    exit(1)

from FinancialYear import SelectFinancialYear
from Database import Database
from helpers import getFinancialYearDate

class Holdings:
    def __init__(self, db=None):
        if db is None:
            db = Database()

        self.db: Database = db
        self.w: sg.Window= None
        self.yr: SelectFinancialYear = None
        self.newWindow()

    def closeWindow(self):
        if self.w is not None:
            self.w.close()
            self.w = None

    def newWindow(self):
        self.closeWindow()

        total = self.db.getTotalHolding()
        buy_price = 0.0
        sell_price = 0.0

        try:
            buy_price = total[1]/total[0]
        except:
            pass

        try:
            sell_price = total[3]/total[2]
        except:
            pass

        holding_n = total[0] - total[2]
        holding_amount = total[1] - total[3]
        holding_amount_withdiv = holding_amount - total[4]

        holding_price = 0.0
        holding_price_withdiv = 0.0

        try:
            holding_price = holding_amount/holding_n
            holding_price_withdiv = holding_amount_withdiv/holding_n
        except:
            pass

        sp = total[3]
        sp_withdiv = sp + total[4]

        cp = total[2] * buy_price

        profit = sp - cp
        profit_withdiv = sp_withdiv - cp

        profit_percent = 0.0
        profit_percent_withdiv = 0.0

        try:
            profit_percent = profit * 100.0 / cp
            profit_percent_withdiv = profit_withdiv * 100.0 / cp
        except:
            pass

        layout = list()
        layout.append([
            sg.Text("TOTAL HOLDINGS:")
        ])
        layout.append([
            sg.Text("\tBUY: {} shares @ {} per share with Total Amount {}".format(total[0], buy_price, total[1]))
        ])
        layout.append([
            sg.Text("\tSELL: {} shares @ {} per share with Total Amount {}".format(total[2], sell_price, total[3]))
        ])
        layout.append([
            sg.Text("\tTotal Dividend Collected is {}".format(total[4]))
        ])

        layout.append([
            sg.Text("\tHOLDING: {} shares @ {} per share with Total Amount {}".format(holding_n, holding_price, holding_amount))
        ])

        layout.append([
            sg.Text("\t\tPROFIT: {}\t{} %".format(profit, profit_percent))
        ])

        layout.append([
            sg.Text("\tHOLDING with DIVIDEND: {} shares @ {} per share with Total Amount {}".format(holding_n, holding_price_withdiv, holding_amount_withdiv))
        ])
        layout.append([
            sg.Text("\t\tPROFIT with DIVIDEND: {}\t{} %".format(profit_withdiv, profit_percent_withdiv))
        ])
        layout.append([
            sg.Text("-"*200)
        ])

        self.addSectionLayout(layout=layout)


        layout.append([
            sg.Button("EXIT"),
            sg.Button("Select Financial Year", key="__CHANGEYEAR__")
        ])

        self.w = sg.Window(title="Holdings", layout=layout)

        while self.processEvents():
            pass

        self.closeWindow()

    def addSectionLayout(self, layout: list):
        if self.yr is None:
            return

        total = self.db.getTotalHoldingForFinancialYear(self.yr.getYear())

        buy_price = 0.0
        sell_price = 0.0

        try:
            buy_price = total[1]/total[0]
        except:
            pass

        try:
            sell_price = total[3]/total[2]
        except:
            pass

        holding_n = total[0] - total[2]
        holding_amount = total[1] - total[3]
        holding_amount_withdiv = holding_amount - total[4]

        holding_price = 0.0
        holding_price_withdiv = 0.0

        try:
            holding_price = holding_amount/holding_n
            holding_price_withdiv = holding_amount_withdiv/holding_n
        except:
            pass

        sp = total[3]
        sp_withdiv = sp + total[4]

        cp = total[2] * buy_price

        profit = sp - cp
        profit_withdiv = sp_withdiv - cp

        profit_percent = 0.0
        profit_percent_withdiv = 0.0

        try:
            profit_percent = profit * 100.0 / cp
            profit_percent_withdiv = profit_withdiv * 100.0 / cp
        except:
            pass

        yr_date = getFinancialYearDate(self.yr.getYear())

        layout.append([
            sg.Text("FINANCIAL YEAR: {} [{} - {}] HOLDINGS:".format(self.yr.getYear(), yr_date[0], yr_date[1]))
        ])

        layout.append([
            sg.Text("\tBUY: {} shares @ {} per share with Total Amount {}".format(total[0], buy_price, total[1]))
        ])
        layout.append([
            sg.Text("\tSELL: {} shares @ {} per share with Total Amount {}".format(total[2], sell_price, total[3]))
        ])
        layout.append([
            sg.Text("\tTotal Dividend Collected is {}".format(total[4]))
        ])

        layout.append([
            sg.Text("\tHOLDING: {} shares @ {} per share with Total Amount {}".format(holding_n, holding_price, holding_amount))
        ])

        layout.append([
            sg.Text("\t\tPROFIT: {}\t{} %".format(profit, profit_percent))
        ])

        layout.append([
            sg.Text("\tHOLDING with DIVIDEND: {} shares @ {} per share with Total Amount {}".format(holding_n, holding_price_withdiv, holding_amount_withdiv))
        ])
        layout.append([
            sg.Text("\t\tPROFIT with DIVIDEND: {}\t{} %".format(profit_withdiv, profit_percent_withdiv))
        ])
        layout.append([
            sg.Text("-"*200)
        ])



    def processEvents(self):
        event, values = self.w.read()

        if event == "EXIT" or event == sg.WIN_CLOSED:
            return False

        if event == "__CHANGEYEAR__":
            yr = SelectFinancialYear(self.db)
            if yr.getYear() is not None:
                if yr.getYear() > 0:
                    self.yr = yr
                    self.newWindow()
                    return False

        return True




def main():
    Holdings()

if __name__ == "__main__":
    main()
