import os

import queue

import numpy as np

import matplotlib.pyplot as plt

from fixedpoint import FixedPoint

import cmath

class Config:
    window = 128
    fileMaxSize = 100000000
    fileMax = 10
    operWidth = 32
    qformat = [4, 12]
    dictCmd = {'start': 1, 'stop': 2, 'restart': 3, 'ready': 4,
               'nextRe': 5, 'nextIm': 6, 'give': 7, 'resume': 8}
    devPath = "/dev/xdma0_user"
    env = "proc"
    verbose = False

def getRoots(toFile=False):
    N_min = Config.window
    n = np.arange(N_min)
    k = n[:, None]
    M = -2j * np.pi * n * k / N_min
    mat = np.exp(M)
    if toFile:
        file = open('roots.txt','w')
        for line in mat:
            for element in line:
                file.write(str(element)+'\n')
    return mat

class fpFormatter:
    qformat = 0

    def __init__(self, qformat=Config.qformat):
        self.qformat = qformat

    def fpToDec(self, fpNum) -> complex:
        xHigh = hex(fpNum[0])
        xLow = hex(fpNum[1])[2:]
        if len(xLow) < 2:
            xLow = '0'+xLow
        x = FixedPoint(xHigh+xLow, signed=True,m=self.qformat[0], n=self.qformat[1])
        yHigh = hex(fpNum[2])
        yLow = hex(fpNum[3])[2:]
        if len(yLow) < 2:
            yLow = '0'+yLow
        y = FixedPoint(yHigh+yLow, signed=True,m=self.qformat[0], n=self.qformat[1])
        if (Config.verbose):##0f38.3244 0968.3244 0000.0000 0968.0000 0f38.0000 0f38.0000 0968.0000 0800.0000
            print(xHigh,xLow)
            print(yHigh,yLow)
            print(x,y)
        return cmath.rect(x, y)##0000.6488 0000.3244 0001.0000 0000.3244 0000.9b78 0000.3244 0001.0000 0000.3244

    def decToFp(self, decNum) -> list:
        mag,phase = cmath.polar(decNum)
        if (Config.verbose):
            print(mag,phase)
        try:
            im = str(FixedPoint(phase, signed=True,
                     m=self.qformat[0], n=self.qformat[1]))
        except Exception:
            im = '0000'
        try:
            re = str(FixedPoint(mag, signed=True,
                     m=self.qformat[0], n=self.qformat[1]))
        except Exception:
            re = '0000'
        lowerIm = im[2:]
        higherIm = im[0:2]
        lowerRe = re[2:]
        higherRe = re[0:2]
        result = [int(higherRe, 16), int(lowerRe, 16),
                  int(higherIm, 16), int(lowerIm, 16) ]
        if (Config.verbose):
            print(result)
        return result

    def test(self,toFile=False,rootsTest=False):
        f = 1000
        block = []
        if rootsTest:
            mat = getRoots(toFile=toFile)
            for line in mat:
                for element in line:
                    block += [element]
        else:
            for i in range(500):
                block += [np.sin(2*np.pi*44100/f*i)]
        blockRes = []
        if toFile:
            file = open('rootsOut.txt','w')
        for sample in block:
            print("-------------")
            print(sample)
            toFp = self.decToFp(sample)
            print(toFp)
            toN = self.fpToDec(toFp)
            print(toN)
            print("-------------")
            if toFile:
                file.write(str(toN)+'\n')
            blockRes += [toN]
        if toFile:
            file.close()
        if rootsTest:
            plt.subplot(1, 2, 1)
            plt.plot([n.real for n in block],[n.imag for n in block])
            plt.subplot(1, 2, 2)
            plt.plot([n.real for n in blockRes],[n.imag for n in blockRes])
            plt.show()
        else:
            plt.subplot(1, 2, 1)
            plt.plot(block)
            plt.subplot(1, 2, 2)
            plt.plot(blockRes)
            plt.show()


class DebugModel():
    vector = []
    roots = []
    def __init__(self):
        file = open('eje.txt','r')
        formatter = fpFormatter()
        for i in range(Config.window):
            sample = float(file.readline())
            toFp = formatter.decToFp(sample)
            toN = formatter.fpToDec(toFp)
            self.vector += [toN]
        file.close()
        mat = getRoots()
        for line in mat:
            row = []
            for element in line:
                toFp = formatter.decToFp(element)
                toN = formatter.fpToDec(toFp)
                row += [toN]
            self.roots += [row]
    def getExpectedResult(self):
        result = np.matmul(np.flip(self.roots),self.vector)
        print(result)
        plt.stem(abs(result),use_line_collection=True)
        plt.show()
        result = [0 for i in range(Config.window)]
        self.roots = np.array(self.roots)
        for i in range(len(self.roots)):
            col = self.roots[:,i]
            acum = 0
            for j in range(len(self.vector)):
                acum += self.vector[j] * col[j]
            result[i] = acum
        print(result)
        result = np.array(result)
        plt.stem(abs(result),use_line_collection=True)
        plt.show()

##-3.05277939-1.61402780e+00j -0.58789185-7.24612611e-01j
## -0.75191509-4.38234577e-01j -0.86328125+9.69191989e-06j
## -0.75192249+4.38241984e-01j -0.58790233+7.24606139e-01j
## -3.05278679+1.61402039e+00j  2.0390625 -1.37113696e-05j]

