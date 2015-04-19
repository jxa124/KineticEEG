"""This module gets the data from Emotiv"""
import ctypes
import sys
sys.path.append("C:/Users/Gaurav/My Documents/GitHub/KineticEEG/KineticEEG")
import Preprocessers
import os
import numpy
os.chdir("C:/Program Files (x86)/Emotiv Education Edition SDK v2.0.0.20/dll/32 bit")
EdkDLL=ctypes.cdll.LoadLibrary("C:/Program Files (x86)/Emotiv Education Edition SDK v2.0.0.20/dll/32 bit/edk.dll")
class EmotivDataGetter:
    def __init__(self):
        self.eEvent=EdkDLL.EE_EmoEngineEventCreate()
        self.eState=EdkDLL.EE_EmoStateCreate()
        self.userID=ctypes.c_uint(0)
        self.seconds=ctypes.c_float(1)
        self.nSamples=int(0)
        self.nSamplesTaken=ctypes.pointer(ctypes.c_uint(self.nSamples))
        self.fin_data=list([[],[],[],[],[],[],[],[],[],[],[],[],[],[]])
    def mainloop(self):
        EdkDLL.EE_EngineConnect(b"Emotiv Systems-5")
        self.hData=EdkDLL.EE_DataCreate()
        EdkDLL.EE_DataSetBufferSizeInSec(ctypes.c_float(1.0))
        while(1):
            state=EdkDLL.EE_EngineGetNextEvent(self.eEvent)
            if state==0:
                eventType=EdkDLL.EE_EmoEngineEventGetType(self.eEvent)
                EdkDLL.EE_EmoEngineEventGetUserId(self.eEvent, ctypes.pointer(self.userID))
                if eventType==16:
                    EdkDLL.EE_DataAcquisitionEnable(self.userID,True)
                    self.readytocollect = True
                if self.readytocollect:
                    EdkDLL.EE_DataUpdateHandle(0, self.hData)
                    EdkDLL.EE_DataGetNumberOfSample(self.hData, self.nSamplesTaken)
                    if self.nSamplesTaken[0]!=0:
                        nSam=self.nSamplesTaken[0]
                        arr=(ctypes.c_double*self.nSamplesTaken[0])()
                        ctypes.cast(arr, ctypes.POINTER(ctypes.c_double))
                        data=numpy.array("d")
                        for sampleIdx in range(self.nSamplesTaken[0]):
                            for i in range(14): 
                                EdkDLL.EE_DataGet(self.hData,[3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16][i],ctypes.byref(arr), nSam)
                                self.fin_data[i].append(arr[sampleIdx])
                            if len(self.fin_data[0])>=1024:
                                #for p in self.fin_data[3]:
                                    #print(p)
                                self.data_processor=Preprocessers.DataProcessor(self.fin_data)
                                self.data_processor.do_high_pass()
                                self.data_processor.do_hanning_wndow()
                                self.data_processor.do_bin_power()
                                print(self.data_processor.data_dict["FC5"][1][0])
                                
if __name__=='__main__':
    g=EmotivDataGetter()
    g.mainloop()
                                
                                
                        
                                    
                                    
                                    
                                
                        
                        
                        
        
        
        
    
        
        
        