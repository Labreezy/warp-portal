import threading
import tkinter.messagebox
from datetime import datetime
import time
from tkinter import *
from tkinter import ttk
import struct
import frida
from time import sleep
from threading import Thread

import keyboard

float3format = "X: {:.02f} Y: {:.02f} Z: {:.02f}"
float4format = float3format + " W: {:.02f}"
positionVar = None
ptr_val = -1
hasError = False
curr_pos = [0,0,0]
curr_rot = [0,0,0,0]
curr_vel = [0,0,0]
recv_time = time.time()

def update_position():

    while ptr_val > 0:
        script.post({"type": "readpos", "payload": ptr_val})
        sleep(0.3)
    print("update_position returned")
    print(f"HasError: {hasError}")
    print(f"Ptr Val: {ptr_val:X}")

def save_position():
    global saved_pos, saved_rot
    saved_pos = curr_pos
    saved_rot = curr_rot
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
    global hasError, ptr_val, posThread, pos, recv_time, curr_pos, curr_rot, curr_vel
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
            x,y,z,_,xr,yr,zr,wr,_,vx,vy,vz = struct.unpack(">3f4s4f32s3f", floatarr)
            curr_pos = [x,y,z]
            curr_rot = [xr,yr,zr,wr]
            curr_vel = [vx,vy,vz]
            positionVar.set("Position: " + float3format.format(*curr_pos))
            speedVar.set("Velocity: " + float3format.format(*curr_vel))
            rotationVar.set("Rotation: " + float4format.format(*curr_rot))
    elif message['type'] == 'error':
        print(message['stack'])
        hasError = True
        script.post("rescan")

if __name__ == '__main__':
    session = frida.attach("xenia.exe") #make it work for canary, error handle xenia not being open
    script = session.create_script(open("script.js").read())
    script.on('message', on_message)
    script.load()
    root = Tk()
    root.geometry('320x240')
    root.title("Warp Portal v0.0.1")
    positionVar = StringVar()
    speedVar = StringVar()
    rotationVar = StringVar()
    positionVar.set("Position: " + float3format.format(0, 0, 0))
    speedVar.set("Speed: " + float3format.format(0,0,0))
    rotationVar.set("Rotation: " + float4format.format(0,0,0,0))

    l = ttk.Label(textvariable=positionVar).grid(row=0,column=0,columnspan=2)
    rl = ttk.Label(textvariable=rotationVar).grid(row=1, column=0, columnspan=2)
    vl = ttk.Label(textvariable=speedVar).grid(row=2,column=0,columnspan=2)
    savebtn = ttk.Button(text="Save (F9)",command=save_position).grid(row=3,column=0)
    loadbtn = ttk.Button(text="Load (F10)",command=load_position).grid(row=3,column=1)
    keyboard.add_hotkey("F9",save_position)
    keyboard.add_hotkey("F10",load_position)
    root.mainloop()
