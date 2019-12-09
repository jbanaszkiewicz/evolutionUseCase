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
## Rozpatrywane algorytmy
Rozpatrywano i zaimplementowano dwa typy algorytmów ewolucyjnych:
* algorytm (1+1)
* algorytm (μ, λ)