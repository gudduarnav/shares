try:
    import hashlib
except ImportError as ex:
    print("Install hashlib. Exception:", str(ex))
    exit(1)

from datetime import datetime

def generatekey(s:str):
    bytedata = s.encode("UTF-8")
    r = hashlib.md5(bytedata)
    return r.hexdigest()

def timestampnow():
    now = datetime.now()
    s_now = now.strftime("%Y%m%d%H%M%S%f")
    return s_now


def main():
    #s = "Hello World"
    #key = generatekey(s)
    #print(s,"key is", key, "len=", len(key))
    id = timestampnow()
    print(id, "len=", len(id))

if __name__=="__main__":
    main()