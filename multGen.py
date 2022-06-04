from myhdl import block, always, now, delay, always_seq, always_comb, instance
from myhdl import modbv, intbv
from myhdl import Signal, ResetSignal, ConcatSignal
import numpy as np

from fixedpoint import FixedPoint

import cmath

window = 128
operandWidth = 32
matrixSize = operandWidth*window*window
vectorSize = operandWidth*window
qformat = [4, 12]

rootMat = []
fpRoots = [[[0,0] for j in range(window)] for i in range(window)]

testing = False

def decToFp(decNum) -> list:
    mag,phase = cmath.polar(decNum)
    try:
        im = str(FixedPoint(phase, signed=True,
                 m=qformat[0], n=qformat[1]))
    except Exception:
        im = '0000'
    try:
        re = str(FixedPoint(mag, signed=True,
                 m=qformat[0], n=qformat[1]))
    except Exception:
        re = '0000'
    lowerIm = im[2:]
    higherIm = im[0:2]
    lowerRe = re[2:]
    higherRe = re[0:2]
    result = [higherRe+lowerRe,
              higherIm+lowerIm ]
    return result

def getRoots():
    global rootMat
    N_min = window
    n = np.arange(N_min)
    k = n[:, None]
    M = -2j * np.pi * n * k / N_min
    roots = np.exp(M)##np.arange(9).reshape((3,3))
    flipped = np.rot90(roots)
    rootMat = np.flip(flipped,0)

def convertToFP(dummy=True):
    i = 0
    j = 0
    for row in rootMat:
        for root in row:
            if dummy :
                reFP, imFP = 0,0
            else:
                reFP, imFP = decToFp(root)
            fpRoots[i][j][0] = reFP
            fpRoots[i][j][1] = imFP
            j+=1
        j = 0
        i+=1

getRoots()
convertToFP()
rootMat = 0

