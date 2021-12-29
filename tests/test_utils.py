import unittest
import numpy as np
from xfab import tools
from xrd_simulator import utils
from scipy.spatial.transform import Rotation

class TestUtils(unittest.TestCase):

    def setUp(self):
        np.random.seed(10) # changes all randomisation in the test

    def test_clip_line_with_convex_polyhedron(self):
        line_points    = np.ascontiguousarray( [[-1.,0.2,0.2],[-1.,0.4,0.6]] )
        line_direction = np.ascontiguousarray( [1.0, 0.0, 0.0] )
        line_direction = line_direction/np.linalg.norm(line_direction)
        plane_points   = np.ascontiguousarray( [[0.,0.5,0.5], [1,0.5,0.5], [0.5,0.5,0.], [0.5,0.5,1.], [0.5,0,0.5], [0.5,1.,0.5]] )
        plane_normals  = np.ascontiguousarray( [[-1.,0.,0.],[1.,0.,0.], [0.,0.,-1.],[0.,0.,1.], [0.,-1.,0.],[0.,1.,0.]] )
        clip_lengths   = utils.clip_line_with_convex_polyhedron( line_points, line_direction, plane_points, plane_normals )
        for l in clip_lengths: 
            self.assertAlmostEqual(l, 1.0, msg="Projection through unity cube should give unity clip length")

        line_direction = np.ascontiguousarray( [1.0, 0.2, 0.1] )
        line_direction = line_direction/np.linalg.norm(line_direction)
        clip_lengths   = utils.clip_line_with_convex_polyhedron( line_points, line_direction, plane_points, plane_normals )
        for l in clip_lengths: 
            self.assertGreater(l, 1.0, msg="Titlted projection through unity cube should give greater than unity clip length")

    def test_lab_strain_to_lattice_matrix(self):

        U = Rotation.random().as_matrix()
        strain_tensor = (np.random.rand(3,3)-0.5)/100. # random small strain tensor
        strain_tensor = (strain_tensor.T + strain_tensor)/2.
        unit_cell = [5.028, 5.028, 5.519, 90., 90., 120.]
        B = utils.lab_strain_to_lattice_matrix(strain_tensor, U, unit_cell)

        n_c = np.random.rand(3,) # crystal unit vector
        n_c = n_c / np.linalg.norm(n_c)
        n_l = np.dot( U, n_c ) # lab unit vector

        # strain along n_l described in lab frame
        strain_l = np.dot( np.dot( n_l, strain_tensor ), n_l) 
        s = tools.b_to_epsilon( B, unit_cell )
        crystal_strain = np.array([[s[0],s[1],s[2]],[s[1],s[3],s[4]],[s[2],s[4],s[5]]])

        # strain along n_l described in crystal frame
        strain_c = np.dot( np.dot( n_c, crystal_strain ), n_c) 

        # The strain should be invariant along a direction
        self.assertAlmostEqual(strain_l, strain_c, msg="bad crystal to lab frame conversion")

    def test_alpha_to_quarternion(self):
        _, alpha_2, alpha_3 = np.random.rand(3,)
        q = utils.alpha_to_quarternion(0, alpha_2, alpha_3)
        self.assertAlmostEqual(q[0], 1.0, "quarternion wrongly computed")
        self.assertAlmostEqual(q[1], 0.0, "quarternion wrongly computed")
        self.assertAlmostEqual(q[2], 0.0, "quarternion wrongly computed")
        self.assertAlmostEqual(q[3], 0.0, "quarternion wrongly computed")
        alpha_1 = np.random.rand(7,)
        alpha_2 = np.random.rand(7,)
        alpha_3 = np.random.rand(7,)
        qq = utils.alpha_to_quarternion(alpha_1, alpha_2, alpha_3)
        for q in qq:
            print(np.linalg.norm(q))
            self.assertTrue(np.abs(np.linalg.norm(q)-1.0)<1e-5,"quarternion not unit length")

if __name__ == '__main__':
    unittest.main()