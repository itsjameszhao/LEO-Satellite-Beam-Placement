# Optimal LEO Satellite Beam Placement

## Overview

This project focuses on designing an efficient algorithm for placing satellite beams in Low Earth Orbit (LEO) constellations to maximize coverage and optimize user connections. Utilizing advanced data structures such as k-d trees, along with optimization techniques like simulated annealing and a min-conflicts algorithm, this project ensures real-time user assignment with minimal conflicts and high spatial efficiency.

## Features

- **Maximized Coverage:** Efficiently places satellite beams to cover the maximum number of users within the LEO constellation.
- **Conflict Resolution:** Implements a min-conflicts algorithm to handle overlapping connections, ensuring optimal resource allocation.
- **Spatial Indexing:** Utilizes k-d trees for rapid spatial queries and Geohash for real-time user assignment.
- **Scalable Architecture:** Designed to handle large constellations and user bases with scalable performance.
- **Random Initialization:** Begins with a randomized assignment of users to satellites to facilitate effective conflict resolution.

## Technologies Used

- **Programming Language:** Python
- **Data Structures:** k-d Trees, Enums, Sets
- **Algorithms:** Min-Conflicts, Simulated Annealing
- **Libraries:** `math`, `enum`, `random`, `pdb`

## Installation

### Prerequisites

- Python 3.7 or higher

### Dependencies

This project relies on Python's standard libraries:
- `math`
- `enum`
- `random`
- `pdb`

No external libraries are required.

## Algorithm Details

### K-d Tree for Spatial Indexing

A k-d tree is used to efficiently query and manage spatial data, allowing rapid identification of users within a critical radius of each satellite. This optimizes the process of determining eligible users for connection.

### Min-Conflicts Algorithm

The min-conflicts algorithm is employed to iteratively resolve conflicts in user-satellite assignments. It minimizes the number of conflicting connections by reassigning users to alternative satellites or colors, ensuring stable and optimal assignments.

### Conflict Detection

Conflicts are identified based on color and angular proximity. Connections with the same color and an angle less than a predefined threshold (e.g., 10 degrees) are considered conflicting and are subject to resolution.
