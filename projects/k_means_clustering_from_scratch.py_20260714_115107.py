"""
Date: 2026-07-14
Implemented k-means clustering using only the standard library to really understand the distance calculations and centroid updates myself.
"""

"""
K-Means Clustering Implementation
A from-scratch implementation to learn how the algorithm actually works.
Uses standard library only - all the math is done manually.
"""

import random
import math


def euclidean_distance(point1, point2):
    """
    Calculate Euclidean distance between two points.
    Works for any dimensionality as long as both points have same length.
    """
    if len(point1) != len(point2):
        raise ValueError("Points must have same dimensionality")
    
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(point1, point2)))


def calculate_centroid(points):
    """
    Calculate the mean position (centroid) of a group of points.
    Returns None if the cluster is empty - happens sometimes during iterations.
    """
    if not points:
        return None
    
    dimensions = len(points[0])
    centroid = []
    
    for dim in range(dimensions):
        mean_value = sum(point[dim] for point in points) / len(points)
        centroid.append(mean_value)
    
    return tuple(centroid)


class KMeans:
    """
    K-Means clustering algorithm.
    
    I decided to track iteration count and whether convergence happened
    because it's useful to know if the algorithm actually settled or just
    hit the max iterations limit.
    """
    
    def __init__(self, k=3, max_iterations=100, tolerance=1e-4):
        """
        Initialize K-Means clusterer.
        
        Args:
            k: Number of clusters to find
            max_iterations: Stop after this many iterations even if not converged
            tolerance: If centroids move less than this, consider it converged
        """
        self.k = k
        self.max_iterations = max_iterations
        self.tolerance = tolerance
        self.centroids = []
        self.labels = []
        self.converged = False
        self.iterations = 0
    
    def _initialize_centroids(self, data):
        """
        Pick k random points from the dataset as initial centroids.
        Using random.sample to ensure we don't pick duplicates.
        """
        self.centroids = random.sample(data, self.k)
    
    def _assign_clusters(self, data):
        """
        Assign each point to the nearest centroid.
        Returns the cluster assignments as a list of indices.
        """
        assignments = []
        
        for point in data:
            # Find which centroid is closest to this point
            distances = [euclidean_distance(point, centroid) for centroid in self.centroids]
            closest_centroid = distances.index(min(distances))
            assignments.append(closest_centroid)
        
        return assignments
    
    def _update_centroids(self, data, assignments):
        """
        Recalculate centroids based on current cluster assignments.
        If a cluster becomes empty, we keep the old centroid - this can happen
        and it's a known edge case in k-means.
        """
        new_centroids = []
        
        for cluster_idx in range(self.k):
            # Get all points assigned to this cluster
            cluster_points = [data[i] for i in range(len(data)) if assignments[i] == cluster_idx]
            
            new_centroid = calculate_centroid(cluster_points)
            
            # Handle empty clusters by keeping the old centroid
            if new_centroid is None:
                new_centroid = self.centroids[cluster_idx]
            
            new_centroids.append(new_centroid)
        
        return new_centroids
    
    def _centroids_changed(self, old_centroids, new_centroids):
        """
        Check if centroids moved significantly.
        Using the tolerance threshold to decide if we've converged.
        """
        for old, new in zip(old_centroids, new_centroids):
            if euclidean_distance(old, new) > self.tolerance:
                return True
        return False
    
    def fit(self, data):
        """
        Run the k-means algorithm on the data.
        Main loop: assign points to clusters, update centroids, repeat.
        """
        if len(data) < self.k:
            raise ValueError(f"Cannot cluster {len(data)} points into {self.k} clusters")
        
        self._initialize_centroids(data)
        
        for iteration in range(self.max_iterations):
            # Assign each point to nearest centroid
            assignments = self._assign_clusters(data)
            
            # Update centroids based on assignments
            new_centroids = self._update_centroids(data, assignments)
            
            # Check for convergence
            if not self._centroids_changed(self.centroids, new_centroids):
                self.converged = True
                self.iterations = iteration + 1
                self.centroids = new_centroids
                self.labels = assignments
                break
            
            self.centroids = new_centroids
        else:
            # Loop completed without breaking - hit max iterations
            self.iterations = self.max_iterations
            self.labels = assignments
        
        return self
    
    def predict(self, data):
        """
        Assign new data points to the nearest centroid from training.
        """
        if not self.centroids:
            raise ValueError("Model not fitted yet - call fit() first")
        
        return self._assign_clusters(data)


if __name__ == "__main__":
    # Generate some fake 2D data with obvious clusters
    # I'm creating three groups manually so we can see if k-means finds them
    print("Generating synthetic data with 3 natural clusters...")
    
    random.seed(42)  # For reproducibility
    
    cluster1 = [(random.gauss(2, 0.5), random.gauss(2, 0.5)) for _ in range(30)]
    cluster2 = [(random.gauss(8, 0.5), random.gauss(3, 0.5)) for _ in range(30)]
    cluster3 = [(random.gauss(5, 0.5), random.gauss(8, 0.5)) for _ in range(30)]
    
    data = cluster1 + cluster2 + cluster3
    random.shuffle(data)  # Mix them up
    
    print(f"Created {len(data)} data points\n")
    
    # Run k-means
    print("Running K-Means with k=3...")
    kmeans = KMeans(k=3, max_iterations=100)
    kmeans.fit(data)
    
    print(f"Converged: {kmeans.converged}")
    print(f"Iterations: {kmeans.iterations}")
    print(f"\nFinal centroids:")
    for i, centroid in enumerate(kmeans.centroids):
        print(f"  Cluster {i}: ({centroid[0]:.2f}, {centroid[1]:.2f})")
    
    # Count cluster sizes
    print(f"\nCluster sizes:")
    for i in range(kmeans.k):
        count = kmeans.labels.count(i)
        print(f"  Cluster {i}: {count} points")
    
    # Test prediction on new points
    print(f"\nTesting prediction on new points:")
    test_points = [(2.1, 2.3), (7.9, 3.1), (5.2, 7.8)]
    predictions = kmeans.predict(test_points)
    
    for point, cluster in zip(test_points, predictions):
        print(f"  Point {point} -> Cluster {cluster}")