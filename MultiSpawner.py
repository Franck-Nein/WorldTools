import argparse
import math
import multiprocessing
from tqdm import tqdm

parser = argparse.ArgumentParser(description='Analiza algunas coordenadas y encuentra spawners dentro de un radio.')
parser.add_argument('input', type=str, help='archivo que contiene las coordenadas')
parser.add_argument('output', type=str, help='archivo de salida')
parser.add_argument('radius', type=float, help='radio máximo para considerar dos coordenadas como parte del mismo multi spawner')
parser.add_argument('spawnerMinimos', type=int, help='cantidad minima de spawners nesesarios para considerar multi spawner')
parser.add_argument('--threads', type=int, default=1, help='número de hilos a utilizar')

args = parser.parse_args()

coords = []
with open(args.input, 'r') as file:
    for line in file:
        tmp = line.strip().replace(" ","").replace("y","").replace("z","").split(":")
        coords.append([str(int(float(tmp[2]))), str(int(float(tmp[3]))), str(int(float(tmp[4]))), ])

        #minecraft:spawner x: 77.5 y: -28 z: 44.5

all_coords= coords

def process_coords(coord):
    multi = []
    multi.append(coord)
    for coord2 in all_coords:
        if coord != coord2:
            dist = math.sqrt((int(coord[0])-int(coord2[0]))**2+(int(coord[1])-int(coord2[1]))**2+(int(coord[2])-int(coord2[2]))**2)
            if (dist < (args.radius*2)):
                multi.append(coord2)
    if (len(multi) > (args.spawnerMinimos-1)):
        multiStr = []
        for x in sorted(multi):
            multiStr.append(" ".join(x))
        return(multiStr)

def fit_sphere(coords):
  # Inicializa el punto central al promedio de todas las coordenadas
  center = [sum(x)/len(x) for x in zip(*coords)]
  learning_rate = 0.01 # Establecer la tasa de aprendizaje para el descenso de gradiente
  num_iterations = 1000 # Establecer el número de iteraciones para el descenso de gradiente
  
  for i in range(num_iterations):
    # Calcula gradientes para cada dimensión del centro
    gradients = [0, 0, 0]
    for coord in coords:
      # Calcular la distancia entre la coord y el centro
      dist = ((coord[0] - center[0])**2 + (coord[1] - center[1])**2 + (coord[2] - center[2])**2)**0.5
      if dist > args.radius: # Si la coord no cabe en la esfera
        # Calcula gradientes basados en la distancia desde el centro
        gradients[0] += (coord[0] - center[0]) / dist
        gradients[1] += (coord[1] - center[1]) / dist
        gradients[2] += (coord[2] - center[2]) / dist
    # Ajustar el centro basado en gradientes
    center[0] -= learning_rate * gradients[0]
    center[1] -= learning_rate * gradients[1]
    center[2] -= learning_rate * gradients[2]
  
  # Calcular el número de coordenadas que caben en la esfera
  count = 0
  for coord in coords:
    dist = ((coord[0] - center[0])**2 + (coord[1] - center[1])**2 + (coord[2] - center[2])**2)**0.5
    if dist <= args.radius:
      count += 1
  return str(count) + ";" + ' '.join([str(elem) for elem in [round(n, 2) for n in center]])

resultado=[]
# Create a Pool with N worker processes
print("Pase 1/2")
with multiprocessing.Pool(args.threads) as pool:
    # Initialize the tqdm progress bar
    with tqdm(total=len(coords)) as pbar:
        for i, result in enumerate(pool.imap_unordered(process_coords, coords)):
            resultado.append(result)
            # Update the progress bar manually
            pbar.update()

# Flatten the resultado list
resultadoTmp = []
for test in resultado:
    if(test):
        resultadoTmp.append(tuple(test))

resultado=[]
for x in resultadoTmp:
        coordTmp=[]
        for coord in str(x).strip().replace("(","").replace(")","").replace("'","").split(", "):
            coordTmp.append([int(n) for n in coord.split(" ")])
        resultado.append(coordTmp)

# Create a Pool with N worker processes
print("Pase 2/2")
resultadoFinal=[]
with multiprocessing.Pool(args.threads) as pool:
    # Initialize the tqdm progress bar
    with tqdm(total=len(resultado)) as pbar:
        for i, result in enumerate(pool.imap_unordered(fit_sphere, resultado)):
            resultadoFinal.append(result)
            # Update the progress bar manually
            pbar.update()

with open(args.output, 'w') as f:
    for conjunto in sorted(set(resultadoFinal), reverse=True):
        f.write(f"{conjunto}\n")
