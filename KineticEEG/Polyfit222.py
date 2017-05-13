import numpy
import numpy.polynomial as poly
import ClassifyUtils
import multiprocessing
import BaseEEG
import statistics
import ctypes
import itertools
import kFoldCrossValidation2
import statistics
import time
import pickle
kernel=ctypes.windll.kernel32

""""    def train(self, data):
        for i in data:
            curr_dat={}
            for j in data[i]:
                #self.mat[i][j].append(poly.polynomial.Polynomial(poly.polynomial.polyfit(list(range(len(data[i][j]))), data[i][j], self.deg)))
                curr_dat[j]=poly.polynomial.Polynomial(poly.polynomial.polyfit(list(range(len(data[i][j]))), data[i][j], self.deg))
            self.mat[i].append(Sample(i, curr_dat))
                
    def classify(self, data):
        mat2={}
        for i in data:
                mat2[i]=poly.polynomial.Polynomial(poly.polynomial.polyfit(list(range(len(data[i]))), data[i], self.deg))
        data_samp=Sample("", mat2)
        output=self.k_nn(data_samp)
        k=4
        sorts=sorted(output, key=lambda x:x[1], reverse=True)
        top_k=sorts[0:10]
        top_k_labels=[j[0] for j in top_k]
        #print(sorts, "sorts")
        #print(len(top_k_labels), "Up")
        try:
            return statistics.mode(top_k_labels)
            #print(len(top_k_labels))
        except:
            return "neutral"""
class Sample:
    def __init__(self, label, data):
        self.data=data
        self.label=label
    def euclidean_distance_between(self, other):
        tote=0
        for i in self.data:
            tote+=ClassifyUtils.euclideandistance(self.data[i].coef, other.data[i].coef, len(self.data[i].coef))
        return tote
class ErrorDetectionAlgorithm:
    """This is a k-Nearest Neighbor Classifier to find the erronous classifications made"""
    def __init__(self, classifier, kfoldresults):
        '''kfoldresults is a tuple containing the different fields ending in class (CORRECT/INCORRECT)'''
        self.classifier=classifier
        self.kfoldresults=kfoldresults
        #print(len(self.kfoldresults))
    def classify(self, sample):
        results=self.classifier.smart_algo(sample)
        results=results[1:3]
        self.results=[]
        for i in self.kfoldresults:
            self.results.append([ClassifyUtils.euclideandistance(i[0:2], results,2), i[-1]])
        self.results=sorted(self.results, key=lambda x:x[0])
        listy=list()
        for i in self.results[0:10]:
            if not i[0]==0:
                listy.append(i[-1])
        try:
            guess=statistics.mode(listy)
        except:
            guess='tie'
        return guess

def RunErrorDetectionApp(file, deg):
    crossval=kFoldCrossValidation2.kFoldCrossValidationRunner2(100,PolyBasedClassifier, deg)
    output=crossval.run_for_errors()
    jk=ErrorDetectionAlgorithm(crossval.temp, output)
    
        
        
            
        
