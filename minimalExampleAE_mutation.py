#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec  4 20:24:29 2019

@author: tomek1911
"""

import numpy as np
import matplotlib.pyplot as plt
import random 
import math
from collections import deque


class tryskacz: 
  def __init__(self,x,y):
   self.x = x
   self.y = y
   
   self.template = np.ones((3,3))
   self.template [1][1]=2

class osobnik:
   def __init__(self):
     self.T = [] #lista pozycji tryskaczy 
     self.S = [] #lista odchyleń standardowych  

   def addElem(self, tryskacz,stdDev):
     self.T.append(tryskacz)
     self.S.append(stdDev)

   def addSigma(self,stdDev):
     self.S.append(stdDev)

   def printOsobnik(self):
     for i in range(len(self.T)):
       print ( "  Tryskacz_",i,": (",self.T[i].x,",",self.T[i].y,"),stdEv: ",self.S[i]) 

   def generateOsobnik(self,numElMax,stdDev, mapSize):
     numEl = np.random.uniform(1,numElMax)     
     for i in range(int(numEl)):       
       t1_x = np.random.uniform(0,mapSize)
       t1_y = np.random.uniform(0,mapSize)
       t1 = tryskacz(int(t1_x),int(t1_y))
       self.addElem(t1,stdDev)
 
   def getTryskaczCount(self):
      return len(self.T)

class map:
  def __init__(self,size):
    self.size = size,
    self.mapClean = np.zeros((size, size))
    self.mapDrawable = np.zeros((size, size))   
    self.tempMapDrawable = np.zeros(((size +2), (size +2))) 

  def drawTryskacz(self, tryskacz):
     temp = self.tempMapDrawable[tryskacz.x-1+1:tryskacz.x+2+1,tryskacz.y-1+1:tryskacz.y+2+1] 
     temp_template = tryskacz.template
     temp_template[temp == 2] = 2 #zabezpieczenie zeby nie nadpisac wody nad tryskaczem
     self.tempMapDrawable[tryskacz.x-1+1:tryskacz.x+2+1,tryskacz.y-1+1:tryskacz.y+2+1] = temp_template
     local_size = self.size[0]+1
     self.mapDrawable = self.tempMapDrawable[1:local_size,1:local_size]     

  def drawOsobnik(self,osobnik):
    for elem in osobnik.T:
      self.drawTryskacz(elem)      
    plt.matshow(self.mapDrawable) 

  def drawOsobnik_noPrint(self,osobnik):
    for elem in osobnik.T:
      self.drawTryskacz(elem) 
      
  def drawOsobnik_Matrix(self,osobnik):
    for elem in osobnik.T:
      self.drawTryskacz(elem)
    return self.mapDrawable 

  def getMapCoverage(self):
     return np.count_nonzero(self.mapDrawable) # haha niesamowite ze byla taka funkcja lol po c++ trudno w to uwierzyć :p

class Population:
 def __init__(self, populationSize, maxIndividualSize, basicSigma):
   self.P = []# mi size population  
   
   for i in range(populationSize):
      o1 = osobnik()
      o1.generateOsobnik(maxIndividualSize,basicSigma,10)
      # m = map(10)
      # m.drawOsobnik(o1)
      # cov = m.getMapCoverage()
      # fit = fitness(o1,m)
      # print ("Pokrycie mapy osobnika ",i,": ",cov,"/100, fitness: ",fit)
      self.P.append(o1)

def rateOsobnik(osobnik, mapSize):
   m = map(mapSize)
   m.drawOsobnik_noPrint(osobnik)
   return fitness(osobnik,m)

def fitness(osobnik, m):
  a = -3; #koszt nowego osobnika
  b = 1; #nagroda za pokrycie jednego pola 
  
  return osobnik.getTryskaczCount() * a + m.getMapCoverage() * b

def updateSigma(fi, c1, c2, sigma, nSigma, iterationIndex, m):
  
    if((iterationIndex % m) == 0): # co m iteraji wykonaj  zerowanie bufora i update sigm
        history = []
        history.append(1)   
          
        if fi < 0.2:      
            sigma = sigma * c1
            nSigma = 1
        elif fi > 0.2:
            sigma = sigma * c2 
            nSigma = 1
        elif fi == 0.2:
            sigma = sigma
            nSigma = nSigma
       
    return sigma, nSigma
    
def chooseBetterOsobnik (osobnik_parent, osobnik_child, history, mapSize):
   
    fp = rateOsobnik(osobnik_parent, mapSize)
    fc = rateOsobnik(osobnik_child, mapSize) 
        
    if(fc > fp):
        history.append(1)
        osobnik_parent = osobnik_child
    else:
        history.append(0)
        
    return osobnik_parent    

def make_child(osobnik_parent, sigmaNew, nSigmaNew, mapSize):
    
     osobnik_child = osobnik()
             
     if(nSigmaNew  < 0):
             
         for i in range(len(osobnik_parent.T) + nSigmaNew):
             v = np.random.uniform(-1,1)
             x = osobnik_parent.T[i].x + sigmaNew * v 
             y = osobnik_parent.T[i].y + sigmaNew * v 
        
         if (x < 0 or x > mapSize or y <0 or y > mapSize):
             x = np.random.uniform(1,mapSize)
             y = np.random.uniform(1,mapSize)
             t = tryskacz(int(x),int(y))
         else:
             t = tryskacz(int(x),int(y))        
         osobnik_child.addElem(t,0)   
             
     else:
         
         for i in range(len(osobnik_parent.T)):
             v = np.random.uniform(-1,1)
             x = osobnik_parent.T[i].x + sigmaNew * v 
             y = osobnik_parent.T[i].y + sigmaNew * v 
        
             if (x < 0 or x > mapSize or y <0 or y > mapSize):
                 x = np.random.uniform(1,mapSize)
                 y = np.random.uniform(1,mapSize)
                 t = tryskacz(int(x),int(y))
             else:
                 t = tryskacz(int(x),int(y))        
             osobnik_child.addElem(t,0) 
         
         for i in range(nSigmaNew):
             x = np.random.uniform(1,mapSize)
             y = np.random.uniform(1,mapSize)
             t = tryskacz(int(x),int(y))
             osobnik_child.addElem(t,0)  
            
     return osobnik_child
             

def mutationNew(osobnik_parent, history, m, c1, c2, sigma, nSigma, iterationIndex,mapSize):
       
    fi = sum(history)/ len(history)
    
    sigma, nSigma = updateSigma(fi, c1,c2, sigma, nSigma, iterationIndex, m)
    
          
    osobnik_child = make_child(osobnik_parent, sigma, nSigma, mapSize)
        
    osobnik_parent = chooseBetterOsobnik(osobnik_parent, osobnik_child, history, mapSize) 
    
    f = rateOsobnik(osobnik_parent, mapSize)
    print("Iter ", iterationIndex,": ",f,"sigma: ",sigma, "nSigma: ",nSigma, "successRate: ", fi)
    
    return osobnik_parent, sigma, nSigma

def plotAllMaps(maps, size, title, rows, cols):
       
    fig = plt.figure(figsize=size)
    fig.suptitle(title)    
    plt.axis('off')
    
    i = 1
    for m in maps:
        f = fig.add_subplot(rows,cols,i)
        f.title.set_text(str(i))
        plt.imshow(m)
        i=i+1
 
    plt.axis('off')
    plt.show() 
    
def chooseBestOsobnik(P):
   
    F =[]
    for i in range(len(P)):
        m = map(10)
        m.drawOsobnik_noPrint(P[i])
        F.append(fitness(P[i],m))   
        
    i = F.index(max(F))  
    bestOsobnik = P[i]
 
    return bestOsobnik

 
def main(itMax, sigma, nSigma, mapSize):

   # PARAMS
  maxTryskaczy = 350
  m  = 10
  c1 = 0.82
  c2 = 1.2
  h = deque(maxlen=m)
  h.append(1)

  M = [] # kontener na mapy
  
  parent = osobnik()
  parent.generateOsobnik(maxTryskaczy,0,mapSize)
  iterInd = 1
  
  for i in range(itMax): 

      parent, sigma, nSigma = mutationNew(parent, h,m,c1,c2,sigma,nSigma,iterInd,mapSize)     
     
      m_t = map(mapSize)
      bestMap = m_t.drawOsobnik_Matrix(parent)     
      M.append(bestMap)
      iterInd = iterInd +1

  plotAllMaps(M,(50,50),"Mapy najlepszych osobników po mutacji z każdej iteracji",2, 2)
  resultMap = map(mapSize)
  resultMap.drawOsobnik(parent)
##############################################  
if __name__ == "__main__":  main(4,2,1,20)
  #todo parse argumentów z konsoli Kuba
  
    