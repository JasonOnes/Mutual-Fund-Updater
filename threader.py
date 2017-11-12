""" class to be used to override the run() function of thread so that I can stop thread upon fund delete"""
from threading import Thread


class Threader(Thread):
   # Thread.__init__(self)
    
    def __init__(self, go=False):

        self.go = go

        super(Threader, self).__init__()

    def start(self):
        self.go = True
        return run()