@block
def simpleAdder(clk,A,B,result):

    resultAuxIm = Signal(intbv(0)[operandWidth:])
    resultAuxRe = Signal(intbv(0)[operandWidth:])
    operAAux = Signal(intbv(0)[operandWidth:])
    operBAux = Signal(intbv(0)[operandWidth:])

    resultAddAux = ConcatSignal(resultAuxRe,resultAuxIm)
    
    @always(clk.negedge)
    def top():
        result.next = resultAddAux.signed()
        operAAux.next = A.signed()
        operBAux.next = B.signed()

    @always(clk.posedge)
    def add():
        resultAuxRe.next = operAAux[operandWidth:operandWidth//2].signed() + operBAux[operandWidth:operandWidth//2].signed()
        resultAuxIm.next = operAAux[operandWidth//2:0].signed() + operBAux[operandWidth//2:0].signed()
    
    return add,top

@block
def multiplier(clk,A,B,resultM):

    resultAuxIm = Signal(intbv(0)[operandWidth:])
    resultAuxRe = Signal(intbv(0)[operandWidth:])
    shiftValue = Signal(intbv(4)[operandWidth:])
    operAAux = Signal(intbv(0)[operandWidth:])
    operBAux = Signal(intbv(0)[operandWidth:])

    resultMultAux = ConcatSignal(resultAuxRe,resultAuxIm)
    
    @always(clk.posedge)
    def top():
        resultM.next = resultMultAux.signed()
        operAAux.next = A.signed()
        operBAux.next = B.signed()

    @always(clk.negedge)
    def mult():
        resultAuxIm.next = operAAux[operandWidth//2:0].signed() + operBAux[operandWidth//2:0].signed()
        resultAuxRe.next = operAAux[operandWidth:operandWidth//2].signed() * operBAux[operandWidth:operandWidth//2].signed() << 4
 
    return mult,top

@block
def multBlock(clk,vector,resultMultBlock):

    matriz = [0 for _ in range(window*window)]
    idxMat = 0
    for i in range(window):
        for j in range(window):
            #dummy stuff, in order to avoid any undesired optimization
            z = Signal(intbv(fpRoots[i][j][0])[operandWidth//2:])
            z = z<<operandWidth//2
            z = z + Signal(intbv(fpRoots[i][j][1])[operandWidth//2:])
            matriz[idxMat] = Signal(intbv(z)[operandWidth:])
            idxMat+=1

    matrix = ConcatSignal(*reversed(matriz))
    
    resultMult = [Signal(intbv(0)[operandWidth:]) for _ in range(window*window)]
    multiplierInst=[]

    idxMat = 0
    idxRes = 0
    for i in range(window):
        idxVector = 0
        for j in range(window):
            multiplierInst += [multiplier(clk,
                                      matrix(idxMat+operandWidth,idxMat),
                                      vector(idxVector+operandWidth,idxVector),
                                      resultMult[idxRes]
                                      )]
            idxMat += operandWidth
            idxVector += operandWidth
            idxRes += 1
            
    resultMultAux = ConcatSignal(*reversed(resultMult))
    
    @always_comb
    def top():
        resultMultBlock.next = resultMultAux

    return top,multiplierInst

@block
def adderBlock(clk,multiplierMat,resultAdderBlock):

    resultRowAdders = [ Signal(intbv(0)[operandWidth:]) for _ in range(window)]
    resultAux = [[Signal(intbv(0)[operandWidth:]) for _ in range(window-1)] for _ in range(window)]
    
    adderInst=[]
    
    idxMat = 0
    for i in range(window):
            adderInst += [
                simpleAdder(
                    clk,
                    multiplierMat(idxMat+operandWidth,idxMat),
                    multiplierMat(idxMat+(2*operandWidth),idxMat+operandWidth),
                    resultAux[i][0])]
            
            idxMat += operandWidth+operandWidth
            j = 0
            for j in range(1,window-2):
                adderInst += [
                    simpleAdder(clk,resultAux[i][j-1],
                                multiplierMat(idxMat+operandWidth,idxMat),
                                resultAux[i][j])]
                idxMat += operandWidth
                
            adderInst += [simpleAdder(clk,resultAux[i][j],
                                      multiplierMat(idxMat+operandWidth,idxMat),
                                      resultRowAdders[i])]                    
            idxMat += operandWidth

    resultRowAddersAux = ConcatSignal(*reversed(resultRowAdders))

    @always(clk.posedge)
    def snoop():
        print(resultAdderBlock)
        
    @always_comb
    def top():
        resultAdderBlock.next = resultRowAddersAux

    if testing:    
        return top,adderInst,snoop
    else:
        return top,adderInst
    
@block
def matrixMult(clk,vector,result):
    
    resultMult = Signal(intbv(0)[matrixSize:])
    
    theMultipliers = multBlock(clk,vector,resultMult)
    theAdders = adderBlock(clk,resultMult,result)
        
    return theAdders,theMultipliers

@block
def testAdder(vectorIn,resultOut):

    HALF_PERIOD = delay(10)
    PERIOD = delay(20)
    clk  = Signal(bool(0))

    dut = matrixMult(clk,vectorIn,resultOut);
    
    @instance
    def check():
        while 1:
            yield HALF_PERIOD
            clk.next = not clk
            input("tick")
            
    return dut, check

opt = input("do test?")

if (opt == "y"):
    testing = True
    fs = 44100
    f = 3000
    samplesEje = [np.sin(2*np.pi*fs/f*i) for i in range(window)]
    
    def FFT_noNp(x):
        x = np.asarray(x, dtype=float)
        N = x.shape[0]
        N_min = window
        n = np.arange(N_min)
        k = n[:, None]
        M = -2j * np.pi * n * k / N_min
        M = np.exp(M)
        X = np.dot(M, x.reshape((N_min, -1)))
        return X.ravel()
    print(FFT_noNp(samplesEje))
    samplesAux = intbv(0)[vectorSize:]
    idxVector = 0
    for n in samplesEje:
        re,im = decToFp(n)
        samplesAux[idxVector+operandWidth-(operandWidth/2):idxVector] = int(re,16)
        samplesAux[idxVector+operandWidth:idxVector] = int(im,16)
        idxVector += operandWidth
    samplesAux = intbv(0)[vectorSize:]
    samplesAux = Signal(samplesAux)
    result = Signal(intbv(0)[vectorSize:])
    tb = testAdder(samplesAux,result)
    tb.name = "mySimInst"
    tb.config_sim(trace=True)
    tb.run_sim(duration=None)
    tb.run_sim()
else:
    clk  = Signal(bool(0))
    result = Signal(intbv(0)[vectorSize:])
    vector = Signal(intbv(0)[vectorSize:])
    dut = matrixMult(clk,vector,result)
    dut.convert(hdl='Verilog')
    file = open('constant','w')
    rootMat = []
    fpRoots = [[[0,0] for j in range(window)] for i in range(window)]
    getRoots()
    convertToFP(dummy=False)
    file.write("assign multBlock0_matrix = " + str(matrixSize)+"'sh")
    for row in fpRoots:
        for root in row:
            file.write(root[0]+root[1])
    file.write(";\n")
    file.close()
            
    
    
    
