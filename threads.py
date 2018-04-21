# -*- coding: utf-8 -*-

"""
The threads module.
======================

The Worker thread executes a callback with the queue message. And the Manager class
handle the worker processes, suporting interaction with the queue transport.

:Example:

>>> import time
>>> from threads import Manager
>>> def run(msg):
...     print('Received: ' + msg)
...     time.sleep(3)
>>> manager = Manager(run)
>>> for i in range(0, 5):
...     manager.put('{} - A new message'.format(i))
>>> manager.start()
>>> manager.wait()
Received: 0 - A new message
Received: 1 - A new message
Received: 2 - A new message
Received: 3 - A new message
Received: 4 - A new message

"""

import threading
import signal
try:
    from queue import Queue
except OSError:
    from Queue import Queue

# Thread exit key.
POISON_PILL = 'exit'

class Worker(threading.Thread):
    """A thread class to handle queue objects."""
    def __init__(self, queue, callback):
        """
        Construct the worker class.
        
        :param queue: The underleying Queue class.
        :param callback: The function to execute with queue content.
        :return: The worker class.
        """
        threading.Thread.__init__(self)
        self.queue = queue
        self.callback = callback

    def run(self):
        """Execute the thread. Overides on Thread object."""
        while True:
            # Get content from queue.
            content = self.queue.get()

            if content == POISON_PILL:
                # Quits the thread loop and exit.
                break 

            # Receive content on queue producer then we run the callback with
            # the content as parameter.
            self.callback(content)

class Manager(object):
    """The thread manager."""

    # The number of parallel workers.
    WORKERS = 4

    def __init__(self, callback):
        """
        Construct the worker manager class.

        :param callback: The function to be executed by the workers.
        """
        self.queue = Queue()
        self.workers = []
        self.callback = callback
        self.joined = False
        self._on_finish = None

    def on_finish(self, callback, *args):
        """
        Define the callback to be executed when the worker finishes the process.
        
        :param callback: The function to be executed.
        :param args: The function arguments.
        """
        if not callable(callback):
            raise TypeError('The callback must be a function, not {}'.format(callback.__class__.__name__))
        
        # Register the worker finishing handler.
        self._on_finish = [callback, *args]

    def start(self, data=None):
        """Start the workers."""
        self.__build_workers()

    def put(self, data):
        """
        Put data on queue to be executed on worker.

        :param data: The data to be inserted on queue. 
        """
        self.queue.put(data)
    
    def wait(self, timeout=None):
        """Stop the workers."""
        for _ in self.workers:
            self.put(POISON_PILL)

        # Wait for threads to finish process.
        for worker in self.workers:
            worker.join()
        
        if self._on_finish:
            # Handle the finishing callback. 
            self.finish_handler()

    def finish_handler(self):
        """Handle a finishing event."""
        if self._on_finish:
            self._on_finish[0](*self._on_finish[1:])

    def __build_workers(self):
        """Build the class workers."""
        for _ in range(0, self.WORKERS):
            worker = Worker(self.queue, self.callback)
            
            # Start the worker process.
            worker.start()

            # Append the worker to the class workers.
            self.workers.append(worker)