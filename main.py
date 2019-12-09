import json
import numpy as np
from skimage.draw import circle
import matplotlib.pyplot as plt
import random 
from math import sqrt, ceil
import argparse
from copy import deepcopy
from collections import deque
from math import pi

class Sprinkler:
    """
    Definition of the prinkler
    center :param: tuple coordinates of the sprinkler           type: tuple
    radius :param: radius of the circle field of the sprinkler  type: int
    """
    def __init__(self, center, radius):
        self.center = center
        self.radius = radius

class Individual:
    def __init__(self, radius):
        self.radius = radius
        self.sprinklers = []
        self.sprinklerField = pi*self.radius*self.radius
    

    def addElem(self, sprinkler):
        self.sprinklers.append(sprinkler)

    def generateIndividual(self, numElemMax, actualMap):
        """
        Generates whole individual, adding new sprinklers in random locations.
        numElemMax :param: maximum ammoount of possible sprinklers  type: int
        actualMap :param: map where individual would be generated   type: ActualMap
        """

        numElem = np.random.randint(1,numElemMax+1)
        for i in range(numElem):
            s1 = np.random.randint(0, np.shape(actualMap.mapPoints)[0])
            s2 = np.random.randint(0, np.shape(actualMap.mapPoints)[1])
            while(actualMap.mapPoints[s1, s2].is_wall == True):
                # print("Probowano wstawic sprinklera na sciane (%d, %d)" % (s1, s2))
                s1 = np.random.randint(0, np.shape(actualMap.mapPoints)[0])
                s2 = np.random.randint(0, np.shape(actualMap.mapPoints)[1])
            self.sprinklers.append(Sprinkler((s1, s2), self.radius))
        print("liczba sprinklerow: %d" % (self.getSprinklersAmmount()))
    
    def getSprinklersAmmount(self):
        return len(self.sprinklers)

class ActualMap:
    def __init__(self,  mapRaw):
        self.mapRaw = mapRaw #unchanged since the beggining
        self.mapPoints = np.array(([[Point(elem) for elem in row] for row in self.mapRaw]))
        self.mapPointsOrigin = deepcopy(self.mapPoints)
        self.mapDrawable = convertMapDrawable(self.mapPoints)
        self.mapDrawableOrigin = deepcopy(convertMapDrawable)
        self.maxSprinklers = len(self.getWaterableLocations())
        print("max sprinklers on the map: %d" % (self.maxSprinklers))

    def resetActualMap(self):
        self.mapPoints = deepcopy(self.mapPointsOrigin)
        self.mapDrawable = deepcopy(self.mapDrawableOrigin)

    def getWaterableLocations(self):
        waterable_locations = []
        for i, row in enumerate(self.mapPoints):
            for j, point in enumerate(row):
                if point.is_wall == False:
                    waterable_locations.append((i, j))
        return waterable_locations

    def getWallLocations(self):
        wall_locations = []
        for i, row in enumerate(self.mapPoints):
            for j, point in enumerate(row):
                if point.is_wall == True:
                    wall_locations.append((i, j))
        return wall_locations

    def drawIndividual(self, individual):
        for sprinkler in individual.sprinklers:
            rr, cc = circle(sprinkler.center[0], sprinkler.center[1], sprinkler.radius , np.shape(self.mapPoints))
            self.mapPoints[rr, cc] = Point("~")
        for sprinkler in individual.sprinklers:
            self.mapPoints[sprinkler.center[0], sprinkler.center[1]] = Point("*")
        for i, row in enumerate(self.mapPointsOrigin):
            for j, elem in enumerate(row):
                if elem.is_wall == True:
                    self.mapPoints[i, j] = Point("#")

        self.mapDrawable = convertMapDrawable(self.mapPoints)

    def getMapCoverage(self):
        counter_waterable = 0 
        counter_wet = 0
        counter_sprinklers = 0
        counter_wall = 0
        
        for row in self.mapPoints:
            for point in row:
                if point.is_sprinkler:
                    counter_sprinklers += 1
                if point.is_waterable:
                    counter_waterable += 1
                if point.is_wet:
                    counter_wet += 1
                if point.is_wall:
                    counter_wall +=1
        counter_wet +=counter_sprinklers
        counter_waterable += counter_wet
        ratio_coverage = counter_wet/counter_waterable
        return ratio_coverage
    

