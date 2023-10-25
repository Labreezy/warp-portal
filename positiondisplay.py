from tkinter import *
from tkinter import ttk
import struct, sys
import frida


float3format = "X: {} Y: {} Z: {}"
positionVar = None

def on_message(message, data):
    print(message)

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
