from math import pi, cos, sin
import numpy as np


def view_nodes(nodes):
    for i, x in enumerate(nodes):
        print(f'Node {i} strat is {x.strat}, co-op is {x.coop}, defect is {x.defect}')


def point(x, y, r, thet):
    theta = thet * 2 * pi
    return y + cos(theta) * r, x + sin(theta) * r


def generate_circle(x, y, r, no_points):
    points = []
    for thet in [i / no_points for i in range(no_points)]:
        points.append(point(x, y, r, thet))
    return np.array(points)