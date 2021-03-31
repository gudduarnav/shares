try:
    from selenium import webdriver
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
except ImportError as __ex:
    print("Install Selenium. Exception:", str(__ex))
    exit(1)


from exchange.exchangedriver import ExchangeDriver
from datetime import datetime


class Driver:
    def __init__(self, waitTime=10):
        self.counter = 0
        self.driver = None
        self.d = dict()

        try:
            options = webdriver.ChromeOptions()
            options.add_argument("--headless")
            options.add_argument("--enable-javascript")

            self.driver = webdriver.Chrome(chrome_options=options)
            self.driver.implicitly_wait(time_to_wait=waitTime)
        except Exception as ex:
            print("Exception:", str(ex))

    def addMe(self, sym, c):
        self.d[sym] = c

    def getMe(self, sym):
        return self.d[sym]


    def addRef(self):
        self.counter = self.counter + 1
        return self.driver

    def get(self): # get driver
        return self.driver

    def releaseRelease(self):
        self.counter = self.counter - 1

    def newWindow(self, id):
        try:
            h = self.driver.window_handles
            if len(h) > 0:
                h0 = h[0]
                self.driver.switch_to.window(h0)

            self.driver.execute_script("window.open('about:blank', '{}')".format(id))
            self.driver.switch_to.window(id)
            return True
        except:
            return False

    def switchTo(self, id):
        curWindow = self.driver.current_window_handle
        title = self.driver.title
        if title == id:
            return True

        h = self.driver.window_handles
        for h1 in h:
            if h1 == curWindow:
                continue
                
            self.driver.switch_to.window(h1)
            title = self.driver.title
            if title == id:
                return True

        return False

    def __del__(self):
        try:
            self.driver.close()
            self.driver.quit()
        except:
            pass


driver = None




class Quote:
    def __init__(self, symbol, waitTime=10):
        global driver
        self.price = 0.0
        self.id = str(datetime.now())
        self.waitTime = waitTime

        try:
            driver.addRef()
            driver.newWindow(id=self.id)

            self.url = "https://www.google.com/search?q={}".format(symbol)
            driver.get().get(self.url)
            self.id = driver.get().title
            driver.addMe(symbol, self)
            print("ID of {} is {}".format(symbol, self.id))
        except Exception as ex:
            print("Quote::__init__(symbol={}) Exception:".format(symbol), str(ex))

    def updatePrice(self):
        global driver
        try:
            if not driver.switchTo(self.id):
                return False

            el = WebDriverWait(driver.get(), self.waitTime).until(
                EC.presence_of_element_located(
                    (By.XPATH,
                     '//*[@id="knowledge-finance-wholepage__entity-summary"]/div/g-card-section/div/g-card-section/div[2]/div[1]/span[1]/span/span[1]')
                )
            )
            self.price = float(el.text)
            return True
        except:
            return False


    def getPrice(self):
        return self.price

    def __del__(self):
        try:
            global driver
            driver.releaseRelease()
        except:
            pass


def createQuote(sym):
    global driver
    if driver is None:
        driver = Driver()

    c = None
    try:
        c = driver.getMe(sym)
    except:
        pass

    if c is None:
        c = Quote(sym)

    return c

class GoogleQuote(ExchangeDriver):
    def __init__(self, symbol):
        self.q = createQuote(symbol)
        self.updatePrices()

    def updatePrices(self):
        return self.q.updatePrice()

    def getBuyPrice(self):
        return self.q.getPrice()

    def getSellPrice(self):
        return self.q.getPrice()

    def getAvePrice(self):
        return self.q.getPrice()


def main():
    q1 = GoogleQuote(symbol="NSE:AXISBANK")
    q2 = GoogleQuote(symbol="NSE:SBIN")
    for _ in range(0, 50):
        print(q1.updatePrices(), q2.updatePrices())
        print(q1.getAvePrice(), q2.getAvePrice())



if __name__ == "__main__":
    main()