def getFitness(individual, currentMap, a):
    """vx
    Calculates fitness of the individual using function:
    f(nrSprinklers, mapCoverage) = a*nrSprinklers + b*mapCoverage
    """
    maxSprinklers = currentMap.maxSprinklers
    currentSprinklers = individual.getSprinklersAmmount()
    #TODO poprawić zeby dzielic liczbe tryskaczy przez pole tryskacza
    #pole tryskacza
    
    sprinklers = (maxSprinklers/individual.sprinklerField-currentSprinklers)/(maxSprinklers/individual.sprinklerField)
    mapCoverage = currentMap.getMapCoverage()
    print("Sprinklers:  %f,     coverage: %f" % (sprinklers, mapCoverage))
    return sprinklers*a + (1-a)*mapCoverage

def rateIndividual(individual, actualMap, a):
    currentMap = deepcopy(actualMap)
    currentMap.drawIndividual(individual)
    return getFitness(individual, currentMap, a) 

def updateSigma(history, c1, c2, sigma, nSigma, iterationIndex, m):
      
    if((iterationIndex % m) == 0): # co m iteraji wykonaj  zerowanie bufora i update sigm
        fi = sum(history)/ len(history)

        if round(fi, ndigits=1) < 0.2:      
            sigma = sigma * c1
            nSigma = 1
        elif round(fi, ndigits=1) > 0.2:
            sigma = sigma * c2 
            nSigma = 1
        elif round(fi, ndigits=1) == 0.2:
            sigma = sigma
            nSigma = nSigma
       
    return sigma, nSigma

def chooseBetterIndividual(individual_parent, individual_child, history, actualMap, a):
    fp = rateIndividual(individual_parent, actualMap, a)
    fc = rateIndividual(individual_child, actualMap, a)
    a = 3
    if (fc>fp):
        history.append(1)
        return individual_child, history
    else:
        history.append(0)
        return individual_parent, history

