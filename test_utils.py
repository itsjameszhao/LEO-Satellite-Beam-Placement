import random
import math
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def generateTestUsers(n, r):
    # generate n evenly-spaced angles
    angles = [(2*math.pi*i)/n for i in range(n)]
    # generate n evenly-spaced inclinations
    inclinations = [(math.pi*i)/(n-1) for i in range(n)]
    # create list of (x, y, z) user coordinates
    user_coords = [(r*math.sin(incl)*math.cos(ang), r*math.sin(incl)*math.sin(ang), r*math.cos(incl)) for incl in inclinations for ang in angles]
    # shuffle user_coords
    random.shuffle(user_coords)
    return user_coords

def generateTestSatellites(m, a, b):
    # generate m random radii
    radii = [random.uniform(a, b) for i in range(m)]
    # generate m random angles
    angles = [random.uniform(0, 2*math.pi) for i in range(m)]
    # generate m random inclinations
    inclinations = [math.acos(random.uniform(-1, 1)) for i in range(m)]
    # create list of (x, y, z) satellite coordinates
    satellite_coords = [(r*math.sin(incl)*math.cos(ang), r*math.sin(incl)*math.sin(ang), r*math.cos(incl)) for r, incl, ang in zip(radii, inclinations, angles)]
    return satellite_coords

def visualize_points(points):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter([p[0] for p in points], [p[1] for p in points], [p[2] for p in points])
    plt.show()

def angle_between_vectors(a, b):
    dot_product = a[0]*b[0] + a[1]*b[1] + a[2]*b[2]
    magnitude_a = math.sqrt(a[0]**2 + a[1]**2 + a[2]**2)
    magnitude_b = math.sqrt(b[0]**2 + b[1]**2 + b[2]**2)
    return math.acos(round(dot_product / (magnitude_a * magnitude_b), 5))