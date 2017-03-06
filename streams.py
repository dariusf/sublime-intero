from threading import Thread
from queue import Queue, Empty

# Taken from http://eyalarubas.com/python-subproc-nonblock.html

class NonBlockingStreamReader:

    def __init__(self, process, stream, success_terminal, failure_terminal, done):

        self.done = done

        def _populateQueue(self, process, stream, success, failure): #, done):
            result = []
            # while process.poll() is not None:
            while True: # TODO terminate if process is dead
                line = None
                try:
                    line = str(stream.readline(), 'utf-8')
                except Exception as e:
                    print('intero process not alive')
                    break
                if line:
                    result.append(line)
                    if success in line or failure in line:
                        # drain the queue
                        self.done(result)
                        result = []
                else:
                    # raise UnexpectedEndOfStream
                    print('end of stream')
                    break

        self._t = Thread(target = _populateQueue,
                args = (self, process, stream, success_terminal, failure_terminal))
        self._t.daemon = True
        self._t.start() #start collecting lines from the stream

# class UnexpectedEndOfStream(Exception): pass
