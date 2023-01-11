import math
import argparse
import multiprocessing
from tqdm import tqdm

#parser = argparse.ArgumentParser(description='Toma una lista de multi spawners y una lista de estructuras, devulve la esctructura mas sercana al multi spawner',formatter_class=argparse.RawTextHelpFormatter)
parser = argparse.ArgumentParser(description='Toma una lista de multi spawners y una lista de estructuras, devulve la esctructura mas sercana al multi spawner')

parser.add_argument('spawner', type=str, help='archivo que contiene los multi spawner')
parser.add_argument('estructuras', type=str, help='archivo que contiene las estructuras')
parser.add_argument('output', type=str, help='archivo de salida')
parser.add_argument('--tipo', metavar='Tipo', type=str, default="any", help='Estructura a buscar, puede ser:, desert_pyramid, jungle_temple, igloo, swamp_hut, village, mansion, monument, ocean_ruin, shipwreck, treasure, mineshaft, outpost, ancient_city, ruined_portal, ruined_portal (nether), fortress, bastion, end_city, end_gateway, spawn, stronghold')
parser.add_argument('-t', '--threads', type=int, default=1, help='número de hilos a utilizar')

args = parser.parse_args()

def distance(x1, y1, z1, x2, y2, z2):
  # Calculate the distance between two 3D points (x1, y1, z1) and (x2, y2, z2)
  return math.sqrt((x1 - x2)**2 + (y1 - y2)**2 + (z1 - z2)**2)


# Read the 3D coordinates from the first file
with open(args.spawner, 'r') as f:
  lines = f.readlines()
  spawners = []
  for line in lines:
    #line = "7;-19434.0 -48.57 176.0"
    id = line.strip().split(';')[0]
    x, y, z = line.strip().split(';')[1].split(' ')
    x = float(x)
    y = float(y)
    z = float(z)
    spawners.append((x, y, z, id))

# Read the 2D coordinates from the second file
with open(args.estructuras, 'r') as f:
  structures = []
  lines = f.readlines()
  for line in lines:
    #line = "desert_pyramid;-22336;-912;"
    id, x, z, discard = line.strip().split(';')
    x = float(x)
    z = float(z)
    structures.append((x, z, id))

# Find the closest 3D coordinate with the matching id
def closest_sctructure(coord1):
  min_distance = float('inf')
  for coord2 in structures:
    if(args.tipo == coord2[2] or args.tipo == "any"):
        d = distance(coord1[0], 0, coord1[2], coord2[0], 0, coord2[1])
        if d < min_distance:
          min_distance = d
          structure = coord2[2].replace(" ","_")
  return(f'{coord1[3]}x spawner a {int(min_distance)} de {structure} (/tp {coord1[0]}, {coord1[1]}, {coord1[2]})')

resultadoFinal=[]
#for coord1 in spawners:
with multiprocessing.Pool(args.threads) as pool:
    # Initialize the tqdm progress bar
    with tqdm(total=len(spawners)) as pbar:
        for i, result in enumerate(pool.imap_unordered(closest_sctructure, spawners)):
            resultadoFinal.append(result)
            # Update the progress bar manually
            pbar.update()

with open(args.output, 'w') as f:
    for conjunto in sorted(resultadoFinal, key=lambda x: (int(x.split(" ")[0].split("x")[0])*-1, int(x.split(" ")[3]))):
      f.write(f"{conjunto}\n")
