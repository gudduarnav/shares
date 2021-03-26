try:
    import sqlite3
except ImportError as ex:
    print("Install sqlite3. Exception: ", str(ex))
    exit(1)

import os

from hashgen import generatekey
from hashgen import timestampnow

from helpers import createSQLDate, splitSQLDate, getFinancialYearDate
import helpers
from time import sleep

from datetime import datetime
from SelectDBFile import getDatabaseFilename

class Database:
    def __init__(self, filename=None):
        if filename is None:
            filename = getDatabaseFilename()

        dir_db = os.path.split(filename)[0]
        if not os.path.isdir(dir_db):
            os.makedirs(dir_db)
        self.db = sqlite3.connect(filename)

    def checkTable(self, tablename):
        q = "SELECT count(name) FROM sqlite_master WHERE type='table' AND name='{}'".format(tablename)
        cursor = self.db.cursor()
        cursor.execute(q)
        if cursor.fetchone()[0] == 1:
            return True
        else:
            return False

    # id, exchange, company
    # symbols
    def createSymbols(self):
        tableName = "symbols"
        if self.checkTable(tableName):
            return True

        q = "create table {} (id char(32) primary key not null, exchange char(5) not null, name char(32) not null)".format(tableName)
        self.db.execute(q)
        self.commit()
        return True

    def addSymbol(self, exchange, company):
        try:
            if not self.createSymbols():
                return False

            _exchange = exchange.strip()[0:min([3, len(exchange)])].upper()
            _company = company.strip()[0:min([32, len(company)])].upper()
            q = "insert into symbols (id, exchange, name) values ('{}', '{}', '{}')".format(generatekey(_exchange+_company),
                                                                                      _exchange, _company)
            self.db.execute(q)
            self.commit()
            return True
        except:
            return False


    def getAllSymbols(self):
        l = dict()
        q = "select id, exchange, name from symbols order by exchange desc, name asc"
        if not self.createSymbols():
            return l
        cursor = self.db.execute(q)
        for row in cursor:
            l[row[0]] = (row[1], row[2])
        return l


    def findSymbols(self, exchange, company):
        _exchange = exchange.strip()[0:min([3, len(exchange)])].upper()
        _company = company.strip()[0:min([32, len(company)])].upper()
        symbols = self.getAllSymbols()

        l = dict()
        for key, val in symbols.items():
            if _exchange in val[0] and _company in val[1]:
                l[key] = val

        return l

    def getIDforSymbol(self, exchange, company):
        if not self.createSymbols():
            return ("", "", "")

        _exchange = exchange.strip()[0:min([3, len(exchange)])].upper()
        _company = company.strip()[0:min([32, len(company)])].upper()
        q = "select id, exchange, name from symbols where exchange='{}' and name='{}'".format(_exchange, _company)
        cursor = self.db.execute(q)
        for row in cursor:
            return (row[0], row[1], row[2])

        return ("", "", "")

    # id, date, exchangecompany, [B(uy)/S(ell)] action, count, amount (Rs.)
    # SHARES
    def createBuySellOptions(self):
        if not self.checkTable("sharesbuy"):
            q = "create table sharesbuy (id char(32) primary key not null, transdate date, symbolid char(32) not null, qty int, amount real)"
            self.db.execute(q)
            self.commit()

        if not self.checkTable("sharessell"):
            q = "create table sharessell (id char(32) primary key not null, transdate date, symbolid char(32) not null, qty int, amount real)"
            self.db.execute(q)
            self.commit()

        return True

    def addBuyOptions(self,
                      dd, mm, yy,
                      symbid,
                      qty, amt):
        sleep(1)
        if not self.createBuySellOptions():
            return None

        _transID = timestampnow()
        _transDate = createSQLDate(dd, mm, yy)
        q = "insert into sharesbuy (id, transdate, symbolid, qty, amount) values ('{}', '{}', '{}', {}, {})".format(
            _transID, _transDate, symbid, qty, amt
        )
        try:
            self.db.execute(q)
            self.commit()
            sleep(1)
            return _transID
        except Exception as ex:
            print("addBuyOptions() Exception:", str(ex))
            return None

    def addSellOptions(self,
                      dd, mm, yy,
                      symbid,
                      qty, amt):
        sleep(1)
        if not self.createBuySellOptions():
            return None

        _transID = timestampnow()
        _transDate = createSQLDate(dd, mm, yy)
        q = "insert into sharessell (id, transdate, symbolid, qty, amount) values ('{}', '{}', '{}', {}, {})".format(
            _transID, _transDate, symbid, qty, amt
        )
        try:
            self.db.execute(q)
            self.commit()
            sleep(1)
            return _transID
        except Exception as ex:
            print("addSellOptions() Exception:", str(ex))
            print(str(ex))
            return None


    # get total qty, amt from buy and sell
    # (buyqty, buytotalamount, sellqty, selltotalamount)
    def getHoldingEquity(self, symid):
        if not self.createBuySellOptions():
            return None

        q1 = "select sum(qty), sum(amount) from sharesbuy where symbolid='{}'".format(symid)
        q2 = "select sum(qty), sum(amount) from sharessell where symbolid='{}'".format(symid)

        try:
            r1 = self.db.execute(q1)
            r2 = self.db.execute(q2)

            buy_qty = 0
            but_amt = 0.0
            sell_qty = 0
            sell_amt = 0.0

            for r1a in r1:
                if r1a is not None:
                    if r1a[0] is not None:
                        buy_qty = r1a[0]
                    if r1a[1] is not None:
                        but_amt = r1a[1]
                break

            for r2a in r2:
                if r2a is not None:
                    if r2a[0] is not None:
                        sell_qty = r2a[0]
                    if r2a[1] is not None:
                        sell_amt = r2a[1]
                break

            return (buy_qty, but_amt, sell_qty, sell_amt)
        except Exception as ex:
            print("getHoldingEquity() Exception:", str(ex))
            print(str(ex))
            return (0, 0.0, 0, 0.0)

    # return holding balance
    # (qtyleft, amtleft)
    def getHoldingBalance(self, symid):
        r = self.getHoldingEquity(symid)
        return (r[0]-r[2], r[1]-r[3])


    # dividend
    # (id, transdate, symid, particulars, amount)
    def createDividendTable(self):
        if self.checkTable("dividend"):
            return True

        q = "create table dividend (id char(32) primary key not null, transdate date, symbolid char(32) not null, remarks char(64), amount real)"
        self.db.execute(q)
        self.commit()

        return True

    def addDividend(self,
                    dd, mm, yy,
                    symid, particulars, amount):
        sleep(1)
        if not self.createDividendTable():
            return None

        _id = timestampnow()
        _date = createSQLDate(dd, mm, yy)
        _sym  = symid
        _remarks = particulars.strip()[0:min([64, len(particulars)])]
        _amount = amount

        q = "insert into dividend (id, transdate, symbolid, remarks, amount) values ('{}','{}', '{}', '{}', {})".format(
            _id,
            _date,
            _sym,
            _remarks,
            _amount
        )
        try:
            self.db.execute(q)
            self.commit()
            sleep(1)
            return _id
        except:
            return None

    def getDividendForThisYear(self):
        if not self.createDividendTable():
            return 0.0

        now = datetime.now()

        start_date = createSQLDate(1, 4, now.year-1)
        stop_date = createSQLDate(31, 3, now.year)

        if now.month >= 4:
            start_date = createSQLDate(1, 4, now.year)
            stop_date = createSQLDate(31, 3, now.year+1)

        q = "select sum(amount) from dividend where transdate between '{}' and '{}'".format(start_date, stop_date)
        try:
            rows = self.db.execute(q)
            for row in rows:
                if row is None:
                    return 0.0
                elif row[0] is None:
                    return 0.0
                else:
                    return row[0]
        except Exception as ex:
            print("getDividendForThisYear() exception:", str(ex))
            return 0.0



    def commit(self):
        try:
            self.db.commit()
        except:
            pass

    def __del__(self):
        try:
            self.commit()
            self.db.close()
        except:
            pass

    def isSetup(self):
        if not self.createBuySellOptions() or\
           not self.createDividendTable() or\
           not self.createSymbols() or\
           not self.createLiveConnTable() or\
           not self.createRemarks():
           return False
        else:
            return True

    def getFinancialYearList(self):
        l = list()
        if not self.isSetup():
            return l

        q = """
             select distinct v from (
                select strftime("%Y",replace(transdate,"/","-")) as V from sharesbuy union all 
                select strftime("%Y",replace(transdate,"/","-")) as V from sharessell union ALL
                select strftime("%Y",replace(transdate,"/","-")) as V from dividend 
            ) order by v asc            
            """

        r = self.db.execute(q)
        for row in r:
            if row is not None:
                l.append(int(row[0]))

        if len(l) >= 1:
           l.append(min(l)-1)
           l.append(max(l)+1)
           l.sort()
        return l



    # Total Holdings
    # (buy_n, buy_amount, sell_n, sell_amount, dividend_amount)
    def getTotalHolding(self):
        if not self.isSetup():
            return (0, 0.0, 0, 0.0, 0.0)

        q = "select sum(qty), sum(amount) from sharesbuy"
        r = self.db.execute(q)
        buy_qty = 0
        buy_amount = 0.0
        for row in r:
            if row is not None:
                if row[0] is not None and row[1] is not None:
                    buy_qty = row[0]
                    buy_amount = row[1]
                    break

        q = "select sum(qty), sum(amount) from sharessell"
        r = self.db.execute(q)
        sell_qty = 0
        sell_amount = 0.0
        for row in r:
            if row is not None:
                if row[0] is not None and row[1] is not None:
                    sell_qty = row[0]
                    sell_amount = row[1]
                    break

        q = "select sum(amount) from dividend"
        r = self.db.execute(q)
        div_amount = 0.0
        for row in r:
            if row is not None:
                if row[0] is not None :
                    div_amount = row[0]

        return (buy_qty, buy_amount, sell_qty, sell_amount, div_amount)

    # Total Holdings
    # (buy_n, buy_amount, sell_n, sell_amount, dividend_amount)
    def getTotalHoldingForFinancialYear(self, year):
        if not self.isSetup():
            return (0, 0.0, 0, 0.0, 0.0)

        start_year = createSQLDate(1, 4, year)
        stop_year = createSQLDate(31, 3, year+1)

        q = "select sum(qty), sum(amount) from sharesbuy where transdate between '{}' and '{}'".format(createSQLDate(1,1,1960), stop_year)
        r = self.db.execute(q)
        buy_qty = 0
        buy_amount = 0.0
        for row in r:
            if row is not None:
                if row[0] is not None and row[1] is not None:
                    buy_qty = row[0]
                    buy_amount = row[1]
                    break

        q = "select sum(qty), sum(amount) from sharessell where transdate between '{}' and '{}'".format(createSQLDate(1,1,1960), stop_year)
        r = self.db.execute(q)
        sell_qty = 0
        sell_amount = 0.0
        for row in r:
            if row is not None:
                if row[0] is not None and row[1] is not None:
                    sell_qty = row[0]
                    sell_amount = row[1]
                    break

        q = "select sum(amount) from dividend where transdate between '{}' and '{}'".format(start_year, stop_year)
        r = self.db.execute(q)
        div_amount = 0.0
        for row in r:
            if row is not None:
                if row[0] is not None :
                    div_amount = row[0]

        return (buy_qty, buy_amount, sell_qty, sell_amount, div_amount)


    # Show Total Holding per shares
    # ["symbolid"] =(exchange, name, total_buyqty, total_buyamount, total_sellqty, total_sellamount, total_divamount)
    def getTotalHoldingbySymbol(self):
        l = dict()
        if not self.isSetup():
            return l

        q = "select id, exchange, name from symbols order by exchange desc, name asc"
        rsym = self.db.execute(q)
        for rowsym in rsym:
            sym_id = rowsym[0]
            sym_exchange = rowsym[1]
            sym_name = rowsym[2]

            q = "select sum(qty), sum(amount) from sharesbuy where symbolid='{}'".format(sym_id)
            r = self.db.execute(q)
            for row in r:
                l[sym_id] = {
                    "exchange": sym_exchange,
                    "name": sym_name,
                    "buyqty": 0 if row[0] is None else row[0],
                    "buyamount": 0.0 if row[1] is None else row[1],
                    "sellqty": 0,
                    "sellamount": 0.0,
                    "divamount": 0.0
                }

            q = "select sum(qty), sum(amount) from sharessell where symbolid='{}'".format(sym_id)
            r = self.db.execute(q)
            for row in r:
                if sym_id in l.keys():
                    l[sym_id]["sellqty"] = 0 if row[0] is None else row[0]
                    l[sym_id]["sellamount"] = 0.0 if row[1] is None else row[1]
                else:
                    l[sym_id] = {
                        "exchange": sym_exchange,
                        "name": sym_name,
                        "buyqty": 0,
                        "buyamount": 0.0,
                        "sellqty": 0 if row[0] is None else row[0],
                        "sellamount": 0.0 if row[1] is None else row[1],
                        "divamount": 0.0
                    }

            q = "select sum(amount) from dividend a where symbolid='{}'".format(sym_id)
            r = self.db.execute(q)
            for row in r:

                if sym_id in l.keys():
                    l[sym_id]["divamount"] = 0.0 if row[0] is None else row[0]
                else:
                    l[sym_id] = {
                        "exchange": sym_exchange,
                        "name": sym_name,
                        "buyqty": 0,
                        "buyamount": 0.0,
                        "sellqty": 0,
                        "sellamount": 0.0,
                        "divamount": 0.0 if row[0] is None else row[0]
                    }

        return l

    def getTotalHoldingbySymbolForYear(self, yr):
        start_date, stop_date = getFinancialYearDate(yr)
        print(start_date, stop_date)
        l = dict()
        if not self.isSetup():
            return l

        q = "select id, exchange, name from symbols order by exchange desc, name asc"
        rsym = self.db.execute(q)
        for rowsym in rsym:
            sym_id = rowsym[0]
            sym_exchange = rowsym[1]
            sym_name = rowsym[2]

            q = "select sum(qty), sum(amount) from sharesbuy where symbolid='{}' and transdate between '{}' and '{}'".format(sym_id, createSQLDate(1,1, 1970), stop_date)
            r = self.db.execute(q)
            for row in r:
                l[sym_id] = {
                    "exchange": sym_exchange,
                    "name": sym_name,
                    "buyqty": 0 if row[0] is None else row[0],
                    "buyamount": 0.0 if row[1] is None else row[1],
                    "sellqty": 0,
                    "sellamount": 0.0,
                    "divamount": 0.0
                }

            q = "select sum(qty), sum(amount) from sharessell where symbolid='{}' and transdate between '{}' and '{}'".format(sym_id, createSQLDate(1,1,1970), stop_date)
            r = self.db.execute(q)
            for row in r:
                if sym_id in l.keys():
                    l[sym_id]["sellqty"] = 0 if row[0] is None else row[0]
                    l[sym_id]["sellamount"] = 0.0 if row[1] is None else row[1]
                else:
                    l[sym_id] = {
                        "exchange": sym_exchange,
                        "name": sym_name,
                        "buyqty": 0,
                        "buyamount": 0.0,
                        "sellqty": 0 if row[0] is None else row[0],
                        "sellamount": 0.0 if row[1] is None else row[1],
                        "divamount": 0.0
                    }

            q = "select sum(amount) from dividend a where symbolid='{}' and transdate between '{}' and '{}'".format(sym_id, start_date, stop_date)
            r = self.db.execute(q)
            for row in r:

                if sym_id in l.keys():
                    l[sym_id]["divamount"] = 0.0 if row[0] is None else row[0]
                else:
                    l[sym_id] = {
                        "exchange": sym_exchange,
                        "name": sym_name,
                        "buyqty": 0,
                        "buyamount": 0.0,
                        "sellqty": 0,
                        "sellamount": 0.0,
                        "divamount": 0.0 if row[0] is None else row[0]
                    }

        return l

    # get list of symbols
    def listSymbols(self):
        l = dict()
        if not self.isSetup():
            return False

        q = "select id,exchange, name from symbols order by exchange desc, name asc"
        rows = self.db.execute(q)
        for row in rows:
            l[row[0]] = {"exchange": row[1], "name": row[2]}

        return l

    def updateSymbol(self, id, newexchange, newname):
        if id is None:
            return

        if len(id) != 32:
            print("ERROR: {} is not properly formatted".format(id))
            return

        newexchange = helpers.beautifyExchange(newexchange)
        newname = helpers.beautifyName(newname)
        newkey = generatekey(newexchange+newname)

        qlist = list()
        qlist.append("update symbols set exchange='{}', name='{}' where id='{}'".format(newexchange, newname, id))
        qlist.append("update symbols set id='{}' where exchange='{}' and name='{}'".format(newkey, newexchange, newname))
        qlist.append("update dividend set symbolid='{}' where symbolid='{}'".format(newkey, id))
        qlist.append("update sharesbuy set symbolid='{}' where symbolid='{}'".format(newkey, id))
        qlist.append("update sharessell set symbolid='{}' where symbolid='{}'".format(newkey, id))
        qlist.append("update marketcode set symbolid='{}' where symbolid='{}'".format(newkey, id))

        for q1 in qlist:
            try:
                self.db.execute(q1)
                self.db.commit()
                print("updateSymbol() Query", q1, ". SUCCESSFUL")
            except Exception as ex:
                print("updateSymbol() Query", q1, ". Exception:", str(ex))

    def deleteSymbol(self, id):
        if id is None:
            return

        if len(id) != 32:
            print("ERROR: {} is not properly formatted".format(id))
            return

        qlist = list()
        qlist.append("delete from symbols where id='{}'".format(id))
        qlist.append("delete from dividend where symbolid='{}'".format(id))
        qlist.append("delete from sharesbuy where symbolid='{}'".format(id))
        qlist.append("delete from sharessell where symbolid='{}'".format(id))
        qlist.append("delete from marketcode where id='{}'".format(id))

        for q1 in qlist:
            try:
                self.db.execute(q1)
                self.db.commit()
                print("deleteSymbol() Query", q1, ". SUCCESSFUL")
            except Exception as ex:
                print("deleteSymbol() Query", q1, ". Exception:", str(ex))

    def getExchangeList(self):
        return ["NSE", "BSE"]


    def getTransactionBetween(self,
                              startdd, startmm, startyy,
                              stopdd, stopmm, stopyy):
        startdate = createSQLDate(startdd, startmm, startyy)
        stopdate  = createSQLDate(stopdd, stopmm, stopyy)

        q = '''select * FROM
            (
            select  transdate, "D" as transtype, id, symbolid, remarks, 0 as qty, amount from dividend
            union all
            select  transdate, "B" as transtype, id, symbolid, "BUY" as remarks, qty, amount from sharesbuy
            union all
            select  transdate, "S" as transtype, id, symbolid, "SELL" as remarks, qty, amount from sharessell
            ) 
            where transdate between '{}' and '{}'
            order by transdate'''.format(startdate, stopdate)
        l = list()
        if not self.isSetup():
            return l

        symbols = self.getAllSymbols()
        result = self.db.execute(q)
        for row in result:
            l.append(
                {
                    "transdate": row[0],
                    "type": row[1],
                    "id": row[2],
                    "symbolid": row[3],
                    "exchange": symbols[row[3]][0],
                    "name": symbols[row[3]][1],
                    "remarks": row[4],
                    "qty": row[5],
                    "amt": row[6]
                }
            )

        return l

    def deleteTransactionID(self, transtype:str, id:str):
        transtype = transtype.upper()
        tablename = None
        if "B" in transtype:
            tablename = "sharesbuy"
        elif "S" in transtype:
            tablename = "sharessell"
        elif "D" in transtype:
            tablename = "dividend"
        else:
            return False

        if id is None:
            return False
        elif len(id) < 5:
            return False

        try:
            q = "delete from {} where id='{}'".format(tablename, id)
            self.db.execute(q)
            self.commit()
            print(q, "SUCCESSFUL")
            return True
        except Exception as ex:
            print("EXCEPTION:", str(ex))
            return False

    def createLiveConnTable(self):
        if self.checkTable("marketcode"):
            return True

        q = "create table marketcode (id char(32) primary key not null, code char(64) not null)"
        try:
            self.db.execute(q)
            self.db.commit()
            print("SUCCESS:", q)
            return True
        except Exception as ex:
            print("createLiveConnTable() Exception:", str(ex))
            return False

    def deleteLiveSymbol(self, id):
        if not self.isSetup():
            return False

        if id is None:
            return False

        if len(id) != 32:
            return False

        q = "delete from marketcode where id='{}'".format(id)
        try:
            self.db.execute(q)
            self.db.commit()
            print("SUCCESS:", q)
            return True
        except Exception as ex:
            print("ERROR in",q,":", str(ex))
            return False

    def saveLiveSymbol(self, id, driver):
        if not self.isSetup():
            return False

        if id is None:
            return False

        if len(id) != 32:
            return False

        q = "insert into marketcode (id, code) values ('{}', '{}')".format(id, driver)
        try:
            self.db.execute(q)
            self.db.commit()
            print("SUCCESS:", q)
        except Exception as ex:
            print("ERROR in",q,":", str(ex))

        q = "update marketcode set code='{}' where id='{}'".format(driver, id)
        try:
            self.db.execute(q)
            self.db.commit()
            print("SUCCESS:", q)
        except Exception as ex:
            print("ERROR in",q,":", str(ex))

        return True

    def getAllLiveSymbols(self):
        d = dict()
        if not self.isSetup():
            return d

        q = "select id, code from marketcode"
        result = self.db.execute(q)
        for row in result:
            try:
                d[row[0]] = row[1]
            except:
                pass

        return d

    # Remarks
    def createRemarks(self):
        q = "create table remarks(id char(32) primary key not null, transdate date not null, particulars char(128))"
        if self.checkTable("remarks"):
            return True

        try:
            self.db.execute(q)
            self.commit()
            return True
        except:
            return False

    def newRemarks(self, dd, mm, yy, particulars:str):
        sleep(1)
        if not self.isSetup():
            return False


        _transdate = createSQLDate(dd, mm, yy)
        _id = generatekey(timestampnow())
        _rem = particulars[0:min([128, len(particulars)])]
        q = "insert into remarks(id, transdate, particulars) values('{}','{}','{}')".format(_id, _transdate, _rem)
        try:
            self.db.execute(q)
            self.commit()
            return True
        except:
            return False

    def deleteRemarks(self, id):
        if not self.isSetup():
            return False

        q = "delete from remarks where id='{}'".format(id)
        try:
            self.db.execute(q)
            self.commit()
            return True
        except:
            return False

    def updateRemarks(self, id, dd, mm, yy, particulars):
        if not self.isSetup():
            return False

        _transdate = createSQLDate(dd, mm, yy)
        _rem = particulars[0:min([128, len(particulars)])]
        q = "update remarks set transdate='{}', particulars='{}' where id='{}'".format(_transdate, _rem, id)
        try:
            self.db.execute(q)
            self.commit()
            return True
        except:
            return False


    def getRemarks(self, startdd, startmm, startyy,
                   stopdd, stopmm, stopyy):
        d = dict()
        if not self.isSetup():
            return d

        _start = createSQLDate(startdd, startmm, startyy)
        _stop = createSQLDate(stopdd, stopmm, stopyy)

        q = "select id, transdate, particulars from remarks where transdate between '{}' and  '{}' order by transdate desc".format(_start, _stop)
        try:
            result = self.db.execute(q)
            for row in result:
               d[row[0]] = {"date": row[1], "particulars": row[2]}
        except:
            pass

        return d


def main():
    db = Database()
    db.newRemarks(1,1,2020, "XX"+timestampnow()+" _"+generatekey(timestampnow()))
    for keys, vals in db.getRemarks(1,1,2019, 10,10,2022).items():
        print(keys, vals)
    #print(db.addSymbol("NSE", "Sunxxx"))
    #for key, val in db.findSymbols("nse","xxx").items():
        #print(key,"=", val)
    #print("transid=",db.addSellOptions(18,2,2020, "87310fae00ecee2eb523ea630b28cb7f", 10, 12345))
    #for key, val in db.listSymbols().items():
    #    print(key, val)

    #db.updateSymbol(id="caef335e94095b0911d13ef539c9c6e4", newexchange="BSE", newname="TITAN CO")
    #db.deleteSymbol(id="737c48f96306ed744ab9f806c5c210ca")
    #print(db.getTransactionBetween(1,1,2021, 12,12,2021))




if __name__=="__main__":
    main()