class debugQ:
    value = 0

    def put(self, x):
        print(x)
        self.value = x

    def task_done(self):
        pass

    def get(self):
        x = self.value
        print(x)
        return x

class mainController():
    fd_h2c = 0
    fd_c2h = 0
    state = "init"
    test = 0
    formatter = 0
    def __init__(self, mode="debug"):
        if mode == "proc":
            try:
                self.initDev()
            except FileNotFoundError:
                print("error with dev open, clossing")
                exit(-1)
        else:
            writeTest()
            self.test = open("tests/eje.txt")
            self.fd_h2c = os.open("backbone/devTestIn.txt", os.O_WRONLY)
            self.fd_c2h = os.open("backbone/devTestOut.txt", os.O_RDONLY)
        self.formatter = fpFormatter()
        self.debugQ = debugQ
        self.initDev()

    def initDev(self):
        self.fd_h2c = os.open(Config.devPath, os.O_WRONLY)
        self.fd_c2h = os.open(Config.devPath, os.O_RDONLY)

    def doClose(self):
        os.close(self.fd_h2c)
        os.close(self.fd_c2h)

    def doPause(self):
        # need to check if supported state
        self.sendToCard([Config.dictCmd["stop"], 0, 0, 0])

    def doRestart(self):
        self.sendToCard([Config.dictCmd["restart"], 0, 0, 0])

    def doStart(self):
        self.sendToCard([Config.dictCmd["start"], 0, 0, 0])

    def sendBlock(self, block):
        formater = fpFormatter()
        while self.readDev() != b'redy':
            pass
        for data in block:
            newNum = formater.decToFp(data)
            hiRe, lowRe = newNum[1], newNum[0]###check here, ok!
            hiIm, lowIm = newNum[3], newNum[2]
            self.sendToCard([Config.dictCmd["nextRe"], 0, hiRe, lowRe])
            self.sendToCard([Config.dictCmd["nextIm"], 0, hiIm, lowIm])
        while (self.readDev() != b'done'):
            self.sendToCard([Config.dictCmd["nextRe"], 0, 0, 0])
            self.sendToCard([Config.dictCmd["nextIm"], 0, 0, 0])
        if (Config.verbose):
            print("block done")
    def getBlock(self):
        block = []
        if (Config.verbose):
            print('getting block')
        if (Config.env == "debug"):
            for i in range(Config.window):
                n = self.test.readline()
                n = complex(n.strip('\n'))
                block += [n]
            return block
        self.sendToCard([Config.dictCmd["ready"], 0, 0, 0])
        while self.readDev() == b'ok\x00\x00':
            self.sendToCard([Config.dictCmd["give"], 0, 0, 0])
        flagRdy = True
        for i in range(Config.window*2):
            if (flagRdy):
                self.sendToCard([Config.dictCmd["give"], 0, 0, 0])
                dataOut = list(self.readDev())
                if (Config.verbose):
                    print(dataOut)
                ##dataOut = np.flip(dataOut)
                formattedData = self.formatter.fpToDec(dataOut)##check here, not ok
                block += [formattedData]
            else:
                self.sendToCard([Config.dictCmd["ready"], 0, 0, 0])
            flagRdy = not flagRdy
        self.sendToCard([Config.dictCmd["start"], 0, 0, 0])
        while self.readDev() != b'done':
            self.sendToCard([Config.dictCmd["ready"], 0, 0, 0])
            self.sendToCard([Config.dictCmd["give"], 0, 0, 0])
        else:
            self.sendToCard([Config.dictCmd["start"], 0, 0, 0])
        if (Config.verbose):
            print('block ok')
        return block

    def sendToCard(self,data):
        bytesToSend = bytearray(data)
        os.pwrite(self.fd_h2c, bytesToSend, 0)

    def readDev(self):
        data = os.pread(self.fd_c2h, 4, 0)
        if (Config.verbose):
            print(data)
        return data  # [data[3],data[2],data[1],data[0]]


def writeTest():
    x = open("eje.txt", "w")
    y = open("ejeIn.txt", "w")
    for i in range(10000):
        n = str(i+(i*1j))
        if (n != "0j"):
            n = n[1:len(n)-1]
        f = 1000
        sine = np.sin(2*np.pi*44100/f*i)
        x.write(str(sine)+'\n')
        y.write(n+'\n')
    x.close()
    y.close()


def test(onlyFormat=False):
    if not onlyFormat:
        x = mainController(mode="proc", toCardQ=queue.Queue())
        x.startExec()
    cmd = 0
    while(cmd != 'out'):
        cmd = input("CMD?: ")
        if (cmd == "pause"):
            x.doPause()
        elif (cmd == "start"):
            x.doStart()
        elif (cmd == "restart"):
            x.doRestart()
        elif (cmd == "doWrites"):
            block = [i for i in range(Config.window)]
            x.sendBlock(block)
        elif (cmd == "doReads"):
            blockOut = x.getBlock()
            print(blockOut)
        elif (cmd == "testFp"):
            formater = fpFormatter()
            x = input("ToFile?: ")
            y = input("Roots test?: ")
            formater.test(toFile=x == 'y',rootsTest=y == 'y')
        elif (cmd == "model"):
            model = DebugModel()
            model.getExpectedResult()
        else:
            print("Wot?")
    if not onlyFormat:
        x.doClose()

##test(onlyFormat=True)
##getRoots(toFile=True)
