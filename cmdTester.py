#!/usr/bin/env python3
import os
import time
import numpy

def myTest():

    size = 8
    fd_h2c = os.open("/dev/xdma0_user", os.O_WRONLY)
    fd_c2h = os.open("/dev/xdma0_user", os.O_RDONLY)
    cmd = ''
    dictCmd = {'start':1,'stop':2,'restart':3,'ready':4,'nextRe':5,'nextIm':6,'give':7,'resume':8}
    teststr = []
    test = []
    for i in range(64):
    	val = hex(i)[2:]
    	if len(val) == 1:
    		val = "0" + val
    	teststr += [val,val]
    	test += [i,i]
    x = ''.join(["00"+str(i) for i in teststr])
    print(x)
    while(cmd != 'out'):
    	cmd = input('CMD: ')
    	if (cmd == 'read'):
    		x = os.pread(fd_c2h, size,0)
    		print(x)
    	elif (cmd == 'doWrites'):
    		val1,val2 = 0,0
    		for i in range(size*2):
    			cmdByte = 0
    			if (i % 2 == 0):
    				cmdByte = dictCmd['nextRe']
    				val1,val2 = 0,1
    				print('nextRe')
    			else:
    				val1,val2 = 0,0
    				cmdByte = dictCmd['nextIm']
    				print('nextIm')
    			data = bytearray([cmdByte,0,val1,val2])##from 31->0 eje cmd = [6,0,16,9] = 09 16 00 06
    			os.pwrite(fd_h2c, data,0)
    			print("wrote: ",data)
    			x = os.pread(fd_c2h, size,0)
    			print(x)
    		os.pwrite(fd_h2c, bytearray([dictCmd['nextRe'],0,0,0]),0)
    		os.pwrite(fd_h2c, bytearray([dictCmd['nextIm'],0,0,0]),0)
    	elif (cmd == 'doReads'):
    		cmdByte = dictCmd['give']
    		for i in range(size*2):
    			cmdByte = 0
    			if (i % 2 == 0):
    				cmdByte = dictCmd['give']
    				print('give')
    			else:
    				cmdByte = dictCmd['ready']
    				print('ready')
    			data = bytearray([cmdByte,0,0,0])
    			os.pwrite(fd_h2c, data,0)
    			if (i%2 == 0):
    				x = os.pread(fd_c2h, size,0)
    				print(x[0],x[1],x[2],x[3])
    	elif (cmd != 'out'):
    		cmdByte = dictCmd[cmd]
    		data = bytearray([cmdByte,0,0,0])
    		os.pwrite(fd_h2c, data,0)
    		x = os.pread(fd_c2h, size,0)
    		print(x)
    	

##############################################    
def main():
    myTest()  

##############################################    

if __name__ == '__main__':
    main()
    
    