def makeChild(individual_parent, sigmaNew, nSigmaNew, actualMap):
    individualChild = Individual(individual_parent.radius)
    list_sprinklers = individual_parent.sprinklers
    random.shuffle(list_sprinklers)

    if nSigmaNew<=0:
        for i in range(len(list_sprinklers)+nSigmaNew):
            vx = np.random.choice([1, -1])
            vy = np.random.choice([1, -1])
            x = list_sprinklers[i].center[0] + round(sigmaNew) * vx
            y = list_sprinklers[i].center[1] + round(sigmaNew) * vy
            while(x not in range(1, np.shape(actualMap.mapPoints)[0]-1) or y not in range(1, np.shape(actualMap.mapPoints)[1]-1)):
                # print("nowa pozycja sprinklera nie moze byc poza mapa  (%d, %d)" % (x, y))
                vx = np.random.choice([-1, 1])
                vy = np.random.choice([-1, 1])
                if (list_sprinklers[i].center[0] + round(sigmaNew) * vx) in range(0, np.shape(actualMap.mapPoints)[0]):
                    x = list_sprinklers[i].center[0] + round(sigmaNew) * vx 
                if list_sprinklers[i].center[1] + round(sigmaNew) * vy in range(0, np.shape(actualMap.mapPoints)[1]):
                    y = list_sprinklers[i].center[1] + round(sigmaNew) * vy
            while(actualMap.mapPoints[x, y].is_wall == True):
                # print("nowa pozycja sprinklera nie moze byc w scianie lub poza mapa (%d, %d)" % (x, y))
                x = np.random.randint(0, np.shape(actualMap.mapPoints)[0])
                y = np.random.randint(0, np.shape(actualMap.mapPoints)[1])
            individualChild.sprinklers.append(Sprinkler((x, y), individualChild.radius))
    if nSigmaNew >0:
        for i in range(len(list_sprinklers)):
            #TODO zrobic losowanie bez zwracania i w ten sposob usunac przeszukiwanie do konca whilem
            vx = np.random.choice([-1, 1])
            vy = np.random.choice([-1, 1])
            x = list_sprinklers[i].center[0] + round(sigmaNew) * vx 
            y = list_sprinklers[i].center[1] + round(sigmaNew) * vy 
            while(x not in range(0, np.shape(actualMap.mapPoints)[0]) or y not in range(0, np.shape(actualMap.mapPoints)[1])):
                # print("nowa pozycja sprinklera nie moze byc poza mapa  (%d, %d)" % (x, y))
                vx = np.random.choice([-1, 1])
                vy = np.random.choice([-1, 1])
                if (list_sprinklers[i].center[0] + round(sigmaNew) * vx) in range(0, np.shape(actualMap.mapPoints)[0]):
                    x = list_sprinklers[i].center[0] + round(sigmaNew) * vx 
                if list_sprinklers[i].center[1] + round(sigmaNew) * vy in range(0, np.shape(actualMap.mapPoints)[1]):
                    y = list_sprinklers[i].center[1] + round(sigmaNew) * vy
            while(actualMap.mapPoints[x, y].is_wall == True):
                # print("nowa pozycja sprinklera nie moze byc w scianie lub poza mapa (%d, %d)" % (x, y))
                x = np.random.randint(0, np.shape(actualMap.mapPoints)[0])
                y = np.random.randint(0, np.shape(actualMap.mapPoints)[1])
            individualChild.sprinklers.append(Sprinkler((x, y), individualChild.radius))

        for i in range(nSigmaNew):
            x = np.random.randint(0, np.shape(actualMap.mapPoints)[0])
            y = np.random.randint(0, np.shape(actualMap.mapPoints)[1])
            while(actualMap.mapPoints[x, y].is_wall == True):
                # print("Probowano wstawic sprinklera na sciane (%d, %d)" % (x, y))
                x = np.random.randint(0, np.shape(actualMap.mapPoints)[0])
                y = np.random.randint(0, np.shape(actualMap.mapPoints)[1])
            individualChild.sprinklers.append(Sprinkler((x, y), individualChild.radius)) 
    return individualChild


class Point:
      # is_waterable = None
  # is_wet = False  
    def __init__(self, ascii_char):
        self.encode_point(ascii_char)

    def display_point(self):
        if self.is_sprinkler: 
            return "*"
        elif self.is_wet:
            return "~"
        elif self.is_waterable:
            return "."
        else:
            return "#"

    def encode_point(self, ascii_char):
        self.is_sprinkler = (ascii_char == "*")
        self.is_wet = (ascii_char == "~")
        self.is_waterable = (ascii_char == ".")
        self.is_wall = (ascii_char == "#")

def mutationNew(individual_parent, history, m, c1, c2, sigma, nSigma, iterationIndex, actualMap, a):     
    sigma, nSigma = updateSigma(history, c1,c2, sigma, nSigma, iterationIndex, m)
              
    individualChild = makeChild(individual_parent, sigma, nSigma, actualMap)
        
    individual, history = chooseBetterIndividual(individual_parent, individualChild, history, actualMap, a) 
    
    fi = sum(history)/ len(history)
    f = rateIndividual(individual, actualMap, a)
    print("Iter ", iterationIndex," rate:   ",f,"sigma: ",sigma, "nSigma:   ",nSigma, "successRate:     ", fi, "spri._count:", len(individual.sprinklers))
    
    return individual, sigma, nSigma, history

