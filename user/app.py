import tkinter as tk
from tkinter import filedialog as fd

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from backbone.dataHandler import fileReader, fileWriter
from backbone.hwCom import mainController

import numpy as np

import threading

import time

import signal

root = tk.Tk()

data = fileReader()
dataOut = fileWriter()

DELAY = 0.2

control = mainController(mode="proc")
clkEnd = False
updating = False
inPause = True
auto = False
dumping = False
# open_hw_manager; connect_hw_server; open_hw_target -xvc_url localhost:2542

class mainWindow(tk.Frame):
    mainGraph = [0, 0, 0]  # 0 fig; 1 axis; 2 plot
    signalGraph = [0, 0, 0]
    stateId = 0
    btnStop = 0
    btnStart = 0
    btnRestart = 0
    btnDoFileWStart = 0
    btnDoFileWStop = 0
    control = 0
    clkThread = 0
    inAuto = False

    def __init__(self, controller, master=None):
        tk.Frame.__init__(self, master)
        root.title('Visualizador de proceso')
        self.initElements()
        self.control = controller
        self.clkThread = threading.Thread(target=self.clk)
        self.clkThread.start()

    def getControl(self):
        return self.control

    def upDateGraph(self):
        if inPause:
            print('do init first')
            return
        global updating
        updating = True
        block = data.readChunk()

        self.signalGraph[1].clear()
        self.signalGraph[1].plot(block)
        self.signalGraph[0].draw_idle()

        self.control.sendBlock(block)
        resultBlock = self.control.getBlock()
        self.mainGraph[1].clear()
        self.mainGraph[1].stem(np.abs(resultBlock),use_line_collection=True)
        self.mainGraph[0].draw_idle()
        if dumping:
            dataOut.appendBlock(resultBlock)
        if data.fileDone:
            self.doDumpStop()
            self.doStart()
            print('done with file')
        updating = False

    def doStart(self):
        global inPause
        global auto
        if inPause:
            filename = fd.askopenfilename()
            if filename == "":
                print('Error, select a file')
                return
            if not data.changeFile(filename):
                return
            self.control.doStart()
            self.btnStart['text'] = 'Stop'
        else:
            self.btnStart['text'] = 'Start'
        self.btnRestart['text'] = 'Auto'
        auto = False
        inPause = not inPause

    def doAuto(self):
        global auto
        if auto:
            self.btnRestart['text'] = 'Auto'
        else:
            self.btnRestart['text'] = 'Stop Auto'
        auto = not auto
    def doDumpInit(self):
        global dumping
        if dumping:
            return
        dumping = True
        dataOut.initDump()
    def doDumpStop(self):
        global dumping
        if not dumping:
            return
        dumping = False
        dataOut.doStop()
    def initElements(self):
        self.btnDoFileWStart = tk.Button(master=root, text="Iniciar Volcado", command=lambda: self.doDumpInit())
        self.btnDoFileWStart.grid(row=0, column=0, sticky='W')
        self.btnDoFileWStop = tk.Button(master=root, text="Detener Volcado", command=lambda: self.doDumpStop())
        self.btnDoFileWStop.grid(row=0, column=0)

        self.mainGraph[2] = plt.Figure(figsize=(8, 5), dpi=100)
        self.mainGraph[1] = self.mainGraph[2].add_subplot(111)
        self.mainGraph[0] = FigureCanvasTkAgg(self.mainGraph[2], master=root)
        self.mainGraph[0].get_tk_widget().grid(
            row=1, column=0, sticky='W', columnspan=2)

        self.signalGraph[2] = plt.Figure(figsize=(8, 3), dpi=100)
        self.signalGraph[1] = self.signalGraph[2].add_subplot(111)
        self.signalGraph[0] = FigureCanvasTkAgg(
            self.signalGraph[2], master=root)
        self.signalGraph[0].get_tk_widget().grid(
            row=2, column=0, sticky='W', columnspan=2, pady=2)

        self.stateId = tk.Label(master=root, text="Indicador estado")
        self.stateId.grid(row=1, column=3, sticky='N', padx=10)

        self.btnStart = tk.Button(
            master=root, text="Iniciar", command=lambda: self.doStart())
        self.btnStart.grid(row=1, column=4, sticky='N')
        self.btnStop = tk.Button(master=root, text="Step", command=lambda: self.upDateGraph())
        self.btnStop.grid(row=1, column=5, sticky='N')
        self.btnRestart = tk.Button(master=root, text="Auto", command=lambda: self.doAuto())
        self.btnRestart.grid(row=1, column=6, sticky='N')
    def clk(self):
        while not clkEnd:
            time.sleep(DELAY)
            if clkEnd:
                return
            if auto:
                self.upDateGraph()

def close_handler():
    global clkEnd
    global inPause
    global auto
    if dumping:
        dataOut.doStop()
    inPause = False
    clkEnd = True
    auto = True
    control.doClose()
    root.destroy()


root.resizable(False, False)
root.protocol("WM_DELETE_WINDOW", close_handler)
app = mainWindow(control,master=root)
app.mainloop()

#
##        mainGraph = plt.Figure(figsize=(6,5), dpi=100)
##        mainAxis = mainGraph.add_subplot(111)
##        grahp1 = FigureCanvasTkAgg(mainGraph, root)
##        grahp1.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH)
