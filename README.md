# Wykorzystanie algorytmów ewolucyjnych w bezpieczeństwie budynków
## Treść zadania
Napisać program dokonujący optymalnego rozkładu tryskaczy na danym obszarze zamkniętym w przestrzeni dyskretnej. 
Tryskacz zapewnia pokrycie obszaru ‘kołowego’ o średnicy D i jego zasięg może być ograniczony przez ściany. 
Tryskacze mogą być umieszczane tylko w punktach wewnętrznych obszaru. Przedmiotem minimalizacji jest liczba tryskaczy. 
WE: plik z mapą/definicją obszaru, średnica D, minimalne pokrycie w % do zakończenia działania algorytmu. 
WY: położenie tryskaczy oraz uzyskany % pokrycia.

## Wymagania wstępne
Program jest kompatybilny z Python 3.6.
Wykorzystano następujące biblioteki:
```python
numpy
json
numpy
skimage
matplotlib
random 
math
argparse
copy
collections
```
## Mapy
Mapy zdefiniowano w formie plików json. Mapy są uszeregowano według zasady: 0 - najprostsza N- najbardziej skomplikowna
## Rozpatrywane algorytmy
Rozpatrywano i zaimplementowano dwa typy algorytmów ewolucyjnych:
* algorytm (1+1)
Pełna wersja algorytmu (1+1) została zdefiniowana w pliku [main](./main.py)
* algorytm (μ, λ)

## Zdefiniowane struktury
W pliku [main](./main.py) zdefiniowano następujące struktury:
```python
class Sprinkler
```
Klasa ta definiuje pojedyńczy tryskacz
```python
class Point
```

```python 
class Individual
```
Klasa ta definiuje osobnika. Pojedyńczy osobnik to zbiór tryskaczy. Zadaniem algorytmu jest znalezienie najlepszego osobnika w procesie ewolucji (Problem sprowadza się więc do znalezienia optymalnego rozłożenia tryskaczy).

```python 
class ActualMap
```
Klasa definiuje mapę. Jest to główna klasa w programie, która organizuje działanie algorytmu.
Zdefiniowano w niej kilka kluczowych atrybutów:
```python
self.mapRaw #przechowuje czystą mapę  w postaci znaków ASCII bez osobnika
self.mapPointsOrigin #przechowuje mapę definiowaną jako zbiór obiektów typu Points
``` 