class PolyBasedClassifier:
    def __init__(self,degree, actions=["arm", "kick", "neutral"]):
        self.mat={} #self.mat will contain the data for each action, for each variable.
        self.deg=degree #Degree of fit
        self.actions=actions #List of actions.
        for i in actions:self.mat.update({i:[]})
        for i in self.actions:self.mat.update({i:{"F3":[], "F4":[], "FC5":[], "FC6":[]}})#Set up data structure per action, per sensor
    def train(self, data):
        for i in data: #i will equal the current action 
            for j in data[i]:#j is the current sensor 
                self.mat[i][j].append(poly.polynomial.Polynomial(poly.polynomial.polyfit(list(range(len(data[i][j]))), data[i][j], self.deg))) #Supply the data for a polynomial fit(seconds vs EEG Mu wave power)
    def classify(self, data):
        mat2={}
        for i in data:
                mat2[i]=poly.polynomial.Polynomial(poly.polynomial.polyfit(list(range(len(data[i]))), data[i], self.deg))
                #mat2[i]=data[i]
        output=self.k_nn_old(mat2)
        num=abs(sorted(output, key=lambda x:x[1])[0][1]-sorted(output, key=lambda x:x[1])[1][1])
        return [min(output, key=lambda x:x[1]), num]
    def cross_classify(self, data, rule_vectors):
        results=dict()
        for i in rule_vectors:
            for j in i:
                results[i]=(i,ClassifyUtils.euclideandistance(data[j].coef, rule[i][j],len(rule[i][j])))
        return min(results, key=lambda x: results[x][1])
        

                
        
    def smart_algo_2(self, data):
    
        matp={"F3":[], "F4":[], "FC5":[], "FC6":[]} #Data structrure for the incoming data(Multiple pieces of data not needed)
        mat2={}#dictionary
        #for i in self.actions:mat2.update({i:{"F3":[], "F4":[], "FC5":[], "FC6":[]}})
        throttle={}
        rule={}
        boundarypoints={"arm":{}, 'kick':{}}
        for i in ['arm', 'kick']:
            #print(i)
            
            for j in self.mat[i]:
                #print(mat[i][j])
                initlist=[]
                for p in itertools.combinations(self.mat[i][j], 2):
                    #print(str(i+"v"+j))
                    initlist.append(ClassifyUtils.euclideandistance(p[0].coef, p[1].coef, len(p[1].coef)))
                #print(str(i+"v"+j))
                boundarypoints[i][j]=initlist
                matp[j].append(statistics.mean(initlist))
                
            #for b in matp:
            #print(len(self.mat['kick']['FC5']))
        for i in ['arm', 'kick','neutral']:
            minst=min(matp, key=lambda x:statistics.mean(matp[x]))
            #print(minst)
            matr=numpy.matrix([i.coef for i in self.mat[i][minst]])
            final=list()
            #rule[minst]=[]
            for j in matr.T:
                #print(j)
                final.append(statistics.mean(numpy.array(j).flatten()))
                #print(Final")
            rule[i]={minst:final}
        for p in data:
            mat2[p]=poly.polynomial.Polynomial(poly.polynomial.polyfit(list(range(len(data[p]))), data[p], self.deg))
        for d in ['arm', 'kick']:
            #print(d)
            for tt in rule[d]:
                sum1=0
                #for ppp in rule[d][tt]:
                sum1+=ClassifyUtils.euclideandistance(mat2[tt].coef, rule[d][tt],len(rule[d][tt]))
                    
                throttle[d]=(sum1/1)
        #print(boundarypoints)
        if throttle[min(throttle, key=lambda x:throttle[x])]>(numpy.percentile(boundarypoints[min(throttle, key=lambda x:throttle[x])][minst],95)+(2*statistics.stdev(boundarypoints[min(throttle, key=lambda x:throttle[x])][minst]))):
            #print("Hi")
            return [["neutral"]]
            

                 
                
    
        return [[min(throttle, key=lambda x:throttle[x])], throttle[min(throttle, key=lambda x:throttle[x])]-throttle[sorted(throttle, key=lambda x:throttle[x])[1]],throttle[min(throttle, key=lambda x:throttle[x])] ]
        
            
        

        
    def smart_algo(self, data):
    
        matp={"F3":[], "F4":[], "FC5":[], "FC6":[]}#Data structrure for the incoming data(Multiple pieces of data not needed)
        mat2={}
        #for i in self.actions:mat2.update({i:{"F3":[], "F4":[], "FC5":[], "FC6":[]}})
        throttle={}
        rule={}
        for i in ['arm', 'kick', "neutral"]:#Associative rule mining phase
            for j in self.mat[i]:# for sensor in action(j is the current sensor)
                initlist=[]#initlist is a list which one will append the distances alculated to.This is done for statistical purposes
                for p in itertools.combinations(self.mat[i][j], 2):#For the 6 choose two combinations of two polynomial object ifor a given movement, sensor
                    initlist.append(ClassifyUtils.euclideandistance(p[0].coef, p[1].coef, len(p[1].coef)))#Append the euclidean distance between the two .
                matp[j].append(statistics.mean(initlist))#Append the mean of all of the distances for this sensor.
        for i in ['arm', 'kick','neutral']:#Going through each action
            minst=min(matp, key=lambda x:statistics.mean(matp[x]))# Find the most clustered sensor by finding the minimum average distance over the three actions.
            matr=numpy.matrix([p.coef for p in self.mat[i][minst]])#Creation of a numpy matrix 
            final=list()#List to contain rules.
            for j in matr.T: #Transposition of the m
                final.append(statistics.mean(numpy.array(j).flatten()))#Flatten the row and average it in order to create the rule vector.
            rule[i]={minst:final}
        for p in data: #Exit Training phase, begin work on live data.
            mat2[p]=poly.polynomial.Polynomial(poly.polynomial.polyfit(list(range(len(data[p]))), data[p], self.deg))#Featurize(find the polynomial fit of) the data
        for d in rule: #Classification phase-Iterate over actions
            for tt in rule[d]: #Iterate over sensor(ONly one sensor, no true iteration)
                sum1=0#Assign variable
                #for ppp in rule[d][tt]:
                sum1+=ClassifyUtils.euclideandistance(mat2[tt].coef, rule[d][tt],len(rule[d][tt]))#Add the Euclidean Distance between sample and rule
                    
                throttle[d]=(sum1/1)#append information to dictionary
                
    
        return [[min(throttle, key=lambda x:throttle[x])],
                throttle[min(throttle, key=lambda x:throttle[x])]-throttle[sorted(throttle, key=lambda x:throttle[x])[1]],throttle[min(throttle, key=lambda x:throttle[x])] ] #Return classification.
        
            
                
    def smart_algo_neutral(self, data):
    
        matp={"F3":[], "F4":[], "FC5":[], "FC6":[]}
        mat2={}
        throttle={}
        min_sensor=list()
        rule={}
        for i in ['arm', 'kick']:
            #print(i)
            
            for j in self.mat[i]:
                #print(mat[i][j])
                initlist=[]
                for p in itertools.combinations(self.mat[i][j], 2):
                    #print(str(i+"v"+j))
                    initlist.append(ClassifyUtils.euclideandistance(p[0].coef, p[1].coef, len(p[1].coef)))
                #print(str(i+"v"+j))
                matp[j].append(statistics.mean(initlist))
            #for b in matp:
            #print(len(self.mat['kick']['FC5']))
            minst=min(matp, key=lambda x:statistics.mean(matp[x]))
            min_sensor.append(minst)
            matp={"F3":[], "F4":[], "FC5":[], "FC6":[]}
            #print(minst)
            #print(self.mat[
            matr=numpy.matrix([t.coef for t in self.mat[i][minst]])
            final=list()
            #rule[minst]=[]
            for j in matr.T:
                #print(j)
                final.append(statistics.mean(numpy.array(j).flatten()))
                #print(Final")
            rule[i]={minst:final}
        for i in ['neutral']:
            subdict=dict()
            for j in list(set(min_sensor)):
                matr=numpy.matrix([t.coef for t in self.mat[i][j]])
                final=list()
                
                for q in matr.T:
                    #print(j)
                    final.append(statistics.mean(numpy.array(q).flatten()))
                    #print(Final")
                subdict[j]=final
            rule[i]=subdict
            
                
                
                
            #print(rule)
        for p in data:
            mat2[p]=poly.polynomial.Polynomial(poly.polynomial.polyfit(list(range(len(data[p]))), data[p], self.deg))
        for d in ['arm', 'kick']:
            #print(d)
            sum1=0
            for tt in rule[d]:
                
                #print(d,tt)
                #for ppp in rule[d][tt]:
                sum1+=ClassifyUtils.euclideandistance(mat2[tt].coef, rule[d][tt],len(rule[d][tt]))
                    
                throttle[d]=(sum1/1)
        for d in ['neutral']:
            minlist=list()
            for tt in rule[d]:
                minlist.append(ClassifyUtils.euclideandistance(mat2[tt].coef, rule[d][tt],len(rule[d][tt])))
            throttle[d]=max(minlist)
                
                

                
                
                
        #print(matp)
        return [[min(throttle, key=lambda x:throttle[x])], throttle[min(throttle, key=lambda x:throttle[x])]-throttle[sorted(throttle, key=lambda x:throttle[x])[1]],throttle[min(throttle, key=lambda x:throttle[x])] ]
        
            
                
            
            
            

    def k_nn_old(self, data):
        pp=[]
        totallist=[]
        for i in self.mat:
            total=0
            for m in self.mat[i]:
                totallist.clear()
                #print(self.mat[i][m])
                for j in list(sorted(self.mat[i][m], key=lambda x:ClassifyUtils.euclideandistance(x.coef, data[m].coef, self.deg+1))):
                    totallist.append(ClassifyUtils.euclideandistance(j.coef, data[m].coef, self.deg+1))
                #totallist.append(0)
                if 0 in totallist:print("OOps")
                totallist=list(filter(lambda x: (x>=(statistics.mean(totallist)-3*statistics.stdev(totallist)) and x<=(statistics.mean(totallist)+3*statistics.stdev(totallist))), totallist))
                
                
                total+=sum(totallist)
            pp.append(tuple((i, total)))
        return pp
    def k_nn(self, data):
        pp=[]
        #print(len(self.mat['arm']['F3']),"Mat")
        for i in self.mat:
            
            for m in self.mat[i]:
                pp.append((i,m.euclidean_distance_between(data)))
               
        return pp
    
