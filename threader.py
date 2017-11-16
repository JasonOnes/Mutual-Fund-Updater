""" class to be used to override the run() function of thread so that I can stop thread upon fund delete"""
#from threading import Thread, Event
import threading
import time 

from fundstuff import schedule_quote
#TODO put schedule_quote and dependent functs in file seperate from main for import

class Threader(threading.Thread):
    #threading.Thread.__init__(self)
    
    def __init__(self, name, target, args):
        # threading.Thread.__init__(self)
        # self.go = True
        # self.go = Event()#
        # self._stop = Event()
        self.args = args
        super(Threader, self).__init__(name=None,target=None, args=[])
        #self._stopper = Event()
        self.go = True


    def start(self):
        return schedule_quote(self)
        # if self.go:
        #     #schedule_quote(self.args)
        #     for arg in self.args:
        #         print(arg)
        #     print(str(self.go))
        #     return schedule_quote(self.args[0], self.args[1], self.args[2], self.args[3], self.go)
        # else:
        #     pass
        #     time.sleep(5)
           
            
        #while not self.go.is_set():
        # while True:
        #     if self.stopped():
        #         break
        #     time.sleep(1)


    def stop(self):
        print("Trying")
        self.go = False
        #return schedule_quote(self.args[0], self.args[1], self.args[2], self.args[3], self.go)
        return schedule_quote(self)
        #self._stopper.set()

    #def stopped(self):
     #   return self._stopper.is_set()
    # def start(self):
    #     self.go = True
    #     return run()
    
    


    def get_going(self):
        fund_thread = Threader.current_thread()
        while getattr(fund_thread, "go", True):
            fund_thread.target(fund_thread.args, fund_thread.go)
            time.sleep(1)



