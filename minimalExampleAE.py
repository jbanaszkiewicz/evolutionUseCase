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
       t1_x = np.random.uniform(0,mapSize-1)
       t1_y = np.random.uniform(0,mapSize-1)
       t1 = tryskacz(int(t1_x),int(t1_y))
       self.addElem(t1,stdDev)
 
   def getTryskaczCount(self):
      return len(self.T)

class map:
  def __init__(self,size):
    self.size = size,
    self.mapClean = np.zeros((size, size))
    self.mapDrawable = np.zeros((size, size))
    self.tempMapDrawable = np.zeros((12, 12)) 

  def drawTryskacz(self, tryskacz):
     temp = self.tempMapDrawable[tryskacz.x-1+1:tryskacz.x+2+1,tryskacz.y-1+1:tryskacz.y+2+1] 
     temp_template = tryskacz.template
     temp_template[temp == 2] = 2 #zabezpieczenie zeby nie nadpisac wody nad tryskaczem
     self.tempMapDrawable[tryskacz.x-1+1:tryskacz.x+2+1,tryskacz.y-1+1:tryskacz.y+2+1] = temp_template
     self.mapDrawable = self.tempMapDrawable[1:11,1:11]     

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

def rateOsobnik(osobnik):
   m = map(10)
   m.drawOsobnik_noPrint(osobnik)
   print(fitness(osobnik,m))

def fitness(osobnik, m):
  a = -2; #koszt nowego osobnika
  b = 1; #nagroda za pokrycie jednego pola 
  
  return osobnik.getTryskaczCount() * a + m.getMapCoverage() * b

def crossover(osobnik1, osobnik2, diffPerc=0.1):
  
  #jesli mam osobniki o różnej liczbie tryskaczy to krzyzuje te co sie da a reszte kopiuje  

  o1_len = len(osobnik1.T)
  o2_len = len(osobnik2.T)
  minLen = min(o1_len,o2_len)
  maxLen = max(o1_len,o2_len)

  diff = abs(o1_len - o2_len)
  diffRange = int(diff * diffPerc)
  if(diffRange == 0):
      diffRange=1
  newLength = int(np.random.uniform(minLen-diffRange, maxLen + diffRange))
  if newLength < 1:
      newLength = 1
      
  newOsobnik = osobnik()

  #print("Nowa dlugosc:  ",newLength,"diff range: ",diffRange)

  for i in range (newLength):
    if(i < minLen): # skrzyżowany osobnik bedzie krótszy niż najkrótszy
     new_Tryskacz = tryskacz(int((osobnik1.T[i].x + osobnik2.T[i].x) / 2), int((osobnik1.T[i].y + osobnik2.T[i].y) / 2))
     new_stdDev = (osobnik1.S[i] + osobnik2.S[i]) / 2
     newOsobnik.addElem(new_Tryskacz,new_stdDev)
    elif (i < maxLen): # skrzyżowany osobnik bedzie krótszy niż najdłuższy
      if maxLen == o1_len:
         newOsobnik.addElem(osobnik1.T[i],osobnik1.S[i])
      else:
         newOsobnik.addElem(osobnik2.T[i],osobnik2.S[i])
    else: # skrzyżowany osobnik bedzie krótszy niż najdłuższy
       j = random.randint(0,o1_len-1)
       k = random.randint(0,o2_len-1)
       new_Tryskacz2 = tryskacz(int((osobnik1.T[j].x + osobnik2.T[k].x) / 2), int((osobnik1.T[j].y + osobnik2.T[k].y) / 2))
       newOsobnik.addElem(new_Tryskacz2,new_stdDev)

  return newOsobnik    

def mutate(population):

    n_pop = len(population)   
    r_prim = 1*(np.power( 2*n_pop, -0.5))
  
    ksi = random.random()

    S = [] # individuals sigma list - distributions 

    for i in range(n_pop):    

      zarodek = population[i]
      n_trys = len(zarodek.T)
      r = 1*(np.power(2*np.power( n_trys, 0.5), -0.5))
      o = osobnik()

      for i in range(n_trys):
        ksi_i = random.random()        
        sigma = zarodek.S[i] * math.exp(ksi_i*r_prim + ksi * r)
        v = np.random.uniform(-1,1)
        x = zarodek.T[i].x + sigma * v 
        y = zarodek.T[i].y + sigma * v 
       
        if (x < 0 or x > 9 or y < 0 or y > 9):
             t = tryskacz(int(5),int(5))
        else:
             t = tryskacz(int(x),int(y))
       
        o.addElem(t,sigma)

      S.append(o) 

    return S

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

 
def main(itMax, sigma):

  maxTryskaczy = 100
  mi = 17
  lamb = 7
  
  M = [] # lista wygenerowanych map 
  
  #wygeneruj populację 'mi' osobników i wylosuj lambda-elementową populację tymczasową 
  population = Population(mi,maxTryskaczy,sigma)
  
  
  # testowe 5 iteracji
  for i in range(itMax): 
    
      L = []    
      for i in range (lamb):
         L.append(random.choice(population.P));

      T = [] # temp population of germs

      # reprodukuj lambda-elementową populację stosując mutację i krzyżowanie

      for i in range (len(L)-1):
        for j in range (len(L)-1):
            o1 = L[i]
            o2 = L[j+1]
            o3 = crossover(o1,o2)
            T.append(o3)
      
      R =  mutate(T)   # returns mutated population 
      F_temp = [] # lista funkcji celu dla wszystich z mutacji
      # utwórz P jako mi osobników z PuR

      for i in range(len(R)):
        m = map(10)
        m.drawOsobnik_noPrint(R[i])
        F_temp.append(fitness(R[i],m))        
       
      bestMutOsobnik = chooseBestOsobnik(R)
      m_t = map(10)
      bestMap = m_t.drawOsobnik_Matrix(bestMutOsobnik)
      M.append(bestMap)

      S = population.P + R

      F = [] # lista funkcji celu dla wszystkich osobników


      for i in range(len(S)):
        m = map(10)
        m.drawOsobnik_noPrint(S[i])
        F.append(fitness(S[i],m))        
      
      Idx = [] # list of mi highest values
      Idx = sorted(range(len(F)), key=lambda i: F[i], reverse=True)[:mi]      
      
      print (max(F))       

      # Nadpisanie starej poplacji nowymi osobnikami 
      for i in range(len(Idx)):
        population.P[i] = S[Idx[i]]

      
  plotAllMaps(M,(50,50),"Mapy najlepszych osobników po mutacji z każdej iteracji",10,10)
  bestOsobnik = chooseBestOsobnik(population.P)
  resultMap = map(10)
  resultMap.drawOsobnik(bestOsobnik)
  
if __name__ == "__main__":
  main(100,0.5)
  #todo parse argumentów z konsoli Kuba
  