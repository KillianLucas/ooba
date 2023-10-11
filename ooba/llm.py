import os
import time
import asyncio
import json
import websockets
import subprocess
from .utils.get_open_ports import get_open_ports
from .utils.detect_hardware import detect_hardware
from .uninstall import uninstall
import random
import sys
import threading
import asyncio
import json
import websockets
from queue import Queue
from.utils.openai_messages_converters import role_content_to_history
from .install import install as install_oobabooga
from .utils.get_app_dir import get_app_dir

REPO_DIR = os.path.join(get_app_dir(), 'text-generation-ui')

class llm:
    def __init__(self, path, cpu=False, verbose=False, first_time=True):

        if first_time:
            print("\nGetting started...")

        try:
            self.path = path
            self.cpu = cpu
            self.verbose = verbose

            self.gpu_choice, start_script_filename = detect_hardware()

            self.start_script = os.path.join(REPO_DIR, start_script_filename)

            if cpu:
                self.gpu_choice = "N"

            # This will exit if it's already installed
            install_oobabooga(gpu_choice=self.gpu_choice)

            # Start oobabooga server
            model_dir = "/".join(path.split("/")[:-1])
            model_name = path.split("/")[-1]

            # Find an open port
            while True:
                self.port = random.randint(2000, 10000)
                open_ports = get_open_ports(2000, 10000)
                if self.port not in open_ports:
                    break

            # Also find an open port for blocking -- it will error otherwise
            while True:
                unused_blocking_port = random.randint(2000, 10000)
                open_ports = get_open_ports(2000, 10000)
                if unused_blocking_port not in open_ports:
                    break

            cmd = [
                self.start_script,
                "--model-dir", model_dir,
                "--model", model_name,
                "--api-blocking-port", str(unused_blocking_port),
                "--api-streaming-port", str(self.port),
                "--extensions", "api",
                "--api"
            ]

            if self.gpu_choice == "N":
                cmd.append("--cpu")
            if self.verbose:
                cmd.append("--verbose")

            if self.verbose:
                print("Running command:", " ".join(cmd))

            env = os.environ.copy()
            env["GPU_CHOICE"] = self.gpu_choice
            env["LAUNCH_AFTER_INSTALL"] = "True"
            env["INSTALL_EXTENSIONS"] = "False"
            
            if self.verbose:
                self.process = subprocess.Popen(cmd, env=env, stdout=sys.stdout, stderr=sys.stderr)
            else:
                self.process = subprocess.Popen(cmd, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            self.uri = f'ws://localhost:{self.port}/api/v1/chat-stream'

            # Wait for it to be ready by checking the port
            num_attempts = 50
            for attempt in range(num_attempts):
                open_ports = get_open_ports(2000, 10000)
                if self.port in open_ports:
                    if self.verbose:
                        print("Server is ready.")
                    break
                else:
                    if self.verbose:
                        print(f"Server is not ready... ({attempt+1}/{num_attempts})")
                    time.sleep(1.5)
            else:
                raise Exception("Server took too long to start")

            
            # Warm up the server (idk if it needs this)
            """
            if self.verbose:
                print("Warming up the server...")
                
            for _ in self.chat([{"role": "user", "content": "Hi"}], max_tokens=1):
                break

            if self.verbose:
                print("Server is warmed up.")
            """
            

        except Exception as e:
            print(e)

            if self.gpu_choice == "N":
                raise
            else:
                print("Auto GPU installation was unsuccessful. Re-installing for CPU use.")

                install_oobabooga(force_reinstall=True, cpu=True)
                self.__init__(path, cpu=True, verbose=self.verbose)

        if first_time:
            # Hack to fix it not working multiple times in a row. Must change this soon
            self.first_time = True


    def chat(self, messages, max_tokens=None, temperature=0):

        # Hack to fix it not working multiple times in a row. Must change this soon
        if self.first_time:
            self.first_time = False
        else:
            self.process.terminate()
            self.__init__(self.path, cpu=self.cpu, verbose=self.verbose, first_time=False)
                
        if any([message["role"] == "system" for message in messages[1:]]):
            raise ValueError("Only the first message can have {'role': 'system'}.")
        
        if "system" in messages[0]["role"]:
            system_message = messages[0]["content"]
            messages = messages[1:]
        else:
            system_message = "You are a helpful AI assistant."

        if messages[-1]["role"] != "user":
            raise ValueError("The last message role must be 'user'")

        user_input = messages[-1]["content"]
        messages = messages[:-1]

        messages = role_content_to_history(messages)

        request = {
            'context': system_message,
            'user_input': user_input,
            'history': messages,
            'mode': 'chat', # Valid options: 'chat', 'chat-instruct', 'instruct'
            'temperature': temperature,
        }

        if max_tokens == None:
            request["auto_max_new_tokens"] = True
        else:
            request["max_new_tokens"] = max_tokens
            request["auto_max_new_tokens"] = False

        q = Queue()

        def run_async_code():
            async def async_chat():
                async with websockets.connect(self.uri, ping_interval=None, open_timeout=9999) as websocket:
                    current_length = 0
                    await websocket.send(json.dumps(request))

                    while True:
                        try:
                            incoming_data = await websocket.recv()
                        except websockets.exceptions.ConnectionClosedError as e:
                            # This happens if they cancel mid-stream
                            if self.verbose:
                                print(e)
                            return
                        incoming_data = json.loads(incoming_data)

                        match incoming_data['event']:
                            case 'text_stream':
                                new_history = incoming_data['history']
                                if not new_history['visible']:
                                    continue
                                token = new_history['visible'][-1][1][current_length:]
                                current_length += len(token)
                                q.put(token)
                            case 'stream_end':
                                q.put(None)  # signal the end
                                return

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(async_chat())

        t = threading.Thread(target=run_async_code)
        t.start()

        while True:
            item = q.get()
            if item is None:  # signal for completion
                break
            yield item