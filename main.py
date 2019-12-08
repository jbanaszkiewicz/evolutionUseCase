import json
import numpy as np
from skimage.draw import circle
import matplotlib.pyplot as plt
import random 
from math import sqrt, ceil
import argparse
from copy import deepcopy

class Sprinkler:
    """
    Definition of the prinkler
    center :param: tuple coordinates of the sprinkler
    """
    def __init__(self, center, radius):
        self.center = center
        self.radius = radius

class Individual:
    def __init__(self, radius, first=False):
        self.radius = radius
        self.sprinklers = []
    
        # if first == True:
        #     self.chooseFirstSprinklers(sprinklers_locations)
        # else:
        #     self.sprinklers_locations = sprinklers_locations
        # self.sprinklers_sdv = [radius*2 for idx in range(len(sprinklers_locations))]

    def addElem(self, sprinkler):
        self.sprinklers.append(sprinkler)

    def generateIndividual(self, numElemMax, mapSize):
        """
        Generates whole individual, adding new sprinklers.
        mapSize :param: tuple with (x, y) size of the map
        """
        numElem = np.random.uniform(1,numElemMax)
        self.sprinklers = [Sprinkler(np.random.uniform(0, mapSize[0]), np.random.uniform(0, mapSize[0]), self.radius) for i in range(numElem)]
    
    def getSprinklersAmmount(self):
        return len(self.sprinklers)

    # def chooseFirstSprinklers(self, possible_sprinklers):
    #     sprinklers_idxs = [random.randint(0, len(possible_sprinklers)-1) for i in range(random.randint(1, len(possible_sprinklers)))]    
    #     self.sprinklers_locations = [possible_sprinklers[idx] for idx in sprinklers_idxs]

class ActualMap:
    def __init__(self,  mapRaw):
        self.mapRaw = mapRaw #unchanged since the beggining
        self.mapPoints = [[Point(elem) for elem in row] for row in self.mapRaw]
        self.mapDrawable = convertMapDrawable(self.mapPoints)
        # max_sprinklers, _ , _ , _ = self.getMapStat(map)
        # self.possible_sprinklers = self.getWaterableLocations()

    def getWaterableLocations(self):
        waterable_locations = []
        for i, row in enumerate(self.mapPoints):
            for j, point in enumerate(row):
                if point.is_waterable or point.is_wet or point.is_sprinkler:
                    waterable_locations.append((i, j))
        return waterable_locations

    def drawIndividual(self, individual):
        for sprinkler in individual.sprinklers:
            rr, cc = circle(sprinkler.center[0], sprinkler.center[1], sprinkler.radius , np.shape(self.mapRaw))
            self.mapPoints[rr, cc] = Point("~")
            self.mapPoints[sprinkler.center[0], sprinkler.center[1]] = Point("*")
            for i, row in enumerate(self.mapPoints):
                for j, elem in enumerate(row):
                    if elem.is_waterable == False:
                        self.mapPoints[i][j] = Point("#")
        self.mapDrawable = convertMapDrawable(self.mapPoints)

    def getMapCoverage(self):
        counter_waterable = 0 
        counter_wet = 0
        counter_sprinklers = 0
        
        for row in self.mapPoints:
            for point in row:
                if point.is_sprinkler:
                    counter_sprinklers += 1
                if point.is_waterable:
                    counter_waterable += 1
                if point.is_wet:
                    counter_wet += 1
        counter_wet +=counter_sprinklers
        counter_waterable += counter_wet
        ratio_coverage = counter_wet/counter_waterable
        return ratio_coverage
    

def getFitness(individual, currentMap, a, b):
    """
    Calculates fitness of the individual using function:
    f(nrSprinklers, mapCoverage) = a*nrSprinklers + b*mapCoverage
    """
    return individual.getSprinklersAmmount()*a + actualMap.getMapCoverage()*b

def rateIndividual(individual, actualMap, a, b):
    currentMap = deepcopy(actualMap)
    currentMap.drawIndividual(individual)
    return getFitness(individual, currentMap, a, b) 

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

def chooseBetterIndividual(individual_parent, individual_child, history, actualMap, a, b):
    fp = rateIndividual(individual_parent, actualMap, a, b)
    fc = rateIndividual(individual_child, actualMap, a, b)

    if (fc>fp):
        history.append(1)
        return individual_child
    else:
        history.append(0)
        return individual_parent

