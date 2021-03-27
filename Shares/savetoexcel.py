try:
    from xlwt import Workbook
except ImportError as __ex:
    print("Install xlwt. Exception:", str(__ex))
    exit(1)

try:
    import PySimpleGUI as sg
except ImportError as __ex:
    print("Install PySimpleGUI. Exception:", str(__ex))
    exit(1)


from Database import Database
import os
from datetime import datetime
from EditTransaction import SelectDate

outputDir = "./output/"

def setOutputDir(dirName):
    global outputDir
    outputDir = dirName


def getOutputDir():
    global outputDir
    if os.path.isdir(outputDir):
        return outputDir

    try:
        os.mkdir(outputDir)
    except Exception as ex:
        print("Exception during create of output directory:", str(ex))
        exit(1)

    if os.path.isdir(outputDir):
        return outputDir


def checkFilename(filename):
    fname = "{}/{}".format(getOutputDir(), filename)
    return fname



def newFilename(pre, ext):
    now = datetime.now()
    tformat = now.strftime("%Y%m%d%H%M%S%f")
    return checkFilename("{}{}.{}".format(
                         pre,
                         tformat,
                         ext))


def autoFilename(ext):
    return newFilename("report_", ext)


# save between date
def saveTransactionsSelectDate(db:Database = None):
    if db is None:
        db = Database()

    seldate = SelectDate()
    startdate = seldate.getStartDate()
    stopdate = seldate.getStopDate()
    if startdate is None or stopdate is None:
        sg.PopupOK("No or INVALID date selected. Export cancelled.", title="Export Cancelled")
        return

    saveTransactionsbyDate(db,
                           startdate[0], startdate[1], startdate[2],
                           stopdate[0], stopdate[1], stopdate[2])

def saveTransactionsbyDate(db : Database,
                           startdd, startmm, startyy,
                           stopdd, stopmm, stopyy):
    if db is None:
        db = Database()

    syms = db.getAllSymbols()


    entries = db.getTransactionBetween(startdd, startmm, startyy, stopdd, stopmm, stopyy)

    wb = Workbook()

    s1 = wb.add_sheet("Transactions")

    s1.write(0,0, "DATE")
    s1.write(0,1, "TYPE")
    s1.write(0,2, "Exchange")
    s1.write(0,3, "Name")

    s1.write(0, 4, "BUY PRICE")
    s1.write(0, 5, "BUY QTY")
    s1.write(0, 6, "BUY AMOUNT")

    s1.write(0, 7, "SELL PRICE")
    s1.write(0, 8, "SELL QTY")
    s1.write(0, 9, "SELL AMOUNT")

    s1.write(0, 10, "DIVIDEND AMOUNT")

    s1.write(0, 11, "TOTAL PRICE")
    s1.write(0, 12, "TOTAL QTY")
    s1.write(0, 13, "TOTAL AMOUNT")

    s1.write(0, 14, "REMARKS")

    total_qty = 0
    total_amt = 0.0

    counter = 1
    for key, vals in syms.items():
        for entry in entries:
            if entry["symbolid"] == key:

                try:
                    yy, mm, dd = map(int, entry["transdate"].split("/"))
                    s1.write(counter, 0, "{:02}-{:02}-{:04}".format(dd, mm, yy))
                except Exception as ex:
                    print("Exception:", str(ex))

                s1.write(counter, 1, entry["type"])
                s1.write(counter, 2, entry["exchange"])
                s1.write(counter, 3, entry["name"])

                if "B" in entry["type"]:
                    s1.write(counter, 5, entry["qty"])
                    s1.write(counter, 6, round(entry["amt"],2))
                    total_amt = total_amt + entry["amt"]
                    total_qty = total_qty + entry["qty"]
                    try:
                        s1.write(counter, 4, round(entry["amt"]/entry["qty"], 2))
                    except:
                        s1.write(counter, 4, round(0, 2))
                elif "S" in entry["type"]:
                    total_amt = total_amt - entry["amt"]
                    total_qty = total_qty - entry["qty"]
                    s1.write(counter, 8, entry["qty"])
                    s1.write(counter, 9, round(entry["amt"],2))
                    try:
                        s1.write(counter, 7, round(entry["amt"]/entry["qty"], 2))
                    except:
                        s1.write(counter, 7, round(0, 2))
                elif "D" in entry["type"]:
                    total_amt = total_amt - entry["amt"]
                    s1.write(counter, 10, round(entry["amt"],2))


                s1.write(counter, 12, total_qty)
                s1.write(counter, 13, round(total_amt, 2))
                try:
                    s1.write(counter, 11, round(total_amt/total_qty, 2))
                except:
                    s1.write(counter, 11, round(0.0, 2))

                s1.write(counter, 14, entry["remarks"])
                counter = counter + 1



    filename = autoFilename(".xls")
    wb.save(filename)
    sg.PopupOK("File {} is saved successfully".format(filename), title="File Saved")