class MultiLiveClassifierApplication:
    def __init__(self, process1, process2, q,  profile,subprocessed=False):
        self.getter=process1
        self.profile=profile
        self.q=q
        self.dict_data=pickle.loads(profile.read())
        self.classifiers=dict()
        unpacked=list()
        for b in self.dict_data:
            unpacked+=self.dict_data[b]
        self.classif=PolyBasedClassifier(12)
        #for q in self.dict_data:
           # self.classif.train(self.dict_data[q])
        self.processer=process2
        for j in unpacked:
            self.classif.train({j.label: j.data})
        #self.thresh,self.d=self.calculate_thresh()
        #print("#####THRESHOLD="+str(self.thresh))
        self.system_up_time=0
    def calculate_thresh(self):
          thresh_select=list()
          for i in self.dict_data:
               for j in self.classifiers:
                    if not j==i:
                         thresh_select.append(self.classifiers[j].test_classifiers_ret(self.dict_data[i]))
          return (max(thresh_select), sorted(thresh_select)[-1]-sorted(thresh_select)[-2])
    def normalized(self, tt):
        return statistics.mean(tt)#*(1-statistics.stdev(tt))
    def car(self,data_dict):
         pp=numpy.matrix([data_dict[j] for j in data_dict])
         #print(pp)
         count=0
         for j in pp.T:
             avg=statistics.mean(numpy.array(j).flatten())
             for p in data_dict:
                 #print(data_dict[p][count])
                 data_dict[p][count]-=avg
             count+=1
         return data_dict
    def runAppSubprocessedDiffAlgo(self):
        self.getter.start()
        getpid=self.getter.pid
        procget=kernel.OpenProcess(ctypes.c_uint(0x0200|0x0400), ctypes.c_bool(False), ctypes.c_uint(getpid))
        kernel.SetPriorityClass(procget, 0x0100)
        #self.classproc.start()
        classpid=self.getter.pid
        self.thresh=0.825
        proclass=kernel.OpenProcess(ctypes.c_uint(0x0200|0x0400), ctypes.c_bool(False), ctypes.c_uint(classpid))
        kernel.SetPriorityClass(proclass, 0x0100)
        self.processer.start()
        procpid=self.processer.pid
        procproc=kernel.OpenProcess(ctypes.c_uint(0x0200|0x0400), ctypes.c_bool(False), ctypes.c_uint(procpid))
        kernel.SetPriorityClass(procproc, 0x0100)
        data_dict=dict({"F3":[], "F4":[], "FC5":[], "FC6":[]})
        countr=0
        switch_countr=0
        switch=False
        average_q={"kick":[self.thresh], "arm":[self.thresh], "neutral":[self.thresh]}
        running_q={"kick":[], "arm":[], "neutral":[]}
        print("Enter Loop")
        runloop=[]
        try:
            print("in")
            while self.getter.is_alive():
                data=self.q.recv()
                #print(data)
                for i in data_dict:
                    data_dict[i].append(data[i][0][2])
                countr=countr+1
                if len(data_dict["F3"])==32:                   #print("In Detector")
                    
                    #if (countr%4)==0:
                         #print("Here")
                         #self.classq.send(data_dict)
                         #res=self.classq.recv()
                         #print("recv...")
                         #p=multiprocessing.Pool()
                         #a.move_mouse(a.get_mouse_pos()[0], a.get_mouse_pos()[1]+2)
                        # res=map(classify_func,res)
                         #print(list(res))
                         #res1=list(res)
                     #print(data_dict)
                     #print(self.car(data_dict))
                     print(self.classif.smart_algo(self.car(data_dict))[0][0])
                     for i in data_dict:
                        del data_dict[i][0:32]
                     #time.sleep(1)
            
                         #countr+=1
                         #print(countr)
