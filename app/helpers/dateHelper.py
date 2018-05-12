import time
def getTimeFromStamp(stamp):
    timeArray = time.localtime(int(stamp))
    return  time.strftime("%Y-%m-%d %H:%M:%S", timeArray)