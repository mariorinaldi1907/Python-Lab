"""
Date: 2026-08-22
Built k-means clustering from scratch to understand how centroid-based clustering actually works under the hood — no sklearn needed.
"""

"""
K-Means Clustering Implementation
A from-scratch implementation of the k-means algorithm using only Python stdlib.
I wanted to really understand how the iterative centroid update process works.
"""

import random
import math


def euclidean_distance(point1, point2):
    """
    Calculate the Euclidean distance between two points.
    
    Args:
        point1: List/tuple of numeric coordinates
        point2: List/tuple of numeric coordinates
    
    Returns:
        Float representing the distance
    """
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(point1, point2)))


def mean_point(points):
    """
    Calculate the mean/centroid of a collection of points.
    
    Args:
        points: List of points, where each point is a list/tuple of coordinates
    
    Returns:
        List representing the mean point, or None if points is empty
    """
    if not points:
        return None
    
    dimensions = len(points[0])
    # For each dimension, calculate the average across all points
    return [sum(p[d] for p in points) / len(points) for d in range(dimensions)]


class KMeans:
    """
    K-Means clustering algorithm implementation.
    
    The algorithm:
    1. Initialize k random centroids
    2. Assign each point to nearest centroid
    3. Update centroids to mean of assigned points
    4. Repeat steps 2-3 until convergence
    """
    
    def __init__(self, k=3, max_iterations=100, tolerance=1e-4):
        """
        Initialize the KMeans clusterer.
        
        Args:
            k: Number of clusters to form
            max_iterations: Maximum number of iterations to run
            tolerance: Convergence threshold (if centroids move less than this, stop)
        """
        self.k = k
        self.max_iterations = max_iterations
        self.tolerance = tolerance
        self.centroids = None
        self.labels = None
        self.iterations_run = 0
    
    def _initialize_centroids(self, data):
        """
        Initialize centroids by randomly selecting k points from the dataset.
        This is the simplest initialization strategy (Forgy method).
        
        Args:
            data: List of data points
        """
        # Just pick k random points from our data as starting centroids
        self.centroids = random.sample(data, self.k)
    
    def _assign_clusters(self, data):
        """
        Assign each data point to the nearest centroid.
        
        Args:
            data: List of data points
        
        Returns:
            List of cluster labels (indices) for each data point
        """
        labels = []
        for point in data:
            # Find the closest centroid for this point
            distances = [euclidean_distance(point, centroid) for centroid in self.centroids]
            closest_centroid = distances.index(min(distances))
            labels.append(closest_centroid)
        return labels
    
    def _update_centroids(self, data, labels):
        """
        Update centroids to be the mean of all points assigned to each cluster.
        
        Args:
            data: List of data points
            labels: List of cluster assignments
        
        Returns:
            List of new centroids
        """
        new_centroids = []
        for cluster_idx in range(self.k):
            # Get all points that belong to this cluster
            cluster_points = [data[i] for i in range(len(data)) if labels[i] == cluster_idx]
            
            if cluster_points:
                # Calculate the mean of these points
                new_centroids.append(mean_point(cluster_points))
            else:
                # If a cluster has no points, keep the old centroid
                # (in practice, this might warrant re-initialization)
                new_centroids.append(self.centroids[cluster_idx])
        
        return new_centroids
    
    def _has_converged(self, old_centroids, new_centroids):
        """
        Check if the algorithm has converged by comparing centroid movement.
        
        Args:
            old_centroids: Previous iteration's centroids
            new_centroids: Current iteration's centroids
        
        Returns:
            Boolean indicating whether convergence criterion is met
        """
        for old, new in zip(old_centroids, new_centroids):
            if euclidean_distance(old, new) > self.tolerance:
                return False
        return True
    
    def fit(self, data):
        """
        Run the k-means algorithm on the provided data.
        
        Args:
            data: List of data points (each point is a list/tuple of numbers)
        """
        # Start with random centroids
        self._initialize_centroids(data)
        
        for iteration in range(self.max_iterations):
            # Assign points to nearest centroid
            labels = self._assign_clusters(data)
            
            # Update centroids based on assigned points
            new_centroids = self._update_centroids(data, labels)
            
            # Check for convergence
            if self._has_converged(self.centroids, new_centroids):
                self.centroids = new_centroids
                self.labels = labels
                self.iterations_run = iteration + 1
                break
            
            self.centroids = new_centroids
        else:
            # If we didn't break (didn't converge), save final state
            self.labels = labels
            self.iterations_run = self.max_iterations
        
        return self
    
    def predict(self, data):
        """
        Predict cluster labels for new data points.
        
        Args:
            data: List of data points to classify
        
        Returns:
            List of predicted cluster labels
        """
        if self.centroids is None:
            raise ValueError("Model hasn't been fitted yet. Call fit() first.")
        
        return self._assign_clusters(data)


if __name__ == "__main__":
    # Generate some simple 2D test data with clear clusters
    # I'm creating three "blobs" of points manually
    random.seed(42)  # For reproducibility
    
    cluster_1 = [[random.uniform(0, 2), random.uniform(0, 2)] for _ in range(20)]
    cluster_2 = [[random.uniform(5, 7), random.uniform(5, 7)] for _ in range(20)]
    cluster_3 = [[random.uniform(0, 2), random.uniform(5, 7)] for _ in range(20)]
    
    data = cluster_1 + cluster_2 + cluster_3
    random.shuffle(data)
    
    print("K-Means Clustering Demo")
    print("=" * 50)
    print(f"Dataset: {len(data)} points in 2D space")
    print(f"Looking for k=3 clusters\n")
    
    # Fit the model
    kmeans = KMeans(k=3, max_iterations=100, tolerance=1e-4)
    kmeans.fit(data)
    
    print(f"Converged in {kmeans.iterations_run} iterations")
    print("\nFinal Centroids:")
    for i, centroid in enumerate(kmeans.centroids):
        print(f"  Cluster {i}: ({centroid[0]:.2f}, {centroid[1]:.2f})")
    
    # Show cluster sizes
    print("\nCluster Sizes:")
    for i in range(kmeans.k):
        count = kmeans.labels.count(i)
        print(f"  Cluster {i}: {count} points")
    
    # Test prediction on a few new points
    print("\nPredicting clusters for new points:")
    test_points = [[1, 1], [6, 6], [1, 6]]
    predictions = kmeans.predict(test_points)
    for point, cluster in zip(test_points, predictions):
        print(f"  Point {point} -> Cluster {cluster}")