def display_map(map):
    """
    Function print map with ascii chars as lines
    map :param: numpy array with chars: "*", "~", ".", "#"
    
    """
    for row in map:
        line = ""
        for point in row:
            line += point.display_point()
        print(line)

def convertMapDrawable(map_pts):
    drawableMap = []
    for i, row in enumerate(map_pts):
        new_row = []
        for j, pt in enumerate(row):
            if pt.is_sprinkler: 
                new_row.append(3)
            elif pt.is_wet:
                new_row.append(1)
            elif pt.is_waterable:
                new_row.append(2)
            else:
                new_row.append(0)
        drawableMap.append(new_row)
    return drawableMap


def plotAllMaps(maps, title):
       
    fig = plt.figure()
    fig.suptitle(title)    
    plt.axis('off')
    numberOfMaps = len(maps)
    axis_size = ceil(sqrt(numberOfMaps))
    
    for i, m in enumerate(maps):
        f = fig.add_subplot(axis_size, axis_size,i+1)
        f.title.set_text(str(i+1))
        plt.imshow(m.mapDrawable, vmax=3)
        
 
    plt.axis('off')
    plt.show() 

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate evolution algorithm")
    parser.add_argument('map', type=str, help="Source path with map of ascii chars")
    parser.add_argument('radius', type=int, help="radius of single sprinkler field")
    parser.add_argument('iterations', type=int, help="Number of iterations in trening")
    parser.add_argument('initSprinklersNr', type=int, help="Number of sprinklers in first population")    
    parser.add_argument('a', type=float ,help="Parameter of fitness funcion in range <0,1>")    
    parser.add_argument('--sigma', type=int, default=2, help="Defines random disturbance from normal distribution of the child's position. As default 2")
    parser.add_argument('--nSigma', type=int, default=2, help="Defines random disturbance from normal distribution of child's ammount of sprinklers. As default 2")
    parser.add_argument('--c1', type=float, default=1.2, help="Parameter of (1+1) function. As default 1.2")
    parser.add_argument('--c2', type=float, default=0.82, help="Parameter of (1+1) function. As default 1.2")    
    parser.add_argument('--historyMax', type=int, choices=range(0, 20), default=10, help="Length of list history, which keeps history of changing and not changing parent to child ")

    
    args = parser.parse_args()
    map_path = args.map
    radius = args.radius
    iterations = args.iterations
    init_sprinklers_nr = args.initSprinklersNr
    sigma = args.sigma
    nSigma = args.nSigma
    a = args.a #wieksze faworyzuje mniej sprinklerow
    historyMaxLength = args.historyMax
    c1 = 0.82
    c2 = 1.2
    """
    # map_path = args.map
    map_path = "./maps/map5.json"
    radius = 4
    iterations = 150
    init_sprinklers_nr = 10
    sigma = 2
    nSigma = 2
    a = 0.8 #wieksze faworyzuje mniej sprinklerow
    historyMaxLength = 10
    c1 = 0.82
    c2 = 1.2
    """
    maps = []
    history = deque(maxlen=historyMaxLength)
    history.append(1)
    #zaladuj mapę do macierzy
    with open(map_path) as json_file:
        data_map = json.load(json_file)
    actualMap = ActualMap(data_map)
   
    

    parent = Individual(radius)   
    parent.generateIndividual(init_sprinklers_nr, actualMap)
    actualMap.drawIndividual(parent)
    

    # actualMap.drawIndividual(parent)
    # plt.matshow(actualMap.mapDrawable, vmax=3)
    # plt.show()
    i = 0
    while (sigma > 0.01):
        parent, sigma, nSigma, history = mutationNew(parent, history, historyMaxLength, c1, c2, sigma, nSigma, i+1, actualMap, a)
        actualMap.drawIndividual(parent)
        maps.append(deepcopy(actualMap))
        actualMap.resetActualMap()
    plotAllMaps(maps[:100], "first 100" )    
    plotAllMaps(maps[-100:], "last 100" )
    plotAllMaps(maps[-10:], "last 10" )