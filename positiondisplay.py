import threading
import tkinter.messagebox
from datetime import datetime
import time
from tkinter import *
from tkinter import ttk
import struct, sys
import frida
from time import sleep
from threading import Thread

float3format = "X: {:.02f} Y: {:.02f} Z: {:.02f}"
positionVar = None
ptr_val = -1
hasError = False
curr_pos = (0,0,0)
saved_pos = (0,0,0)
recv_time = time.time()

def update_position():

    while ptr_val > 0:
        script.post({"type": "readpos", "payload": ptr_val})
        sleep(0.3)
    print("update_position returned")
    print(f"HasError: {hasError}")
    print(f"Ptr Val: {ptr_val:X}")

def save_position():
    global saved_pos
    saved_pos = curr_pos
    print(f"saved position as {saved_pos}")

def load_position():
    global saved_pos
    print(f"LOADING {saved_pos}")
    if saved_pos[0] == 0 and saved_pos[1] == 0 and saved_pos[2] == 0:
        return
    payload_obj = {"pos_bytes": list(struct.pack(">3f",*saved_pos)), "baseptr": ptr_val}
    script.post({"type":"writepos","payload": payload_obj})

posThread = Thread(target=update_position,daemon=True)

def on_message(message, data):
    global hasError, ptr_val, posThread, pos, recv_time, curr_pos
    if message['type'] == 'send':
        #   print(message['payload'])
        if message['payload'].startswith("0x"):
            now = datetime.now()
            cooldown_tdelta = time.time() - recv_time
            if ptr_val == -1 or cooldown_tdelta >= 5:
                ptr_val = int(message['payload'],16)
                sleep(.75) #wait a bit for 06 to load
                recv_time = time.time()
                hasError = False
                #script.post({"type": "checkamigo", "payload": ptr_val})
                script.post({"type": "readpos", "payload": ptr_val})
                if not posThread.is_alive():
                    posThread = Thread(target=update_position,daemon=True)
                    posThread.start()
            elif cooldown_tdelta < 5:
                print("too soon bro")
        elif message['payload'] == "position":
            floatarr = data
            curr_pos = struct.unpack(">3f", floatarr)
            positionVar.set(float3format.format(*curr_pos))
    elif message['type'] == 'error':
        print(message['stack'])
        hasError = True
        script.post("rescan")

if __name__ == '__main__':
    session = frida.attach("xenia.exe")
    script = session.create_script(open("script.js").read())
    script.on('message', on_message)
    script.load()
    root = Tk()
    root.title("Warp Portal v0.0.1 alpha ver.")
    positionVar = StringVar()
    positionVar.set(float3format.format(0, 0, 0))
    l = ttk.Label(textvariable=positionVar).grid(row=0,column=0,columnspan=2)
    savebtn = ttk.Button(text="Save",command=save_position).grid(row=1,column=0)
    loadbtn = ttk.Button(text="Load",command=load_position).grid(row=1,column=1)

    root.mainloop()
