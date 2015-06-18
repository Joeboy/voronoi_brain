"""
Run from blender python console with:
exec(compile(open(filename).read(), filename, 'exec'))
"""


import bpy
import math
import random
import sys
from itertools import chain
# I don't know how to not hardcode this when running from blender (no __file__):
sys.path.append("/home/joe/building/blenderstuff/pytest/")
import imp
import voronoi_sphere
imp.reload(voronoi_sphere)


NUM_FACES = 100

# Clean up mess from any previous run:
for o in bpy.data.objects:
    if "Geodome" in o.name:
        try:
            bpy.context.scene.objects.unlink(o)
        except:
            pass
        bpy.data.objects.remove(o)


def get_random_point():
    """See https://www.cs.cmu.edu/~mws/rpos.html"""
    z = random.random() * 2 - 1
    phi = random.random() * 2 * math.pi
    theta = math.asin(z)
    x = math.cos(theta) * math.cos(phi)
    y = math.cos(theta) * math.sin(phi)
    return x, y, z


# Generate random points on surface of sphere. Each of these will end up
# being a voronoi face:
coords = [get_random_point() for _ in range(NUM_FACES)]
# Voronize them:
vs = voronoi_sphere.SphericalVoronoi(coords)

geomesh = bpy.data.meshes.new("Geomesh")   # create a new mesh  
geoob = bpy.data.objects.new("Geodome", geomesh)   # create an object with that mesh
geoob.location = bpy.context.scene.cursor_location   # position object at 3d-cursor
bpy.context.scene.objects.link(geoob)                # Link object to scene

# Get coords for voronoi faces' vertices:
vertices_coords = list(set([tuple(l) for l in chain(*[f.tolist() for f in vs.faces])]))

faces = []
# from_pydata wants lists of indexes of vertices as its faces param:
for f in vs.faces:
    faces.append([vertices_coords.index(tuple(v)) for v in f])

geomesh.from_pydata(vertices_coords, [], faces)

