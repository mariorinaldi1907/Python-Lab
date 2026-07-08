"""
Date: 2026-07-08
Implemented k-means clustering using only standard library to understand how centroid-based clustering actually works under the hood.
"""

"""
K-Means Clustering from scratch
Implements the classic unsupervised learning algorithm without any ML libraries.
I wanted to really understand how k-means works internally, so I built it step by step.
"""

import random
import math


def euclidean_distance(point1, point2):
    """
    Calculate the Euclidean distance between two points.
    Works for any dimensionality as long as both points have the same number of features.
    """
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(point1, point2)))


def mean_point(points):
    """
    Calculate the centroid (mean) of a list of points.
    Returns the component-wise average across all dimensions.
    """
    if not points:
        return None
    
    dimensions = len(points[0])
    centroid = []
    
    for dim in range(dimensions):
        avg = sum(point[dim] for point in points) / len(points)
        centroid.append(avg)
    
    return centroid


class KMeans:
    """
    K-Means clustering implementation.
    
    The algorithm:
    1. Initialize k random centroids
    2. Assign each point to nearest centroid
    3. Recalculate centroids as mean of assigned points
    4. Repeat 2-3 until centroids stop moving (or max iterations)
    """
    
    def __init__(self, k=3, max_iterations=100, tolerance=1e-4):
        """
        Args:
            k: Number of clusters
            max_iterations: Stop after this many iterations even if not converged
            tolerance: If centroids move less than this, consider converged
        """
        self.k = k
        self.max_iterations = max_iterations
        self.tolerance = tolerance
        self.centroids = None
        self.labels = None
        self.iterations_run = 0
    
    def _initialize_centroids(self, data):
        """
        Initialize centroids by randomly selecting k points from the data.
        There are smarter ways (k-means++) but this is simpler and works fine.
        """
        return random.sample(data, self.k)
    
    def _assign_clusters(self, data):
        """
        Assign each data point to the nearest centroid.
        Returns a list of cluster labels (indices 0 to k-1).
        """
        labels = []
        
        for point in data:
            distances = [euclidean_distance(point, centroid) for centroid in self.centroids]
            closest_centroid = distances.index(min(distances))
            labels.append(closest_centroid)
        
        return labels
    
    def _update_centroids(self, data, labels):
        """
        Recalculate centroids as the mean of all points assigned to each cluster.
        If a cluster is empty, keep the old centroid (edge case handling).
        """
        new_centroids = []
        
        for cluster_idx in range(self.k):
            # Get all points assigned to this cluster
            cluster_points = [data[i] for i in range(len(data)) if labels[i] == cluster_idx]
            
            if cluster_points:
                new_centroids.append(mean_point(cluster_points))
            else:
                # Keep old centroid if cluster is empty
                new_centroids.append(self.centroids[cluster_idx])
        
        return new_centroids
    
    def _centroids_changed(self, old_centroids, new_centroids):
        """
        Check if centroids moved more than the tolerance threshold.
        Returns True if we should keep iterating.
        """
        for old, new in zip(old_centroids, new_centroids):
            if euclidean_distance(old, new) > self.tolerance:
                return True
        return False
    
    def fit(self, data):
        """
        Run the k-means algorithm on the data.
        
        Args:
            data: List of points, where each point is a list/tuple of numbers
        """
        # Initialize centroids randomly from the data
        self.centroids = self._initialize_centroids(data)
        
        for iteration in range(self.max_iterations):
            # Assign points to nearest centroid
            self.labels = self._assign_clusters(data)
            
            # Calculate new centroids
            new_centroids = self._update_centroids(data, self.labels)
            
            # Check for convergence
            if not self._centroids_changed(self.centroids, new_centroids):
                self.iterations_run = iteration + 1
                print(f"Converged after {self.iterations_run} iterations")
                break
            
            self.centroids = new_centroids
            self.iterations_run = iteration + 1
        else:
            print(f"Reached max iterations ({self.max_iterations})")
        
        return self
    
    def predict(self, point):
        """
        Predict which cluster a new point belongs to.
        """
        distances = [euclidean_distance(point, centroid) for centroid in self.centroids]
        return distances.index(min(distances))


if __name__ == "__main__":
    # Generate some synthetic 2D data with clear clusters
    # I'm making three blob-like clusters manually
    random.seed(42)  # For reproducible results
    
    cluster1 = [[random.gauss(2, 0.5), random.gauss(2, 0.5)] for _ in range(30)]
    cluster2 = [[random.gauss(8, 0.5), random.gauss(3, 0.5)] for _ in range(30)]
    cluster3 = [[random.gauss(5, 0.5), random.gauss(8, 0.5)] for _ in range(30)]
    
    data = cluster1 + cluster2 + cluster3
    random.shuffle(data)  # Mix them up so it's not trivial
    
    print("K-Means Clustering Demo")
    print("=" * 50)
    print(f"Dataset: {len(data)} points in 2D space")
    print(f"Looking for {3} clusters\n")
    
    # Run k-means
    kmeans = KMeans(k=3, max_iterations=100)
    kmeans.fit(data)
    
    print(f"\nFinal centroids:")
    for i, centroid in enumerate(kmeans.centroids):
        print(f"  Cluster {i}: ({centroid[0]:.2f}, {centroid[1]:.2f})")
    
    # Count points in each cluster
    print(f"\nCluster sizes:")
    for i in range(kmeans.k):
        count = kmeans.labels.count(i)
        print(f"  Cluster {i}: {count} points")
    
    # Test prediction on a new point
    test_point = [2.5, 2.5]
    predicted_cluster = kmeans.predict(test_point)
    print(f"\nTest point {test_point} assigned to cluster {predicted_cluster}")