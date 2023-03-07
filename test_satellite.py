import unittest
import cProfile
from pstats import Stats
import numpy as np
import pdb
from satellite import *
from test_utils import *

class TestSatellite(unittest.TestCase):
    def setUp(self):
        self.pr = cProfile.Profile()
        self.pr.enable()

    def tearDown(self):
        p = Stats(self.pr)
        p.strip_dirs()
        p.sort_stats('cumtime')
        p.print_stats()
        print("\n--->>>")

    def test_build_kdtree(self):
        points = [(1, 2, 3), (4, 5, 6), (7, 8, 9)]
        kdtree = KDTree(points)
        self.assertEqual(kdtree.root.point, (4, 5, 6))
        self.assertEqual(kdtree.root.left.point, (1, 2, 3))
        self.assertEqual(kdtree.root.right.point, (7, 8, 9))

    def test_ball_query_kdtree(self):
        points = [(1, 2, 3), (4, 5, 6), (7, 8, 9)]
        kdtree = KDTree(points)
        indices = kdtree.ball_query((0, 0, 0), 5)
        self.assertEqual(indices, {points[0]})

    def test_ball_query_kdtree_extensive(self):
        # generate 500 random points
        points = [(random.uniform(-100, 100), random.uniform(-100, 100), random.uniform(-100, 100)) for i in range(500)]
        print(f"testing on points {points}")
        kdtree = KDTree(points)

        # test ball_query on 10 random centers and radii
        for i in range(10):
            center = (random.uniform(-100, 100), random.uniform(-100, 100), random.uniform(-100, 100))
            print(f"generated center is {center}")
            r = random.uniform(1, 100)
            result = kdtree.ball_query(center, r)

            # check that all points within radius are returned
            for point in points:
                if np.linalg.norm(np.array(point) - np.array(center)) <= r:
                    self.assertIn(point, result)
                    # print("AssertIn passed")

            # check that no points outside radius are returned
            for point in points:
                if np.linalg.norm(np.array(point) - np.array(center)) > r:
                    self.assertNotIn(point, result)
                    # print("AssertNotIn passed")


    def test_angle_between(self):
        satellite = Satellite(0, 0, 0, 0, set())
        user1 = User(1, 1, 0, 0)
        user2 = User(2, 0, 1, 0)
        connection1 = SatelliteConnection(0, 0, user1, Colors.Blue)
        connection2 = SatelliteConnection(0, 1, user2, Colors.Green)
        angle = satellite.angleBetweenConnections(connection1, connection2)
        self.assertAlmostEqual(angle, 90.0, delta=0.001)
        print("Test angle between passed")

    def test_remove_no_connections(self):
        user1 = User(1, 1, 1, 1)
        user2 = User(2, 2, 2, 2)
        sat = Satellite(1, 0, 0, 0, {user1, user2})
        conn1 = SatelliteConnection(1, 1, user1, Colors.Blue)
        conn2 = SatelliteConnection(1, 2, user2, Colors.Green)
        sat.current_connections = {conn1, conn2}
        sat.removeConflictingConnections()
        self.assertEqual(sat.current_connections, {conn1, conn2})

    def test_remove_two_connections(self):
        user1 = User(1, 1, 1, 1)
        user2 = User(2, 2, 2, 2)
        user3 = User(3, 3, 3, 3)
        sat = Satellite(1, 0, 0, 0, {user1, user2, user3})
        conn1 = SatelliteConnection(1, 1, user1, Colors.Blue)
        conn2 = SatelliteConnection(1, 2, user2, Colors.Blue)
        conn3 = SatelliteConnection(1, 3, user3, Colors.Blue)
        sat.current_connections = {conn1, conn2, conn3}
        sat.removeConflictingConnections()
        self.assertEqual(sat.current_connections, set())

    def test_find_random_conflicted_connection(self):
        # Create a satellite
        sat = Satellite(0, 0, 0, 0, set())
        
        # Add a user
        user1 = User(1, 1, 0, 0)
        user2 = User(1, 0.996, 0.087, 0)
        user3 = User(1, 0.966, 0.2588, 0)
        sat.addUser(user1)
        
        # Add two connections with same color and an angle of 5 degrees
        conn1 = SatelliteConnection(1, 1, user1, Colors.Blue)
        conn2 = SatelliteConnection(1, 2, user2, Colors.Blue)
        sat.addConnection(conn1)
        sat.addConnection(conn2)
        
        # Test that either conn1 or conn2 is returned
        res = sat.findRandomConflictedConnection()
        self.assertTrue(res == (conn1, conn2) or res == (conn2, conn1))
        
        # Add another connection with different color and an angle of 15 degrees
        conn3 = SatelliteConnection(1, 3, user3, Colors.Red)
        sat.addConnection(conn3)
        
        # Test that either conn1 or conn2 is returned
        res = sat.findRandomConflictedConnection()
        self.assertTrue(res == (conn1, conn2) or res == (conn2, conn1))
        
        # Remove conn1 and conn2
        sat.removeConnection(conn1)
        sat.removeConnection(conn2)
        
        # Test that nothing is returned
        res = sat.findRandomConflictedConnection()
        self.assertEqual(res, None)

    def test_getAlternativeMinConflictConnection(self):
        # create a satellite with some visible and current connections
        user1 = User(1, 1, 1, 1)
        user2 = User(2, 2, 2, 2)
        user3 = User(3, 3, 3, 3)
        user4 = User(4, 4, 4, 4)
        user5 = User(5, -5, -5, -5)
        sat = Satellite(id=0, x=0, y=0, z=0, visible_users={user1, user2, user3, user4, user5})
        sat.addConnection(SatelliteConnection(0, 1, user1, Colors.Blue))
        sat.addConnection(SatelliteConnection(0, 2, user2, Colors.Green))
        sat.addConnection(SatelliteConnection(0, 3, user3, Colors.Red))

        # No unassigned users
        unassigned_users = set()

        # test on a conflict with Blue, Red, and Green connections
        conflict_connection = SatelliteConnection(0, 4, user4, Colors.Red)
        alt_conn = sat.getAlternativeMinConflictConnection(conflict_connection, unassigned_users)
        self.assertEqual(alt_conn.color, Colors.Yellow)

        # add colors full for the (1,1,1) direction but another user available in the opposite direction
        sat.addConnection(SatelliteConnection(0, 4, user4, Colors.Yellow))
        unassigned_users.add(user5)
        conflict_connection = SatelliteConnection(0, 4, user4, Colors.Red) # conflict along same direction
        alt_conn = sat.getAlternativeMinConflictConnection(conflict_connection, unassigned_users)
        self.assertEqual(alt_conn.user.id, 5)

    def test_getNumConflictingConnections(self):
        # create some users
        user1 = User(1, 0, 0, 0)
        user2 = User(2, 1, 1, 1)
        user3 = User(3, 2, 2, 2)
        user4 = User(4, 3, 3, 3)
        user5 = User(5, 4, 4, 4)

        # create some satellite connections
        conn1 = SatelliteConnection(1, 1, user1, Colors.Blue)
        conn2 = SatelliteConnection(1, 2, user2, Colors.Green)
        conn3 = SatelliteConnection(1, 3, user3, Colors.Red)
        conn4 = SatelliteConnection(1, 4, user4, Colors.Yellow)
        conn5 = SatelliteConnection(1, 5, user5, Colors.Yellow)

        # create a satellite with connections
        sat = Satellite(1, 0, 0, 0, {user1, user2, user3, user4, user5})
        sat.addConnection(conn1)
        sat.addConnection(conn2)
        sat.addConnection(conn3)
        sat.addConnection(conn4)
        sat.addConnection(conn5)

        # test cases
        self.assertEqual(sat.getNumConflictingConnections(conn1), 0)  # no conflicts
        self.assertEqual(sat.getNumConflictingConnections(conn2), 0)  # no conflicts
        self.assertEqual(sat.getNumConflictingConnections(conn3), 0)  # no conflicts
        self.assertEqual(sat.getNumConflictingConnections(conn4), 1)  # conflict with 5
        self.assertEqual(sat.getNumConflictingConnections(conn5), 1)  # conflict with 4

    def test_init_starlink(self):
        # Test case 1: Two users and two satellites
        user_coords = [(-1, -1, -1), (1, 1, 1)]
        satellite_coords = [(2, 1, 2), (1, 2, 1)]
        manager = StarlinkManager(user_coords, satellite_coords)
        self.assertEqual(len(manager.users), 2)
        self.assertEqual(len(manager.satellites), 2)
        self.assertEqual(manager.r, math.sqrt(3))

    def test_findSatelliteEligibleUsers(self):
        # Test Case 1: Two users, one eligible, one not
        user_coords = [(1, 1, 1), (-1, -1, -1)]
        satellite_coords = [(2, 2, 2)]
        manager = StarlinkManager(user_coords, satellite_coords)
        satellite = manager.satellites[0]
        eligible_user = manager.users[0]
        non_eligible_user = manager.users[1]
        eligible_users = manager.findSatelliteEligibleUsers(satellite)
        assert eligible_user in eligible_users
        assert non_eligible_user not in eligible_users

        # Test Case 2: Multiple users, some eligible
        user_coords = generateTestUsers(100, 100)
        satellite_coords = generateTestSatellites(1, 100, 200)
        manager = StarlinkManager(user_coords, satellite_coords)
        satellite = manager.satellites[0]
        eligible_users = manager.findSatelliteEligibleUsers(satellite)
        for user in eligible_users:
            user_normal_vector = user_coords[manager.users.index(user)]
            user_to_sat_vector = (satellite.x - user.x, satellite.y - user.y, satellite.z - user.z)
            user_angle = angle_between_vectors(user_normal_vector, user_to_sat_vector)
            assert user_angle <= math.pi/4

        non_eligible_users = set(manager.users) - set(eligible_users)
        for user in non_eligible_users:
            user_normal_vector = (user.x, user.y, user.z)
            user_to_sat_vector = (satellite.x - user.x, satellite.y - user.y, satellite.z - user.z)
            user_angle = angle_between_vectors(user_normal_vector, user_to_sat_vector)
            assert user_angle > math.pi/4

    def test_randomInit(self):
        num_satellites = 500
        num_users = 500000
        user_coords = generateTestUsers(int(math.sqrt(num_users)), 1)
        satellite_coords = generateTestSatellites(num_satellites, 1.08, 1.09)
        manager = StarlinkManager(user_coords, satellite_coords)
        manager.randomInit()
        
        # Test 1: Every satellite has 32 connections and each connection has a color (one of red, blue, green, and yellow)
        for satellite in manager.satellites:
            assert len(satellite.current_connections) == 32
            for connection in satellite.current_connections:
                assert connection.color in Colors

        # Test 2: There are 32 * num_satellites users with a satellite connection that is not none
        users_with_connection = [user for user in manager.users if user.current_connection is not None]
        assert len(users_with_connection) == num_satellites * 32

        # Test 3: Each user that is connected is connected to only one satellite
        connections_per_user = {}
        for user in manager.users:
            if user.current_connection is not None:
                if user in connections_per_user:
                    assert False, "User connected to multiple satellites"
                connections_per_user[user] = user.current_connection
        assert len(connections_per_user) == num_satellites * 32

        # Test 4: No two connections among all the satellites are connected to the same user
        connections = [connection for satellite in manager.satellites for connection in satellite.current_connections]
        users = [connection.user for connection in connections]
        assert len(set(users)) == len(users), "Two connections connected to the same user"


