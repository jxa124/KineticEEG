import time
import sys
sys.path.append("C:/Users/Gaurav/Documents/GitHub/KineticEEG/KineticEEG")
sys.path.append("C:/Users/Gaurav/Documents/GitHub/KineticEEG/Tools")
import PreprocessUtils
import matplotlib.pyplot as plt
import numpy
import CSV_Extractor
import time
FILE="C:/Users/Gaurav/Documents/CSV/Done/Zander -1-12.02.15.13.18.23.CSV"   
FFT_SIZE=1024
STEP_SIZE=16
FFT_SENSOR="AF3"
def bplot(file, sensor, rects1, a, fig):
    goodlist=list()
    tree=list()
    counter=float()
    while not len(tree)==FFT_SIZE:
       print("s")
       stuff=a.get128more(sensor)
       tree+=stuff
       time.sleep(1)
       counter+=1
    while True:
        inittime=time.time()
        artree=PreprocessUtils.highpass(tree)
        win32=numpy.hanning(1024)
        artree=numpy.array(artree)
        stuff1=win32*artree
        stuff2=PreprocessUtils.bin_power(stuff1, [1,4,7,13,30], 128)
        stuff4=abs(20*numpy.log(stuff2))
        stuff5=tuple(stuff4[0])
        print(str(stuff5)+"-"+str(counter))        
        goodlist.append(stuff5)
        del tree[0:16]
        more16=a.get16more(sensor)
        tree+=more16
        time.sleep((0.125-(time.time()-inittime)))
        counter+=(0.125)
fig, ax=plt.subplots()
rects1=ax.bar([0,1,2,3], (0,0,0,0),1)
plt.ylim(105, 112)
plt.ion()
win=fig.canvas.manager
a=CSV_Extractor.CSVExtractor(FILE)
plt.show()
bplot(file,FFT_SENSOR, rects1, a, fig)
        
        
    
    
       
       
        
