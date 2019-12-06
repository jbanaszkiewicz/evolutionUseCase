import json
import numpy as np
from skimage.draw import circle
import matplotlib.pyplot as plt
import random 
from math import sqrt, ceil
import argparse

class Sprinkler:
      def __init__(self, center, radius):
        self.center = center
        self.radius = radius

class Individual:
    def __init__(self, sprinklers_locations, radius, first=False):
        self.radius = radius
    
        if first == True:
            self.chooseFirstSprinklers(sprinklers_locations)
        else:
            self.sprinklers_locations = sprinklers_locations
        self.sprinklers_sdv = [radius*2 for idx in range(len(sprinklers_locations))]

    def chooseFirstSprinklers(self, possible_sprinklers):
        sprinklers_idxs = [random.randint(0, len(possible_sprinklers)-1) for i in range(random.randint(1, len(possible_sprinklers)))]    
        self.sprinklers_locations = [possible_sprinklers[idx] for idx in sprinklers_idxs]

class Algorithm:
    def __init__(self, population_size,  map, max_iterrs, sprinkler_radius, ratio_tmp_population=0.5):
        self.map = map
        max_sprinklers, _ , _ , _ = self.getMapStat(map)
        self.possible_sprinklers = self.getWaterableLocations()
        
        self.population= [Individual(self.possible_sprinklers,sprinkler_radius, first=True) for i in range(population_size)]
        tmp_population_idxs = [random.randint(0, len(self.population)) for i in range(int(len(self.population)*ratio_tmp_population))]
        self.tmp_population = [self.population[idx] for idx in range(len(tmp_population_idxs))]


  
    # def cross_elements(self, indiv1, indiv2):
    #     # losowanie liczby tryskaczy w nowym krzyzowanym osobniku
    #     l1 = len(indiv1.sprinklers_locations)
    #     l2 = len(indiv2.sprinklers_locations)
    #     minimum = min((l1, l2))-abs(l1-l2)/2 
    #     maximum = max((l1, l2))+abs(l1-l2)/2
    #     if minimum <0:
    #         minimum = 0
    #     if maximum >len(self.possible_sprinklers):
    #         maximum = len(self.possible_sprinklers)
    #     l_n = random.randint(minimum, maximum)

    #     # if l_n < l1
    #     #krzyżowanie
    #     sprinklers_indiv1 = indiv1.sprinklers_locations
    #     sprinklers_indiv2 = indiv2.sprinklers_locations
    #     sprinklers_indivN = np.multiply(np.add(sprinklers_indiv1, sprinklers_indiv2), 0.5)
# dual(sprinklers_locations=sprinklers_indivN, radius=indiv1.radius)
#         sprinklers_indivN = sprinklers_indivN.astype(int)
#         indivN = Indivi
#         return indivN
     

    def getWaterableLocations(self):
        waterable_locations = []
        for i, row in enumerate(self.map):
            for j, point in enumerate(row):
                if point.is_waterable or point.is_wet or point.is_sprinkler:
                    waterable_locations.append((i, j))
        return waterable_locations

  
    def getMapStat(self, map):
        map_size = np.shape(map)
        counter_waterable = 0 
        counter_wet = 0
        counter_sprinklers = 0
        
        for row in map:
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
        print(f"counter_waterable:  {counter_waterable}")
        print(f"counter_wet:        {counter_wet}")
        print(f"counter_sprinklers: {counter_sprinklers}")
        print(f"ratio_coverage:     {ratio_coverage}")
        return counter_waterable, counter_wet, counter_sprinklers, ratio_coverage
        




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

def fillInMap(clean_map_pts, individual):
    tmp_map_pts = np.copy(clean_map_pts)
    sprinklers_locations = individual.sprinklers_locations
    radius = individual.radius
    print(f"radius: {radius}")
    for location in sprinklers_locations:
        rr, cc = circle(location[0], location[1], radius , np.shape(clean_map_pts))
        tmp_map_pts[rr, cc] = Point("~")
    for location in sprinklers_locations:
        tmp_map_pts[location[0]][location[1]] = Point("*")
    for i, row in enumerate(clean_map_pts):
        for j, elem in enumerate(row):
            if elem.is_waterable == False:
                tmp_map_pts[i][j] = Point("#")
    return tmp_map_pts

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
    init_population_size = 49
    iterrations = 10
    

    #zaladuj mapę do macierzy
    with open(map_path) as json_file:
        data_map0 = json.load(json_file)
    map_points = [[Point(elem) for elem in row] for row in data_map0]
    drawableMap = convertMapDrawable(map_points)
    # plt.matshow(drawableMap, vmax=3)
    # plt.show()

    algorithm = Algorithm(init_population_size, map_points, iterrations, radius, ratio_tmp_population=0.1)
    drawableMap_populations = []
    for i in range(init_population_size):
        filledInMap_population = fillInMap(map_points, algorithm.population[i])
        drawableMap_populations.append(convertMapDrawable(filledInMap_population))
    plotAllMaps(np.array(drawableMap_populations), (50, 50), "Tytul")

    
    
