import os
import time
import asyncio
import json
import websockets
import subprocess
from .utils.get_open_ports import get_open_ports
from .utils.install_oobagooba import install_oobabooga
from .uninstall import uninstall
import random
import sys


class llm:
    def __init__(self, path, cpu=False, verbose=False):

        try:
            self.cpu = cpu
            self.verbose = verbose

            if cpu:
                self.gpu_choice = "N"
            else:
                self.gpu_choice = None # < We'll detect it

            # This will add self.gpu_choice and self.start_script, which we need.
            # (It will finish very quickly if it's actually already installed!)
            install_oobabooga(self)

            # Start oobabooga server
            model_dir = "/".join(path.split("/")[:-1])
            model_name = path.split("/")[-1]

            # Find an open port
            while True:
                self.port = random.randint(0, 10000)
                open_ports = get_open_ports(0, 10000)
                if self.port not in open_ports:
                    break

            cmd = [
                self.start_script,
                "--model-dir", model_dir,
                "--model", model_name,
                "--api-streaming-port", str(self.port),
                "--extensions", "api",
                "--api",
            ]

            if self.gpu_choice == "N":
                cmd.append("--cpu")
            if self.verbose:
                cmd.append("--verbose")

            if self.verbose:
                print("Running command:", " ".join(cmd))

            env = os.environ.copy()
            env["LAUNCH_AFTER_INSTALL"] = "True"
            if self.verbose:
                subprocess.Popen(cmd, env=env, stdout=sys.stdout, stderr=sys.stderr)
            else:
                subprocess.Popen(cmd, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            ##### DEBUG #####
            """
            while True:
                time.sleep(3)
                if process.stderr:
                    for line in iter(process.stderr.readline, ''):
                        print(line)
                if process.stdout:
                    for line in iter(process.stdout.readline, ''):
                        print(line)
            """
            ##### DEBUG #####

            self.uri = f'ws://localhost:{self.port}/api/v1/chat-stream'

            # Wait for it to be ready by checking the port
            for attempt in range(50):
                open_ports = get_open_ports(0, 10000)
                if self.port in open_ports:
                    if self.verbose:
                        print("Server is ready.")
                    break
                else:
                    if self.verbose:
                        print(f"Server is not ready... ({attempt+1}/20)")
                    time.sleep(1.5)
            else:
                raise Exception("Server took too long to start")

            # Warm up the server (idk why it needs this, but it does)
            if self.verbose:
                print("Warming up the server...")
                
            async def warmup_server():
                await self.chat([{"role": "user", "content": "Hi"}], max_tokens=1)
            asyncio.run(warmup_server())

            if self.verbose:
                print("Server is warmed up.")

        except Exception as e:
            print(e)

            if not self.cpu:
                print("Auto GPU installation was unsuccessful. Re-installing for CPU use.")

                uninstall(confirm=False)
                self.__init__(path, cpu=True, verbose=self.verbose)


    def chat(self, messages, max_tokens=None, temperature=0):

        if messages[-1]["role"] != "user":
            raise ValueError("The last message role must be 'user'")
        
        user_input = messages[-1]["content"]
        messages = messages[:-1]

        request = {
            'user_input': user_input,
            'history': messages,
            'mode': 'chat', # Valid options: 'chat', 'chat-instruct', 'instruct'
            'temperature': temperature,
        }

        if max_tokens == None:
            request["auto_max_new_tokens"] = True
        else:
            request["max_tokens"] = max_tokens

        async def async_chat():
            async with websockets.connect(self.uri, ping_interval=None) as websocket:
                await websocket.send(json.dumps(request))

                current_length = 0

                while True:
                    incoming_data = await websocket.recv()
                    incoming_data = json.loads(incoming_data)

                    match incoming_data['event']:
                        case 'text_stream':
                            new_history = incoming_data['history']
                            if not new_history['visible']:
                                continue
                            token = new_history['visible'][-1][1][current_length:]
                            current_length += len(token)
                            yield token
                        case 'stream_end':
                            return
                    
        # Create a new event loop and run the async function in it
        loop = asyncio.new_event_loop()
        return loop.run_until_complete(async_chat())