##                    if (countr%4)==0:
##                        
##                        try:
##                            print(statistics.mode(runloop))
##                            
##                        except:
##                            print("Neutral")
                        #runloop=[]
                         #print (len(res1))
                         #print(res)
                         #for i in res:
                              #average_q[i[0]].append(i[1])
                              #print("Here1")
                              #if len(running_q[i[0]])==3:
                                   #print("Hi")
                                   #del running_q[i[0]][0]
                              #running_q[i[0]].append(i[1])
                         #final_list=list()
                         #if len(running_q["arm"])<3:continue
                         #for i in running_q:
                             #print(running_q[i])
##                             curr_avg=numpy.average(running_q[i], weights=[1,4,9])
##                             if curr_avg>self.thresh:
##                                 final_list.append(tuple((i, curr_avg)))
                                 
                         
##                         final_list=list()
##                         for i in average_q:
##                              
##                              #print("Here3")
##                              if not highpass(running_q[i])[-1] in curr_ar and highpass(running_q[i])[-1]>curr_ar.miny:
##                                   final_list.append(tuple((i,highpass(running_q[i])[-1])))
##                         if len(final_list)==0:
##                              #print("Here4")
##                              continue
##                         if not switch_countr==3 and switch==True:
##                             switch_countr+=1
##                             continue
##                         if switch_countr==3 and switch ==True:
##                            switch_countr=0
##                            switch=False
##                            continue
##                         if len(final_list)==1:
##                              percent=final_list[0][1]
##                              #print("Here5")
##                              #percent=abs(percent-statistics.mean(average_q[final_list[0][0]]))
##                              percent=abs(percent-self.thresh)
##                              #print(str(max(res, key=lambda x:x[1])[0])+str(sorted(res, key=lambda x:x[1])[-1][1]-sorted(res, key=lambda x:x[1])[-2][1])+str("\n"))
##                              if max(res, key=lambda x:x[1])[0]=="kick":
##                                   switch=True
##                                   a.move_mouse(a.get_mouse_pos()[0], int(a.get_mouse_pos()[1]+(abs(percent*100*60))))
##                                   print("Kick"+str(percent))
##                              else:
##                                    switch=True
##                                    print("arm"+str(percent))
##                                    a.move_mouse(a.get_mouse_pos()[0], int(a.get_mouse_pos()[1]-(abs(percent*100*60))))
##                         else:
##                              maxy=max(final_list, key=lambda x:x[1])
##                              percent=final_list[0][1]
##                              percent=abs(percent-self.thresh)
##                              #percent=abs(float(maxy[1])-float(statistics.mean(float(average_q[maxy[0]]))))
##                              if maxy[0]=="kick":
##                                   switch=True
##                                   print("kick"+str(percent))
##                                   a.move_mouse(a.get_mouse_pos()[0], int(a.get_mouse_pos()[1]+(abs(percent*100*60))))
##                              else:
##                                  switch=True
##                                  print("arm"+str(percent))
##                                  a.move_mouse(a.get_mouse_pos()[0], int(a.get_mouse_pos()[1]-(abs(percent*100*60))))
##                         
##                              #if max(res, key=lambda x:x[1])[1]>=0.825 and not max(res, key=lambda x:x[1])[0]=="neutral" and (sorted(res, key=lambda x:x[1])[-1][1]-sorted(res, key=lambda x:x[1])[-2][1])>self.d:
##
##                                   
                                   
                         
                    #countr=0
                    #print(data_dict)
                    
                #print(time.time())
                #self.system_up_time+=16/128
        except:
            self.getter.terminate()
            #self.classproc.terminate()
            self.processer.terminate()
            raise

    def runAppSubprocessed(self):
        self.getter.start()
        getpid=self.getter.pid
        procget=kernel.OpenProcess(ctypes.c_uint(0x0200|0x0400), ctypes.c_bool(False), ctypes.c_uint(getpid))
        kernel.SetPriorityClass(procget, 0x0100)
        self.classproc.start()
        classpid=self.getter.pid
        proclass=kernel.OpenProcess(ctypes.c_uint(0x0200|0x0400), ctypes.c_bool(False), ctypes.c_uint(classpid))
        kernel.SetPriorityClass(proclass, 0x0100)
        self.processer.start()
        procpid=self.processer.pid
        procproc=kernel.OpenProcess(ctypes.c_uint(0x0200|0x0400), ctypes.c_bool(False), ctypes.c_uint(procpid))
        kernel.SetPriorityClass(procproc, 0x0100)
        data_dict=dict({"F3":[], "F4":[], "FC5":[], "FC6":[]})
        countr=0
        switch_countr=0
        switch=False
        average_q={"kick":[self.thresh], "arm":[self.thresh], "neutral":[self.thresh]}
        running_q={"kick":[], "arm":[], "neutral":[]}
        print("Enter Loop")
        try:
            while self.getter.is_alive():
                data=self.q.recv()
                #print(data)
                for i in data_dict:
                    data_dict[i].append(data[i][0][2])
                countr=countr+1
                if len(data_dict["F3"])==32:                   #print("In Detector")
                    for i in data_dict:
                        del data_dict[i][0]
                    if (countr%4)==0:
                         self.classq.send(data_dict)
                         res=self.classq.recv()
                         #p=multiprocessing.Pool()
                         #a.move_mouse(a.get_mouse_pos()[0], a.get_mouse_pos()[1]+2)
                        # res=map(classify_func,res)
                         #print(list(res))
                         res1=list(res)
                         #print (len(res1))
                         #print(res)
                         for i in res:
                              average_q[i[0]].append(i[1])
                              #print("Here1")
                              if len(running_q[i[0]])==3:
                                   #print("Hi")
                                   del running_q[i[0]][0]
                              running_q[i[0]].append(i[1])
                         #print("Here2")
                         final_list=list()
                         for i in average_q:
                              if len(average_q[i])<=1:
                                   curr_ar=SLICERZ.Area(highpass(average_q[i])[-1], 0)
                              else:
                                   curr_ar=SLICERZ.Area(highpass(average_q[i])[-1], 1*statistics.stdev(highpass(average_q[i])))
                              #print("Here3")
                              if not highpass(running_q[i])[-1] in curr_ar and highpass(running_q[i])[-1]>curr_ar.miny:
                                   final_list.append(tuple((i,highpass(running_q[i])[-1])))
                         if len(final_list)==0:
                              #print("Here4")
                              continue
                         if not switch_countr==3 and switch==True:
                             switch_countr+=1
                             continue
                         if switch_countr==3 and switch ==True:
                            switch_countr=0
                            switch=False
                            continue
                         if len(final_list)==1:
                              percent=final_list[0][1]
                              #print("Here5")
                              #percent=abs(percent-statistics.mean(average_q[final_list[0][0]]))
                              percent=abs(percent-highpass(average_q[final_list[0][0]])[-1])
                              #print(str(max(res, key=lambda x:x[1])[0])+str(sorted(res, key=lambda x:x[1])[-1][1]-sorted(res, key=lambda x:x[1])[-2][1])+str("\n"))
                              if max(res, key=lambda x:x[1])[0]=="kick":
                                   switch=True
                                   a.move_mouse(a.get_mouse_pos()[0], int(a.get_mouse_pos()[1]+(abs(percent*100*60))))
                                   print("Kick"+str(percent))
                              else:
                                    switch=True
                                    print("arm"+str(percent))
                                    a.move_mouse(a.get_mouse_pos()[0], int(a.get_mouse_pos()[1]-(abs(percent*100*60))))
                         else:
                              maxy=max(final_list, key=lambda x:x[1])
                              percent=final_list[0][1]
                              percent=abs(percent-highpass(average_q[final_list[0][0]])[-1])
                              #percent=abs(float(maxy[1])-float(statistics.mean(float(average_q[maxy[0]]))))
                              if maxy[0]=="kick":
                                   switch=True
                                   print("kick"+str(percent))
                                   a.move_mouse(a.get_mouse_pos()[0], int(a.get_mouse_pos()[1]+(abs(percent*100*60))))
                              else:
                                  switch=True
                                  print("arm"+str(percent))
                                  a.move_mouse(a.get_mouse_pos()[0], int(a.get_mouse_pos()[1]-(abs(percent*100*60))))
                         
                              #if max(res, key=lambda x:x[1])[1]>=0.825 and not max(res, key=lambda x:x[1])[0]=="neutral" and (sorted(res, key=lambda x:x[1])[-1][1]-sorted(res, key=lambda x:x[1])[-2][1])>self.d:

                                   
                                   
                         countr+=1
                    #countr=0
                    #print(data_dict)
                    
                #print(time.time())
                self.system_up_time+=16/128
        except:
            self.getter.terminate()
            self.classproc.terminate()
            self.processer.terminate()
            raise

    def runApp(self):
        self.getter.start()
        getpid=self.getter.pid
        procget=kernel.OpenProcess(ctypes.c_uint(0x0200|0x0400), ctypes.c_bool(False), ctypes.c_uint(getpid))
        kernel.SetPriorityClass(procget, 0x0100)
        self.processer.start()
        procpid=self.processer.pid
        procproc=kernel.OpenProcess(ctypes.c_uint(0x0200|0x0400), ctypes.c_bool(False), ctypes.c_uint(procpid))
        kernel.SetPriorityClass(procproc, 0x0100)
        data_dict=dict({"F3":[], "F4":[], "FC5":[], "FC6":[]})
        countr=0
        try:
            while self.getter.is_alive():
                data=self.q.recv()
                #print(data)
                for i in data_dict:
                    data_dict[i].append(data[i][0][2])
                countr=countr+1
                if len(data_dict["F3"])==32:
                    #print("In Detector")
                    for i in data_dict:
                        del data_dict[i][0]
                    #if (countr%4)==0:
                   # res=[(tr, self.classifiers[tr].test_classifiers_ret(data_dict)) for tr in self.classifiers]
                    #p=multiprocessing.Pool()
                    
                   # res=map(classify_func,res)
                    #print(list(res))
                    #res1=list(res)
                    #print (len(res1))
                    #if max(res, key=lambda x:x[1])[1]>=0.85 and not max(res, key=lambda x:x[1])[0]=="neutral":
                        # print(str(max(res, key=lambda x:x[1])[0])+str(max(res, key=lambda x:x[1])))
                    #countr=0
                    #print(data_dict)
                    
                print(time.time())
                self.system_up_time+=16/128
        except:
            self.getter.terminate()
            self.processer.terminate()
            raise
    
