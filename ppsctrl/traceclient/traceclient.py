import zmq
import sys
import os
import logging
import threading
import gc
import ctypes
import inspect
import queue


class TraceClient:
    _traceclientinstance = None

    def __init__(self, serverIp, port=6662, identity=1, sockopt_string = "id_123"):
        self._die = False
        self._host = serverIp
        self._port = port
        self._identity = identity
        # self._func = func
        self._context = zmq.Context()
        self._socket = self._context.socket(zmq.DEALER)
        self._socket.setsockopt_string(zmq.IDENTITY, sockopt_string)
        self._socket.setsockopt(zmq.RCVTIMEO, 0)
        self._socket.setsockopt(zmq.RCVHWM,0)
        self._socket.setsockopt(zmq.SNDHWM,0)
        #self._lock = threading.Lock()
        self._lock_send = threading.Lock()
        #self._messages = []
        #self._buffer = bytes()
        # self._replies = {}
        #self.message_queue=queue.Queue(maxsize=20)
        self._connect()
        #self._socket.setsockopt(zmq.NOBLOCK,True)
        #self._thread = threading.Thread(target=self._run, daemon=True)
        #self._thread.start()

    @staticmethod
    def get_trace_client(request):
        if TraceClient._traceclientinstance is None:
            host = request.config.getoption("--target-host")
        TraceClient._traceclientinstance = TraceClient(host, 6662)
        return TraceClient._traceclientinstance

    @staticmethod
    def get_rtc_client(request):
        if TraceClient._traceclientinstance is None:
            host = request.config.getoption("--target-host")
        TraceClient._traceclientinstance = TraceClient(host, 6666, 1, "PpsAdaptor")
        return TraceClient._traceclientinstance

    def _append(self, msg: str):
        # logging.info(msg)
        #with self._lock:
        #    self._messages.append(msg)
        self.message_queue.put(msg)
        
    def get_queue_size(self):
        return self.message_queue.qsize()
        
    def _connect(self):
        print("Connecting to ...[%s]%s\n" % (self._host, self._port))
        logging.info("Connecting to %s:%d...", self._host, self._port)
        try:
            self._socket.connect("tcp://{0}:{1}".format(self._host, self._port))
            logging.info("Connected")
        except TimeoutError as ex:
            raise TimeoutError(
                f"Timeout connecting to {self._host}:{self._port}"
            ) from ex

    def _run(self):
        while not self._die:
            if not self._socket.closed:
                message = self._socket.recv()
                self._append(message)
            else:
                logging.error("sock is closed,can't receive any message...")
                break

    def sendMsg(self, data):
        with self._lock_send:
        #self._lock.acquire()
            if not self._socket.closed:
                self._socket.send(data)
                del data
                #gc.collect()
            else:
                logging.error("sock is closed,can't send message...")
        #self._lock.release()
    def recvMsgSocket(self):
        message=None
        if not self._socket.closed:
            message = self._socket.recv()
        return message
        
    def recvMsgSocket1(self):
        #message=None
        #try:
        #    if not self._socket.closed:
        #        message = self._socket.recv()
        #except zmq.Again as e:
        #    message=None
        #        return message 
        full_message=None
        message_parts = []
        while True:
            try:
                part = self._socket.recv()
                if self._socket.get(zmq.RCVMORE):
                    message_parts.append(part)
                else:
                    message_parts.append(part)
                    break
            except zmq.Again:
                part=None
        full_message = b''.join(message_parts)
        message_parts.clear()
        del message_parts
        return full_message
        
        
    def readMsg1(self):
        #self._lock.acquire()
        #with self._lock:
        #    if len(self._messages) > 0:
                # msg = self._messages[0]
                # msg =  self._messages.pop(0)
        #        return self._messages.pop(0)
            #self._lock.release()
        #return None
        items=[]
        #for _ in range(10):
        #    if self.message_queue.empty():
        #        break;
        #    else:
         #       items.append(self.message_queue.get())
        #return items
        
        while not self.message_queue.empty():
            items.append(self.message_queue.get())
        return items
    
    def readMsg(self):
        #self._lock.acquire()
        #with self._lock:
        #    if len(self._messages) > 0:
                # msg = self._messages[0]
                # msg =  self._messages.pop(0)
        #        return self._messages.pop(0)
            #self._lock.release()
        #return None
         #return self.message_queue.get()
        #message=None
        #while message is None: 
        #    if not self._socket.closed:
        #        message = self._socket.recv()
        #return message
        message=None
        while message is None: 
            try:
                if not self._socket.closed:
                    message = self._socket.recv()
            except zmq.Again as e:
                message=None
        return message
        
        
