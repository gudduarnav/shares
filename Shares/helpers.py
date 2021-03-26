# helper functions


def getInt(s : str, default_value : int = 0):
    try:
        return int(s)
    except:
        return default_value


def getFloat(s : str, default_value : float = 0.0):
    try:
        return float(s)
    except:
        return default_value

def createSQLDate(dd: int, mm: int, yy: int):
    return "{:04}/{:02}/{:02}".format(yy, mm, dd)


def getFinancialYearDate(yr):
    startYr = createSQLDate(1, 4, yr)
    endYr = createSQLDate(31, 3, yr+1)
    return (startYr, endYr)

def splitSQLDate(s:str):
    try:
        s1 = s.split("/")
        yy = int(s1[0])
        mm = int(s1[1])
        dd = int(s1[2])
        return (dd,mm,yy)
    except:
        return (0,0,0)


def beautifyExchange(exchange):
    return exchange.strip()[0:min([3, len(exchange)])].upper()

def beautifyName(name):
    return name.strip()[0:min([32, len(name)])].upper()


def main():
    print(getFinancialYearDate(2019))


if __name__=="__main__":
    main()