from datetime import datetime

from backbone.hwCom import Config as config

import numpy as np

class fileWriter:
    file = 0
    fileSize = 0
    fileNumber = 0
    fileName = 0
    def initDump(self):
        if self.file != 0:
            self.file.close()
        self.fileSize = 0
        self.fileNumber = 1
        timeStamp = datetime.now()
        self.name = "tests/fileDump/" + timeStamp.strftime("%d-%m-%Y-%H-%M-%S")
        name = self.name + "part_" + str(self.fileNumber) + "_dump.txt"
        self.file = open(name,"w")
    def appendBlock(self,block):
        for line in block:
            if self.fileSize > config.fileMaxSize:
                if not self.changeFile():
                    return False
            dataOut = str(line)+"\n"
            self.fileSize += len(dataOut)
            self.file.write(dataOut)
        return True
    def changeFile(self):
        if self.file != 0:
                self.file.close()
        self.fileNumber += 1
        if self.fileNumber >= config.fileMax:
            if self.file != 0:
                self.file.close()
            print('Cannot write more than 10 files per continuos dump')
            return False
        name = self.name + "part_" + str(self.fileNumber) + "_dump.txt"
        self.file = open(name,"w")
        return True
    def doStop(self):
        if self.file != 0:
            self.file.close()
        self.fileSize = 0
        self.fileNumber = 0
        self.fileName = 0

class fileReader:
    file = 0
    gen = 0
    fileDone = False

    def changeFile(self, path):
        if self.file != 0:
            self.file.close()
        try:
            self.file = open(path, 'r')
        except:
            print('error opening file')
            return False
        self.gen = self.initGen()
        self.fileDone = False
        return True
    def initGen(self):
        for line in self.file:
            yield line

    def shutdown(self):
        self.file.close()

    def readChunk(self):
        block = []
        for i in range(config.window):
            try:
                n = 0
                try:
                    n = next(self.gen)
                    n = complex(n.strip('\n'))
                except ValueError:
                    print("Error en formato de archivo, revisar")
                block += [n]
            except StopIteration:
                self.fileDone = True
                block += [0]
        return np.array(block, dtype=complex)