class MultiLiveTrainingDataGatherer:
     def __init__(self, process1,process2,q,dumpto, qevents,k):
        self.getter=process1
        self.q=q
        self.events=qevents
        self.k=k
        self.processer=process2
     def car(self,data_dict):
         pp=numpy.matrix([data_dict[j] for j in data_dict])
         count=0
         for j in pp.T:
             avg=statistics.mean(numpy.array(j).flatten())
             for p in data_dict:
                 data_dict[p][count]-=avg
             count+=1
     def runApp(self):
        self.getter.start()
        getpid=self.getter.pid
        procget=kernel.OpenProcess(ctypes.c_uint(0x0200|0x0400), ctypes.c_bool(False), ctypes.c_uint(getpid))
        kernel.SetPriorityClass(procget, 0x0100)
        self.processer.start()
        procpid=self.processer.pid
        procproc=kernel.OpenProcess(ctypes.c_uint(0x0200|0x0400), ctypes.c_bool(False), ctypes.c_uint(procpid))
        kernel.SetPriorityClass(procproc, 0x0100)
        sampslist=dict()
        data_dict=dict()
        count=0
        for i in self.events:
            sampslist[i]=[]
        for k in range(self.k):
            for i in self.events:
                data_dict[i]={"F3":[], "F4":[], "FC5":[], "FC6":[]}
            
            for tp in data_dict:
                
                print(tp)
                #time.sleep(1)
                first=bool(True)
                
                try:
                    while self.getter.is_alive():
                        #print(data_dict)
                        #print(data_dict[tp])
                        data=self.q.recv()
                        if first:
                            
                            #print(tp)
                            #time.sleep(1)
                            data=self.q.recv()
                            first=False
                        for i in data_dict[tp]:
                            data_dict[tp][i].append(data[i][0][2])
                        if len(data_dict[tp]["F3"])==32:
                            for i in data_dict[tp]:
                                del data_dict[tp][i][0]
                            raise KeyboardInterrupt
                        
                            
                        print(time.asctime())
                except:
                    for i in range(32):
                         self.q.recv()
                    if not count==3:
                        continue
            count=0
            for pl in data_dict:
