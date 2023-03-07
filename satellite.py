import math
from enum import Enum
import pdb
import random

USER_ANGLE_DEGREES = 45
SATELLITE_ANGLE_DEGREES = 10

class Colors(Enum):
    Blue = 0
    Green = 1
    Red = 2
    Yellow = 3

class Satellite:
    def __init__(self, id, x, y, z, visible_users):
        self.id = id
        self.x = x
        self.y = y
        self.z = z
        self.visible_users = visible_users
        self.current_connections = set()

    def addUsersCanConnect(self, users):
        self.visible_users = users

    def addUser(self, user):
        self.visible_users.add(user)

    def addConnection(self, connection):
        self.current_connections.add(connection)

    def removeConnection(self, connection):
        self.current_connections.remove(connection)

    def removeConflictingConnections(self):
        connections_to_remove = set()
        for conn1 in self.current_connections:
            for conn2 in self.current_connections:
                if self.areConflictingConnections(conn1, conn2):
                        connections_to_remove.add(conn1)
                        connections_to_remove.add(conn2)
        for conn in connections_to_remove:
            conn.user.current_connection = None
            self.current_connections.remove(conn)

    def findRandomConflictedConnection(self):
        connections = list(self.current_connections)
        random.shuffle(connections)
        for conn1 in connections:
            for conn2 in connections:
                if self.areConflictingConnections(conn1, conn2):
                        return conn1, conn2
        return None

    def getAlternativeMinConflictConnection(self, conflict_connection, unassigned_users):
        candidates = []
        candidate_users = {conflict_connection.user}.union(self.visible_users.intersection(unassigned_users)) # union of current user and all unassigned users
        for user in candidate_users:
            for color in Colors:
                # create an alternate connection for this user and color
                alt_connection = SatelliteConnection(
                    sat_id=self.id,
                    conn_id=conflict_connection.conn_id,
                    user=user,
                    color=color
                )
                # count the number of conflicting connections
                num_conflicts = self.getNumConflictingConnections(alt_connection)
                candidates.append((alt_connection, num_conflicts))

        # choose the alternate connection with the lowest score
        candidates.sort(key=lambda x: x[1])
        min_score = candidates[0][1]
        best_candidates = [c for c in candidates if c[1] == min_score]

        return random.choice(best_candidates)[0]

    def getNumConflictingConnections(self, connection):
        # similar to removeConflictingConnections(), but counts instead of removing
        num_conflicts = 0
        for conn in self.current_connections:
            if self.areConflictingConnections(conn, connection):
                num_conflicts += 1
        return num_conflicts

    def areConflictingConnections(self, conn1, conn2):
        if conn1 == conn2:
                return False
        if conn1.color == conn2.color:
            angle = self.angleBetweenConnections(conn1, conn2)
            if angle < 10:
                return True
            return False
    
    def angleBetweenConnections(self, connection1, connection2):
        point1 = connection1.user.get_coordinates()
        point2 = connection2.user.get_coordinates()
        vector1 = [point1[0] - self.x, point1[1] - self.y, point1[2] - self.z]
        vector2 = [point2[0] - self.x, point2[1] - self.y, point2[2] - self.z]
        dot_product = sum([a * b for a, b in zip(vector1, vector2)])
        magnitude1 = math.sqrt(sum([a * a for a in vector1]))
        magnitude2 = math.sqrt(sum([a * a for a in vector2]))
        cosine_angle = round(dot_product / (magnitude1 * magnitude2), 3)
        return math.degrees(math.acos(cosine_angle))

class SatelliteConnection:
    def __init__(self, sat_id, conn_id, user, color):
        self.sat_id = sat_id # sat ID number
        self.conn_id = conn_id # 1-32
        self.user = user # user object
        self.color = color # color enum

class User:
    def __init__(self, id, x, y, z):
        self.id = id
        self.x = x
        self.y = y
        self.z = z
        self.current_connection = None

    def get_coordinates(self):
        return (self.x, self.y, self.z)

class KDNode:
    def __init__(self, point=None, axis=None, left=None, right=None):
        self.point = point
        self.axis = axis
        self.left = left
        self.right = right

