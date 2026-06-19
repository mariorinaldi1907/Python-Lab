"""
Date: 2026-06-19
Built k-means clustering with random initialization and convergence detection — wanted to really understand how cluster assignments work under the hood.
"""

#!/usr/bin/env python3
"""
K-Means Clustering from scratch using only the standard library.

I wanted to understand how k-means actually works without relying on sklearn,
so I built this to see the centroid updates and convergence happen step by step.
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


class KMeans:
    """
    K-Means clustering implementation.
    
    I'm using random initialization here, though k-means++ would be smarter.
    The algorithm iterates until centroids stop moving or max_iter is reached.
    """
    
    def __init__(self, k=3, max_iter=100, tolerance=1e-4):
        """
        Initialize K-Means clusterer.
        
        Args:
            k: Number of clusters
            max_iter: Maximum iterations before stopping
            tolerance: If centroids move less than this, we've converged
        """
        self.k = k
        self.max_iter = max_iter
        self.tolerance = tolerance
        self.centroids = None
        self.labels = None
        
    def _initialize_centroids(self, data):
        """
        Randomly select k points from data as initial centroids.
        
        I'm just picking random samples here — good enough for learning,
        though production code should probably use k-means++.
        """
        return random.sample(data, self.k)
    
    def _assign_clusters(self, data):
        """
        Assign each point to the nearest centroid.
        
        Returns a list where index i contains the cluster assignment for data[i].
        """
        labels = []
        for point in data:
            # Find the closest centroid
            distances = [euclidean_distance(point, centroid) for centroid in self.centroids]
            closest_cluster = distances.index(min(distances))
            labels.append(closest_cluster)
        return labels
    
    def _update_centroids(self, data, labels):
        """
        Recalculate centroids as the mean of all points in each cluster.
        
        This is the core of k-means — moving the centroids to the center
        of their assigned points.
        """
        new_centroids = []
        
        for cluster_idx in range(self.k):
            # Get all points assigned to this cluster
            cluster_points = [data[i] for i in range(len(data)) if labels[i] == cluster_idx]
            
            if cluster_points:
                # Calculate mean across each dimension
                dimensions = len(cluster_points[0])
                centroid = [
                    sum(point[dim] for point in cluster_points) / len(cluster_points)
                    for dim in range(dimensions)
                ]
                new_centroids.append(centroid)
            else:
                # If a cluster is empty, keep the old centroid
                # (This can happen with unlucky initialization)
                new_centroids.append(self.centroids[cluster_idx])
        
        return new_centroids
    
    def _centroids_changed(self, old_centroids, new_centroids):
        """
        Check if centroids have moved more than the tolerance threshold.
        
        We use this to detect convergence and stop early.
        """
        for old, new in zip(old_centroids, new_centroids):
            if euclidean_distance(old, new) > self.tolerance:
                return True
        return False
    
    def fit(self, data):
        """
        Run the k-means algorithm on the data.
        
        Args:
            data: List of points, where each point is a list/tuple of coordinates
        """
        # Initialize centroids randomly
        self.centroids = self._initialize_centroids(data)
        
        for iteration in range(self.max_iter):
            # Assign each point to nearest centroid
            self.labels = self._assign_clusters(data)
            
            # Calculate new centroids
            new_centroids = self._update_centroids(data, self.labels)
            
            # Check for convergence
            if not self._centroids_changed(self.centroids, new_centroids):
                print(f"Converged after {iteration + 1} iterations")
                break
            
            self.centroids = new_centroids
        else:
            print(f"Stopped after {self.max_iter} iterations (max reached)")
        
        return self
    
    def predict(self, data):
        """
        Assign new data points to the nearest cluster.
        
        Args:
            data: List of points to classify
        
        Returns:
            List of cluster labels
        """
        if self.centroids is None:
            raise ValueError("Model hasn't been fitted yet — call fit() first")
        
        return self._assign_clusters(data)


if __name__ == "__main__":
    # Create some synthetic 2D data for testing
    # I'm making three obvious clusters to see if k-means finds them
    random.seed(42)
    
    cluster1 = [[random.gauss(2, 0.5), random.gauss(2, 0.5)] for _ in range(30)]
    cluster2 = [[random.gauss(8, 0.6), random.gauss(3, 0.6)] for _ in range(30)]
    cluster3 = [[random.gauss(5, 0.5), random.gauss(8, 0.5)] for _ in range(30)]
    
    data = cluster1 + cluster2 + cluster3
    random.shuffle(data)  # Mix them up so it's not trivial
    
    print("Running K-Means clustering on 90 synthetic 2D points...")
    print(f"Data range: x=[{min(p[0] for p in data):.2f}, {max(p[0] for p in data):.2f}], "
          f"y=[{min(p[1] for p in data):.2f}, {max(p[1] for p in data):.2f}]")
    print()
    
    # Fit the model
    kmeans = KMeans(k=3, max_iter=100, tolerance=1e-4)
    kmeans.fit(data)
    
    print("\nFinal centroids:")
    for i, centroid in enumerate(kmeans.centroids):
        print(f"  Cluster {i}: ({centroid[0]:.2f}, {centroid[1]:.2f})")
    
    # Show cluster sizes
    print("\nCluster sizes:")
    for i in range(kmeans.k):
        count = kmeans.labels.count(i)
        print(f"  Cluster {i}: {count} points")
    
    # Test prediction on new points
    print("\nTesting prediction on new points:")
    test_points = [[2.1, 2.0], [8.0, 3.2], [5.0, 7.8]]
    predictions = kmeans.predict(test_points)
    for point, cluster in zip(test_points, predictions):
        print(f"  Point {point} -> Cluster {cluster}")