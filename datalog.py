import logging, datetime, time
import os

'''
class Datalog 
    creates a logfile named YYYYMMDD.log with today's date
    calculates, from logHours (default 1) and logsPerHour (default 60) 
        amount of measurements to take, i.e. times to enter s/t into the log 
        logging Idle interval

    method LogIt adds data and a counter to the log, delimited by delim (default |) 
    method Idle sleeps for an Idle interval. 
    
todo: 
    rather than sleeping, pass control back to OS and do useful stuff while Idle interval lasts
    
'''

class Datalog:
    def __init__(self, logHours=1, logsPerHour=60):
        Filename = datetime.datetime.now().strftime("%Y%m%d")
        logging.basicConfig(filename=Filename + '.log', level=logging.INFO)

        self.logsPerHour = logsPerHour
        self.logHours = logHours
        self.logInterval = 3600 // logsPerHour
        self.logTime = range(0, int(logHours * logsPerHour))
    
    def LogIt(self, data, i, delim='|'):
        timenow = delim + datetime.datetime.now().strftime("%H:%M:%S")
        logging.info(delim.join([timenow, str(data), str(i)]))
        return
        
    def Idle(self):
        time.sleep(self.logInterval)
        return

# example usage:         
def main():
    log = Datalog(logHours=0.5, logsPerHour=120)
    for i in log.logTime:
        data = os.urandom(6)    # this is just for testing
        log.LogIt(data, i)
        log.Idle()              # this is ugly
        
if __name__ == "__main__":
    main()
    
