import utm
import simplekml
import math
from shapely.geometry import Polygon
from shapely.geometry import Point

def round_polygon(polygon, d):
    # Trova i punti che costituiscono il poligono interno
    inner_points = list(polygon.exterior.coords)

    # Crea un buffer intorno al poligono interno per ottenere i bordi arrotondati
    outer_polygon = polygon.buffer(d, cap_style=3, join_style=1)

    # Rimuovi i buchi che potrebbero essere stati creati dal buffer
    if polygon.interiors:
        for interior in polygon.interiors:
            interior_ring = Polygon(interior)
            outer_polygon = outer_polygon.difference(interior_ring)

    return outer_polygon


# Funzione per calcolare i punti lungo un'ellisse
def calcola_scia(xo, yo, D, gradi):
    xc = xo-4*D*math.sin(gradi)
    yc = yo-4*D*math.cos(gradi)
    punti = []
    x = xo+D/2*math.cos(gradi)
    y = yo-D/2*math.sin(gradi) 
    punti.append((x, y))
    x = xo-D/2*math.cos(gradi)
    y = yo+D/2*math.sin(gradi) 
    punti.append((x, y))
    x = xc-D/2*math.cos(gradi)*1.7
    y = yc+D/2*math.sin(gradi)*1.7
    punti.append((x, y))
    x = xc+D/2*math.cos(gradi)*1.7
    y = yc-D/2*math.sin(gradi)*1.7 
    punti.append((x, y))
    x = xo+D/2*math.cos(gradi)
    y = yo-D/2*math.sin(gradi) 
    punti.append((x, y))
    return punti

# Funzione per ruotare i punti di un angolo alpha in senso orario
def ruota_punti(punti, xo, yo, alpha):
    punti_ruotati = []
    for x, y in punti:
        x_rot = xo + (x - xo) * math.cos(alpha) + (y - yo) * math.sin(alpha)
        y_rot = yo - (x - xo) * math.sin(alpha) + (y - yo) * math.cos(alpha)
        punti_ruotati.append((x_rot, y_rot))
    return punti_ruotati

# Funzione per convertire coordinate UTM in gradi decimali
def utm_to_latlon(utm_coord, zone_number):
    latlon_coord = utm.to_latlon(utm_coord[0], utm_coord[1], zone_number=zone_number, northern=True)
    return latlon_coord

# Leggi le coordinate xo, yo dal file di input
with open("coordinates", "r") as file:
    coordinate = [map(float, line.split()) for line in file]

# Definizioni dei parametri
D = float(input("Inserisci la lunghezza caratteristica: "))
lunghezza_asse_maggiore = 10 * D
lunghezza_asse_minore = 6 * D
numero_punti = 100
alpha_degrees = float(input("Inserisci l'angolo di rotazione dell'ellisse in senso orario rispetto all'asse verticale (in gradi): "))
alpha = alpha_degrees * (math.pi / 180)
zone_number = int(input("Inserisci il numero di zona UTM: "))
outer_dist = int(input("Inserisci i metri di buffer dalla scia: "))

# Crea un nuovo oggetto KML
kml = simplekml.Kml()

# Itera su ogni coppia di coordinate
for xo, yo in coordinate:
    # Calcola i punti lungo l'ellisse
    punti_scia = calcola_scia(xo, yo, D, alpha)

    # Converti le coordinate UTM ruotate in gradi decimali
    punti_latlon = [utm_to_latlon(coord, zone_number) for coord in punti_scia]

    # Crea un poligono con i vertici lungo l'ellisse ruotato
    poligono = kml.newpolygon(name=f"scia - ({xo}, {yo})")

    # Aggiungi i vertici al poligono
    poligono.outerboundaryis.coords = [(coord[1], coord[0]) for coord in punti_latlon]  # Inverti l'ordine delle coordinate

    # Calcola i punti lungo l'ellisse
    buffer_scia = round_polygon(Polygon(punti_scia), outer_dist)

    # Converti le coordinate UTM ruotate in gradi decimali
    print(f"{punti_scia}")
    print(f"{list(zip(*buffer_scia.exterior.coords.xy))}")
    buffer = list(zip(*buffer_scia.exterior.coords.xy))
    punti_latlon = [utm_to_latlon(coord, zone_number) for coord in buffer]

    # Crea un poligono con i vertici lungo l'ellisse ruotato
    poligono = kml.newpolygon(name=f"buffer scia - ({xo}, {yo})")

    # Aggiungi i vertici al poligono
    poligono.outerboundaryis.coords = [(coord[1], coord[0]) for coord in punti_latlon]  # Inverti l'ordine delle coordinate
# Salva il file KML
kml_file = "scia.kml"
kml.save(kml_file)

