"""
Date: 2026-06-26
Built k-means clustering without any ML libraries to really understand how the algorithm assigns points to centroids and iteratively improves clusters.
"""

#!/usr/bin/env python3
"""
K-means clustering implementation from scratch.
Uses only standard library — no numpy, no sklearn, just pure Python.
"""

import random
import math


def euclidean_distance(point1, point2):
    """
    Calculate Euclidean distance between two points.
    
    Args:
        point1: List or tuple of coordinates
        point2: List or tuple of coordinates
    
    Returns:
        Float representing the distance
    """
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(point1, point2)))


def mean_of_points(points):
    """
    Calculate the mean (centroid) of a list of points.
    
    Args:
        points: List of points (each point is a list/tuple of coordinates)
    
    Returns:
        List representing the mean point
    """
    if not points:
        return None
    
    dimensions = len(points[0])
    return [sum(point[d] for point in points) / len(points) for d in range(dimensions)]


class KMeans:
    """
    K-means clustering algorithm implementation.
    
    The algorithm works by:
    1. Randomly initializing k centroids
    2. Assigning each point to the nearest centroid
    3. Recalculating centroids as the mean of assigned points
    4. Repeating steps 2-3 until convergence
    """
    
    def __init__(self, k=3, max_iterations=100, tolerance=1e-4):
        """
        Initialize K-means clusterer.
        
        Args:
            k: Number of clusters
            max_iterations: Maximum number of iterations to run
            tolerance: Convergence threshold (if centroids move less than this, stop)
        """
        self.k = k
        self.max_iterations = max_iterations
        self.tolerance = tolerance
        self.centroids = None
        self.labels = None
    
    def fit(self, data):
        """
        Fit the k-means model to the data.
        
        Args:
            data: List of data points (each point is a list/tuple of numbers)
        """
        # Initialize centroids randomly by picking k random points from data
        self.centroids = random.sample(data, self.k)
        
        for iteration in range(self.max_iterations):
            # Assign each point to the nearest centroid
            clusters = [[] for _ in range(self.k)]
            self.labels = []
            
            for point in data:
                # Find the closest centroid
                distances = [euclidean_distance(point, centroid) for centroid in self.centroids]
                closest_centroid = distances.index(min(distances))
                clusters[closest_centroid].append(point)
                self.labels.append(closest_centroid)
            
            # Calculate new centroids
            new_centroids = []
            for cluster in clusters:
                if cluster:  # Only update if cluster has points
                    new_centroids.append(mean_of_points(cluster))
                else:
                    # If a cluster is empty, reinitialize randomly
                    new_centroids.append(random.choice(data))
            
            # Check for convergence — if centroids barely moved, we're done
            centroid_shift = sum(
                euclidean_distance(old, new)
                for old, new in zip(self.centroids, new_centroids)
            )
            
            self.centroids = new_centroids
            
            if centroid_shift < self.tolerance:
                print(f"Converged after {iteration + 1} iterations")
                break
        else:
            print(f"Reached max iterations ({self.max_iterations})")
    
    def predict(self, data):
        """
        Predict cluster labels for new data points.
        
        Args:
            data: List of data points
        
        Returns:
            List of cluster labels (integers 0 to k-1)
        """
        labels = []
        for point in data:
            distances = [euclidean_distance(point, centroid) for centroid in self.centroids]
            labels.append(distances.index(min(distances)))
        return labels


if __name__ == "__main__":
    # Generate some synthetic 2D data with clear clusters
    # I'm creating three groups of points manually to see if k-means finds them
    random.seed(42)  # For reproducibility
    
    print("=== K-Means Clustering Demo ===\n")
    
    # Cluster 1: points around (2, 2)
    cluster1 = [[2 + random.gauss(0, 0.5), 2 + random.gauss(0, 0.5)] for _ in range(30)]
    
    # Cluster 2: points around (8, 8)
    cluster2 = [[8 + random.gauss(0, 0.5), 8 + random.gauss(0, 0.5)] for _ in range(30)]
    
    # Cluster 3: points around (2, 8)
    cluster3 = [[2 + random.gauss(0, 0.5), 8 + random.gauss(0, 0.5)] for _ in range(30)]
    
    # Combine all data
    data = cluster1 + cluster2 + cluster3
    
    print(f"Generated {len(data)} data points in 3 natural clusters")
    print(f"Running k-means with k=3...\n")
    
    # Fit k-means
    kmeans = KMeans(k=3, max_iterations=100)
    kmeans.fit(data)
    
    print(f"\nFinal centroids:")
    for i, centroid in enumerate(kmeans.centroids):
        print(f"  Cluster {i}: [{centroid[0]:.2f}, {centroid[1]:.2f}]")
    
    # Count points in each cluster
    cluster_counts = [kmeans.labels.count(i) for i in range(kmeans.k)]
    print(f"\nCluster sizes:")
    for i, count in enumerate(cluster_counts):
        print(f"  Cluster {i}: {count} points")
    
    # Test prediction on new points
    print(f"\nTesting prediction on new points:")
    test_points = [[2.5, 2.5], [8.0, 8.0], [2.0, 8.5]]
    predictions = kmeans.predict(test_points)
    for point, label in zip(test_points, predictions):
        print(f"  Point {point} -> Cluster {label}")