class KDTree:
    def __init__(self, points=None):
        self.root = None
        if points is not None:
            self.build(points)

    def build(self, points):
        self.root = self._build(points)

    def _build(self, points, depth=0):
        if len(points) == 0:
            return None
        axis = depth % 3
        sorted_points = sorted(points, key=lambda x: x[axis])
        mid = len(points) // 2
        return KDNode(
            point=sorted_points[mid],
            axis=axis,
            left=self._build(sorted_points[:mid], depth + 1),
            right=self._build(sorted_points[mid+1:], depth + 1)
        )

    def ball_query(self, center, r):
        result = set()
        self._ball_query(self.root, center, r, result)
        return result

    def _ball_query(self, node, center, r, indices):
        if node is None:
            return
        dist = math.sqrt(sum([pow(node.point[i] - center[i], 2) for i in range(3)]))
        if dist <= r:
            indices.add(node.point)
        if node.left is not None and center[node.axis] - r <= node.point[node.axis]:
            self._ball_query(node.left, center, r, indices)
        if node.right is not None and center[node.axis] + r >= node.point[node.axis]:
            self._ball_query(node.right, center, r, indices)

class StarlinkManager:
    def __init__(self, user_coords, satellite_coords):
        self.kdtree = KDTree(user_coords)
        self.users = [User(i, *user_coord) for i, user_coord in enumerate(user_coords)]
        self.r = math.sqrt(user_coords[0][0] ** 2 + user_coords[0][1] ** 2 + user_coords[0][2] ** 2)
        self.point_to_user_mapping = {user_coord : user for user_coord, user in zip(user_coords, self.users)}
        self.satellites = [Satellite(j, *satellite_coord, visible_users=None) for j, satellite_coord in enumerate(satellite_coords)]
        self.unassigned_users = set(self.users)
        for satellite in self.satellites:
            visible_users = self.findSatelliteEligibleUsers(satellite)
            satellite.addUsersCanConnect(visible_users)

    def findSatelliteEligibleUsers(self, satellite):
        self.d = math.sqrt(satellite.x ** 2 + satellite.y ** 2 + satellite.z ** 2)
        # critical radius to query k-d tree, worked out using geometry
        critical_radius = math.sqrt(2) * self.d * math.sin(math.pi / 4 - math.asin(1/math.sqrt(2) * self.r / self.d))
        points = self.kdtree.ball_query((satellite.x, satellite.y, satellite.z),critical_radius)
        return set(self.point_to_user_mapping[point] for point in points)

    def randomInit(self):
        for satellite in self.satellites:
            # get unassigned users for the current satellite
            for _ in range(32):
                unassigned_users = satellite.visible_users.intersection(self.unassigned_users)
                if len(unassigned_users) == 0:
                    break # break out of inner loop
                # randomly select an unassigned user and assign a random color
                user = random.choice(list(unassigned_users))
                color = random.choice(list(Colors))
                connection = SatelliteConnection(satellite.id, len(satellite.current_connections) + 1, user, color)
                satellite.addConnection(connection)
                user.current_connection = connection
                self.unassigned_users.remove(user)

    def minConflicts(self, max_steps):
        for _ in range(max_steps):
            # shuffle satellites randomly
            random.shuffle(self.satellites)
            # loop through all satellites
            for satellite in self.satellites:
                # find a random conflicted connection
                conflict_connections = satellite.findRandomConflictedConnection()
                if conflict_connections is not None:
                    # get the alternative connection with the minimum conflicts
                    alternative_connection = satellite.getAlternativeMinConflictConnection(conflict_connections[0], self.unassigned_users)
                    # remove the conflicted connection and add the alternative connection
                    satellite.removeConnection(conflict_connections[0])
                    satellite.addConnection(alternative_connection)
        
    def cleanUp(self):
        for satellite in self.satellites:
            satellite.removeConflictingConnections()

    def generateResult(self):
        result = []
        for sat in self.satellites:
            for conn in sat.current_connections:
                result.append((sat.id, conn.user.id))
        return result

    def run(self):
        self.randomInit()
        N = 32 * len(self.satellites)
        num_steps = 2 * N 
        self.minConflicts(num_steps)
        self.cleanUp()
        return self.generateResult()