# save all transactions
def saveAllTransactions(db : Database = None):
    if db is None:
        db = Database()

    syms = db.getAllSymbols()
    entries = db.getTransactionBetween(1,1,1970, 31,12, datetime.now().year+1)

    wb = Workbook()

    s1 = wb.add_sheet("Transactions")

    s1.write(0,0, "DATE")
    s1.write(0,1, "TYPE")
    s1.write(0,2, "Exchange")
    s1.write(0,3, "Name")

    s1.write(0, 4, "BUY PRICE")
    s1.write(0, 5, "BUY QTY")
    s1.write(0, 6, "BUY AMOUNT")

    s1.write(0, 7, "SELL PRICE")
    s1.write(0, 8, "SELL QTY")
    s1.write(0, 9, "SELL AMOUNT")

    s1.write(0, 10, "DIVIDEND AMOUNT")

    s1.write(0, 11, "TOTAL PRICE")
    s1.write(0, 12, "TOTAL QTY")
    s1.write(0, 13, "TOTAL AMOUNT")

    s1.write(0, 14, "REMARKS")

    total_qty = 0
    total_amt = 0.0

    counter = 1
    for key, vals in syms.items():
        for entry in entries:
            if entry["symbolid"] == key:

                try:
                    yy, mm, dd = map(int, entry["transdate"].split("/"))
                    s1.write(counter, 0, "{:02}-{:02}-{:04}".format(dd, mm, yy))
                except Exception as ex:
                    print("Exception:", str(ex))

                s1.write(counter, 1, entry["type"])
                s1.write(counter, 2, entry["exchange"])
                s1.write(counter, 3, entry["name"])

                if "B" in entry["type"]:
                    s1.write(counter, 5, entry["qty"])
                    s1.write(counter, 6, round(entry["amt"],2))
                    total_amt = total_amt + entry["amt"]
                    total_qty = total_qty + entry["qty"]
                    try:
                        s1.write(counter, 4, round(entry["amt"]/entry["qty"], 2))
                    except:
                        s1.write(counter, 4, round(0, 2))
                elif "S" in entry["type"]:
                    total_amt = total_amt - entry["amt"]
                    total_qty = total_qty - entry["qty"]
                    s1.write(counter, 8, entry["qty"])
                    s1.write(counter, 9, round(entry["amt"],2))
                    try:
                        s1.write(counter, 7, round(entry["amt"]/entry["qty"], 2))
                    except:
                        s1.write(counter, 7, round(0, 2))
                elif "D" in entry["type"]:
                    total_amt = total_amt - entry["amt"]
                    s1.write(counter, 10, round(entry["amt"],2))


                s1.write(counter, 12, total_qty)
                s1.write(counter, 13, round(total_amt, 2))
                try:
                    s1.write(counter, 11, round(total_amt/total_qty, 2))
                except:
                    s1.write(counter, 11, round(0.0, 2))

                s1.write(counter, 14, entry["remarks"])
                counter = counter + 1



    filename = autoFilename(".xls")
    wb.save(filename)
    sg.PopupOK("File {} is saved successfully".format(filename), title="File Saved")


# save holdings to file
def saveAllHoldings(db : Database = None):
    if db is None:
        db = Database()

    wb = Workbook()

    s1 = wb.add_sheet("Holdings")

    s1.write(0,0, "Date")
    s1.write(0,1, "Exchange")
    s1.write(0,2, "Name")

    s1.write(0,3, "Buy Price")
    s1.write(0,4, "Buy QTY")
    s1.write(0,5, "Buy AMOUNT")

    s1.write(0,6, "Sell Price")
    s1.write(0,7, "Sell QTY")
    s1.write(0,8, "Sell AMOUNT")

    s1.write(0,9, "Holding Price")
    s1.write(0,10, "Holding QTY")
    s1.write(0,11, "Holding AMOUNT")

    s1.write(0, 12, "DIV Price")
    s1.write(0, 13, "DIV QTY")
    s1.write(0, 14, "DIV AMOUNT")

    s1.write(0, 15, "Holding Price DIV")
    s1.write(0, 16, "Holding QTY DIV")
    s1.write(0, 17, "Holding Amount DIV")

    entries = db.getTotalHoldingbySymbol()
    counter = 1
    for key, vals in entries.items():
        s1.write(counter, 0, datetime.now().strftime("%d-%m-%Y"))
        s1.write(counter, 1, vals["exchange"])
        s1.write(counter, 2, vals["name"])

        try:
            s1.write(counter, 3, round(vals["buyamount"]/vals["buyqty"], 2))
        except:
            s1.write(counter, 3, round(0.0, 2))

        s1.write(counter, 4, vals["buyqty"])
        s1.write(counter, 5, vals["buyamount"])

        try:
            s1.write(counter, 6, round(vals["sellamount"]/vals["sellqty"], 2))
        except:
            s1.write(counter, 6, round(0.0, 2))

        s1.write(counter, 7, vals["sellqty"])
        s1.write(counter, 8, vals["sellamount"])

        _hold_qty = vals["buyqty"] - vals["sellqty"]
        _hold_amt = vals["buyamount"] - vals["sellamount"]

        try:
            s1.write(counter, 9, round(_hold_amt/_hold_qty, 2))
        except:
            s1.write(counter, 9, round(0.0, 2))

        s1.write(counter, 10, _hold_qty)
        s1.write(counter, 11, _hold_amt)

        try:
            s1.write(counter, 12, round(vals["divamount"]/_hold_qty))
        except:
            s1.write(counter, 12, round(0.0, 2))

        s1.write(counter, 13, _hold_qty)
        s1.write(counter, 14, round(vals["divamount"],2))

        _hold_amt_div = _hold_amt - vals["divamount"]

        try:
            s1.write(counter, 15, round(_hold_amt_div/_hold_qty, 2))
        except:
            s1.write(counter, 15, round(0.0, 2))

        s1.write(counter, 16, _hold_qty)
        s1.write(counter, 17, round(_hold_amt_div, 2))

        counter = counter + 1

    filename = autoFilename(".xls")
    wb.save(filename)
    sg.PopupOK("File {} is saved successfully".format(filename), title="File Saved")






def main():
    saveTransactionsSelectDate()

if __name__ == "__main__":
    main()

