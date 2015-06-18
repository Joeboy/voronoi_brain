""" Voronoi Tesseltion on a sphere
Code mostly borrowed from Lucas Wilkins,
http://jellymatter.com/2014/01/29/voronoi-tessellation-on-the-surface-of-a-sphere-python-code/"""
 
import operator
 
from numpy import dot, cross, sqrt, sum, array, arctan2
from scipy.spatial import ConvexHull
 
 
def list_dict_add(dic, key, val):
    if key in dic.keys():
        dic[key].append(val)
    else:
        dic[key]=[val]
 
class SphericalVoronoi(object):
    """
    Object representing the Voronoi tesselation on a sphere. Takes cartesian
    coordinates of points in 3D as input.
     
    Fields
    ------
    * vertices - vertices of the voronoi diagram
    * dual_vertices - original points (potentially re-ordered)
    * faces - voronoi regions for each input point
    * dual_face_indices - index of triangulation, normals all aligned
    * hull - scipy.spatial.ConvexHull object used for triangulation
     
     
    Note: If the convex hull of the points has faces that are not triangular it
    will give duplicate faces.
    """
     
    def __init__(self, points):
        points = array(points)
         
        if not points.shape[1] == 3:
            raise ValueError("Points must be spcified in cartesian coordinates")
             
        points = (points.T/sqrt(sum(points**2,1))).T
         
        self.hull = ConvexHull(points)
        self.dual_vertices = self.hull.points[self.hull.vertices,:]
         
        # find face normals (voronoi verts) and map to the original points
         
        face_index = 0
        self.dual_vertex_to_face_index = {}
        vertices = []
        self.dual_face_indices = []
         
        for tri in self.hull.simplices:
            tri_points = self.dual_vertices[tri,:]
             
 
            normal = cross(tri_points[1,:]-tri_points[0,:],
                           tri_points[2,:]-tri_points[0,:])
            normal /= sqrt(sum(normal**2))
             
            # we have to make sure the triangles have outward facing normals
            #  or the points will appear at the polar opposite point
            com = sum(tri_points,0)
            if dot(com, normal) < 0:
                vertices.append(-normal)
            else:
                vertices.append(normal)
             
            # store the index of the normal in a list for each face/orig. point
            for dual_index in tri:
                list_dict_add(self.dual_vertex_to_face_index,
                              dual_index, face_index)
             
            face_index+=1
         
        self.vertices = array(vertices)
         
        # store face coordinates
        faces = []
        for dual_index in self.hull.vertices:
            face_inds = self.dual_vertex_to_face_index[dual_index]
            #print(99)
            #print(face_inds)
            facepoints = self.vertices[face_inds,:]
            faces.append(facepoints)
         
        # Order the faces
        faces_ordered = []
        for face in faces:
            # find centre of mass
            npoints = face.shape[0]
             
            com = sum(face,0)/npoints
             
            # find the maximum direction to use a a projection (fast and sufficent)
            index, value = max(enumerate(abs(com)),
                               key=operator.itemgetter(1))
            inds = [i for i in range(3) if not i==index]
             
            com2d = com[inds]
            points2d = face[:,inds]
             
            points2d_minus_com = points2d - com2d
             
            # find order
            angles = arctan2(points2d_minus_com[:,0],
                             points2d_minus_com[:,1])
             
             
            indices = sorted(range(npoints), key=lambda k: angles[k])
            ordered = face[indices,:]
             
            # This will have ensured they are consistently either clockwise
            #  or anticlockwise, but we don't know which
             
            # check order direction relative to normal using first three points
            order_const = dot(com,
                              cross(ordered[0,:]-com,
                                    ordered[1,:]-com))
         
             
            if order_const < 0:
                ordered = ordered[::-1,:]
             
            faces_ordered.append(ordered)
             
        self.faces = faces_ordered
