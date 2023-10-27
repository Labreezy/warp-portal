from tkinter import *
from tkinter import ttk
import struct, sys
import frida
from time import sleep

float3format = "X: {} Y: {} Z: {}"
positionVar = None



def on_message(message, data):
    if message['type'] == 'send':
        print(message['payload'])
        if message['payload'].startswith("0x"):
            ptr_val = int(message['payload'],16)
            sleep(2)
            script.post({"type": "findptr", "payload": ptr_val})
    elif message['type'] == 'error':
        print(message['stack'])

if __name__ == '__main__':
    session = frida.attach("xenia.exe")
    script = session.create_script(open("script.js").read())
    script.on('message', on_message)
    script.load()
    root = Tk()
    positionVar = StringVar()
    positionVar.set(float3format.format(0, 0, 0))
    l = ttk.Label(textvariable=positionVar)
    l.pack()
    root.mainloop()