##                pp=numpy.matrix([data_dict[pl][j] for j in data_dict[pl]])
##                count=0
##                for j in pp.T:
##                    avg=statistics.mean(j)
##                    for p in data_dict[pl]:
##                        data_dict[pl][p][count]-=avg
##                    count+=1
                    
                sampslist[pl].append(Sample(pl, data_dict[pl]))
                print("j")
            print("Train Done")
                
                    
                    
                    ###print("Train Done")
                    
                   # raise
        self.getter.terminate()
        self.processer.terminate()
        for j in sampslist:
            for p in sampslist[j]:
                print(p.data)
                self.car(p.data)
                print(p.data)
        fileobj=open("C:/Users/Gaurav/Desktop/KineticEEGProgamFiles/Trainingdata.kineegtr", "wb")
        fileobj.write(pickle.dumps(sampslist))
        fileobj.close()
                            
            
            
def MultiDataGather():
    q,q1=multiprocessing.Pipe()
    getter=multiprocessing.Process(target=BaseEEG.run_data_getter_processer, args=(q1,))
    q2, q3=multiprocessing.Pipe()
    processor=multiprocessing.Process(target=BaseEEG.exec_proc, args=(q, q2, 1))
    #myApp=LiveClassifierApplication(getter, processor, q3, open("C:/Users/Gaurav/Desktop/KineticEEGProgamFiles/Trainingdata.dat", "rb"))
    myApp=MultiLiveTrainingDataGatherer(getter, processor, q3, open("C:/Users/Gaurav/Desktop/KineticEEGProgamFiles/Trainingdata.kineegtr", "wb"),["kick", "arm","neutral"],6)
    #print("Move")
    myApp.runApp()
def MultiRunApp():
    q,q1=multiprocessing.Pipe()
    getter=multiprocessing.Process(target=BaseEEG.run_data_getter_processer, args=(q1,))
    q2, q3=multiprocessing.Pipe()
    processor=multiprocessing.Process(target=BaseEEG.exec_proc, args=(q, q2, 1))
    #print("Start")
    myApp=MultiLiveClassifierApplication(getter, processor, q3, open("C:/Users/Gaurav/Desktop/KineticEEGProgamFiles/Trainingdata.kineegtr", "rb"))
    #myApp=LiveTrainingDataGatherer(getter, processor, q3, open("C:/Users/Gaurav/Desktop/KineticEEGProgamFiles/Trainingdata.dat", "wb"))
    myApp.runAppSubprocessedDiffAlgo()
if __name__=='__main__':


    #MultiDataGather()
    MultiRunApp()
    pass