def makeChild(individual_parent, sigmaNew, nSigmaNew, actualMap):
    individualChild = Individual(individual_parent.radius)
    #TODO mam wrażenie ze w tych if else dzieje sie to samo, ale troche w innej kolejnosci
    if(nSigmaNew  < 0):
             
        for i in range(len(individual_parent.sprinklers) + nSigmaNew):
            v = np.random.uniform(-1,1)
            x = individual_parent.sprinklers[i].center[0] + sigmaNew * v 
            y = individual_parent.sprinklers[i].center[1] + sigmaNew * v 
        
            if (not 0<x<actualMap.mapPoints.shape[0] or not 0<y<actualMap.mapPoints.shape[1]):
                x = np.random.uniform(0,actualMap.mapPoints.shape[0])
                y = np.random.uniform(0,actualMap.mapPoints.shape[1])
            sprinkler = Sprinkler(center=(int(x),int(y)), radius=individual_parent.radius)
            individualChild.addElem(sprinkler)     
    else:
         
        for i in range(len(individual_parent.sprinklers)):
            v = np.random.uniform(-1,1)
            x = individual_parent.sprinklers[i].center[0] + sigmaNew * v 
            y = individual_parent.sprinklers[i].center[1] + sigmaNew * v 
            if (not 0<x<actualMap.mapPoints.shape[0] or not 0<y<actualMap.mapPoints.shape[1]):
                x = np.random.uniform(0,actualMap.mapPoints.shape[0])
                y = np.random.uniform(0,actualMap.mapPoints.shape[1])
            sprinkler = Sprinkler(center=(int(x),int(y)), radius=individual_parent.radius)
            individualChild.addElem(sprinkler)      
         
        for i in range(nSigmaNew):
            x = np.random.uniform(0,actualMap.mapPoints.shape[0])
            y = np.random.uniform(0,actualMap.mapPoints.shape[1])
            sprinkler = Sprinkler(center=(int(x),int(y)), radius=individual_parent.radius)
            individualChild.addElem(sprinkler) 
              
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

def mutationNew(individual_parent, history, m, c1, c2, sigma, nSigma, itterationIndex, actualMap):
    pass
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
    for row in map_pts:
        new_row = []
        for pt in row:
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

# def fillInMap(clean_map_pts, individual):
#     tmp_map_pts = np.copy(clean_map_pts)
#     sprinklers_locations = individual.sprinklers_locations
#     radius = individual.radius
#     print(f"radius: {radius}")
#     for location in sprinklers_locations:
#         rr, cc = circle(location[0], location[1], radius , np.shape(clean_map_pts))
#         tmp_map_pts[rr, cc] = Point("~")
#     for location in sprinklers_locations:
#         tmp_map_pts[location[0]][location[1]] = Point("*")
#     for i, row in enumerate(clean_map_pts):
#         for j, elem in enumerate(row):
#             if elem.is_waterable == False:
#                 tmp_map_pts[i][j] = Point("#")
#     return tmp_map_pts

def plotAllMaps(maps, size, title):
       
    fig = plt.figure()
    fig.suptitle(title)    
    plt.axis('off')
    numberOfMaps = np.shape(maps)[0]
    axis_size = ceil(sqrt(numberOfMaps))
    
    for i, m in enumerate(maps):
        f = fig.add_subplot(axis_size, axis_size,i+1)
        f.title.set_text(str(i+1))
        plt.imshow(m)
        
 
    plt.axis('off')
    plt.show() 

if __name__ == "__main__":
    # parser = argparse.ArgumentParser(description="Calculate evolution algorithm")
    # parser.add_argument('map', type=str, help="Source path with map of ascii chars")
    # parser.add_argument('radius', type=int, help="radius of single sprinkler field")
    # parser.add_argument('init_population_size', type=int, help="Number of sprinkers in first population")    
    # parser.add_argument('iterrations', type=int, help="Number of iterations in trening")

    
    # args = parser.parse_args()

    # map_path = args.map
    map_path = "./maps/map1.json"
    radius = 3
    init_population_size = 50
    iterrations = 10
    init_sprinklers_nr = 10
    

    #zaladuj mapę do macierzy
    with open(map_path) as json_file:
        data_map0 = json.load(json_file)
    
    # plt.matshow(drawableMap, vmax=3)
    # plt.show()

    algorithm = Algorithm(init_population_size, map_points, iterrations, radius, ratio_tmp_population=0.1)
    drawableMap_populations = []
    for i in range(init_population_size):
        filledInMap_population = fillInMap(map_points, algorithm.population[i])
        drawableMap_populations.append(convertMapDrawable(filledInMap_population))
    plotAllMaps(np.array(drawableMap_populations), (50, 50), "Tytul")

    
    
