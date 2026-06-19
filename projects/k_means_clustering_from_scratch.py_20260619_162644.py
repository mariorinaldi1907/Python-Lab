"""
Date: 2026-06-19
Built k-means clustering without any ML libraries to really understand how the algorithm converges through iterative centroid updates.
"""

#!/usr/bin/env python3
"""
K-Means Clustering from Scratch
================================
A pure Python implementation of the k-means clustering algorithm.
No external dependencies - just math and random for distance calculations.

I wanted to understand how k-means actually works under the hood,
so I built this to see the centroid updates happening step by step.
"""

import random
import math


class KMeans:
    """
    K-Means clustering implementation.
    
    The algorithm works by:
    1. Randomly initializing k centroids
    2. Assigning each point to its nearest centroid
    3. Updating centroids to be the mean of assigned points
    4. Repeating steps 2-3 until convergence (or max iterations)
    """
    
    def __init__(self, k=3, max_iterations=100, tolerance=1e-4):
        """
        Initialize the K-Means clusterer.
        
        Args:
            k: Number of clusters to find
            max_iterations: Maximum number of iterations before stopping
            tolerance: If centroids move less than this, we've converged
        """
        self.k = k
        self.max_iterations = max_iterations
        self.tolerance = tolerance
        self.centroids = None
        self.labels = None
        
    def _euclidean_distance(self, point1, point2):
        """
        Calculate Euclidean distance between two points.
        
        Using the classic sqrt(sum of squared differences) formula.
        """
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(point1, point2)))
    
    def _initialize_centroids(self, data):
        """
        Randomly select k data points as initial centroids.
        
        There are fancier initialization methods (like k-means++),
        but random selection works fine for most cases.
        """
        return random.sample(data, self.k)
    
    def _assign_clusters(self, data):
        """
        Assign each data point to its nearest centroid.
        
        Returns a list of cluster indices (0 to k-1) for each point.
        """
        labels = []
        for point in data:
            # Find the closest centroid for this point
            distances = [self._euclidean_distance(point, centroid) 
                        for centroid in self.centroids]
            closest_centroid = distances.index(min(distances))
            labels.append(closest_centroid)
        return labels
    
    def _update_centroids(self, data, labels):
        """
        Update centroids to be the mean of all points assigned to them.
        
        This is the key step where the centroids "move" toward their clusters.
        """
        new_centroids = []
        
        for cluster_idx in range(self.k):
            # Get all points assigned to this cluster
            cluster_points = [data[i] for i in range(len(data)) 
                            if labels[i] == cluster_idx]
            
            if cluster_points:
                # Calculate mean of all points in this cluster
                # Using zip(*cluster_points) to transpose: [(x1,y1), (x2,y2)] -> [(x1,x2), (y1,y2)]
                centroid = [sum(coords) / len(coords) 
                           for coords in zip(*cluster_points)]
            else:
                # If a cluster is empty (rare), keep the old centroid
                centroid = self.centroids[cluster_idx]
            
            new_centroids.append(centroid)
        
        return new_centroids
    
    def _has_converged(self, old_centroids, new_centroids):
        """
        Check if centroids have stopped moving significantly.
        
        Convergence happens when all centroids move less than our tolerance.
        """
        for old, new in zip(old_centroids, new_centroids):
            if self._euclidean_distance(old, new) > self.tolerance:
                return False
        return True
    
    def fit(self, data):
        """
        Run the k-means algorithm on the data.
        
        Args:
            data: List of data points (each point is a list/tuple of coordinates)
        
        Returns:
            self (for method chaining)
        """
        # Start with random centroids
        self.centroids = self._initialize_centroids(data)
        
        for iteration in range(self.max_iterations):
            # Assign each point to nearest centroid
            self.labels = self._assign_clusters(data)
            
            # Update centroids based on assignments
            old_centroids = self.centroids
            self.centroids = self._update_centroids(data, self.labels)
            
            # Check if we've converged
            if self._has_converged(old_centroids, self.centroids):
                print(f"Converged after {iteration + 1} iterations")
                break
        else:
            print(f"Stopped after {self.max_iterations} iterations (max reached)")
        
        return self
    
    def predict(self, data):
        """
        Assign new data points to the nearest existing centroid.
        
        Args:
            data: List of data points to classify
            
        Returns:
            List of cluster labels
        """
        if self.centroids is None:
            raise ValueError("Must call fit() before predict()")
        
        return self._assign_clusters(data)


if __name__ == "__main__":
    # Generate some synthetic 2D data with three obvious clusters
    random.seed(42)  # For reproducibility
    
    # Cluster 1: points around (2, 2)
    cluster1 = [[2 + random.gauss(0, 0.5), 2 + random.gauss(0, 0.5)] for _ in range(30)]
    
    # Cluster 2: points around (8, 3)
    cluster2 = [[8 + random.gauss(0, 0.5), 3 + random.gauss(0, 0.5)] for _ in range(30)]
    
    # Cluster 3: points around (5, 8)
    cluster3 = [[5 + random.gauss(0, 0.5), 8 + random.gauss(0, 0.5)] for _ in range(30)]
    
    # Combine all data
    data = cluster1 + cluster2 + cluster3
    random.shuffle(data)  # Mix them up
    
    print("Running K-Means Clustering on 90 2D points...")
    print(f"Looking for k=3 clusters\n")
    
    # Fit the model
    kmeans = KMeans(k=3, max_iterations=100)
    kmeans.fit(data)
    
    print("\nFinal centroids:")
    for i, centroid in enumerate(kmeans.centroids):
        print(f"  Cluster {i}: ({centroid[0]:.2f}, {centroid[1]:.2f})")
    
    # Count points in each cluster
    print("\nCluster sizes:")
    for i in range(kmeans.k):
        count = kmeans.labels.count(i)
        print(f"  Cluster {i}: {count} points")
    
    # Test prediction on new points
    print("\nTesting prediction on new points:")
    test_points = [[2.1, 2.3], [7.9, 2.8], [5.2, 8.1]]
    predictions = kmeans.predict(test_points)
    
    for point, label in zip(test_points, predictions):
        print(f"  Point {point} -> Cluster {label}")