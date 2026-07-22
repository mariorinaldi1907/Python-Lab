"""
Date: 2026-07-22
Built a k-means clustering algorithm without any ML libraries to really understand how centroid assignment and iteration works under the hood.
"""

"""
K-Means Clustering Implementation from Scratch

This is my take on implementing k-means without relying on sklearn or numpy.
I wanted to understand the algorithm at a fundamental level, so I built it
using only Python's standard library. The core idea is simple: assign points
to the nearest centroid, then recalculate centroids based on those assignments.
Repeat until convergence (or max iterations).
"""

import random
import math


class KMeans:
    """
    K-Means clustering implementation using only Python standard library.
    
    The algorithm alternates between:
    1. Assignment step: assign each point to nearest centroid
    2. Update step: recalculate centroids as mean of assigned points
    """
    
    def __init__(self, k=3, max_iterations=100, tolerance=1e-4):
        """
        Initialize K-Means clustering.
        
        Args:
            k: Number of clusters
            max_iterations: Maximum iterations before stopping
            tolerance: If centroids move less than this, we've converged
        """
        self.k = k
        self.max_iterations = max_iterations
        self.tolerance = tolerance
        self.centroids = None
        self.labels = None
    
    def _euclidean_distance(self, point1, point2):
        """
        Calculate euclidean distance between two points.
        Works for any dimensionality.
        """
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(point1, point2)))
    
    def _initialize_centroids(self, data):
        """
        Initialize centroids by randomly selecting k points from the dataset.
        This is the "forgy" method - simple but effective.
        """
        return random.sample(data, self.k)
    
    def _assign_clusters(self, data):
        """
        Assign each point to the nearest centroid.
        Returns a list of cluster labels (0 to k-1).
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
        Recalculate centroids as the mean of all points assigned to each cluster.
        This is where the "means" in k-means comes from.
        """
        new_centroids = []
        
        for cluster_idx in range(self.k):
            # Get all points assigned to this cluster
            cluster_points = [data[i] for i in range(len(data)) 
                            if labels[i] == cluster_idx]
            
            if cluster_points:
                # Calculate mean for each dimension
                dimensions = len(cluster_points[0])
                centroid = []
                for dim in range(dimensions):
                    mean_value = sum(point[dim] for point in cluster_points) / len(cluster_points)
                    centroid.append(mean_value)
                new_centroids.append(centroid)
            else:
                # If a cluster is empty, keep the old centroid
                # (or we could reinitialize it randomly)
                new_centroids.append(self.centroids[cluster_idx])
        
        return new_centroids
    
    def _has_converged(self, old_centroids, new_centroids):
        """
        Check if centroids have moved less than tolerance threshold.
        If so, we've converged and can stop iterating.
        """
        for old, new in zip(old_centroids, new_centroids):
            if self._euclidean_distance(old, new) > self.tolerance:
                return False
        return True
    
    def fit(self, data):
        """
        Run the k-means algorithm on the dataset.
        
        Args:
            data: List of points, where each point is a list/tuple of coordinates
        """
        # Start with random centroids
        self.centroids = self._initialize_centroids(data)
        
        for iteration in range(self.max_iterations):
            # Assignment step
            self.labels = self._assign_clusters(data)
            
            # Update step
            new_centroids = self._update_centroids(data, self.labels)
            
            # Check for convergence
            if self._has_converged(self.centroids, new_centroids):
                print(f"Converged after {iteration + 1} iterations")
                break
            
            self.centroids = new_centroids
        else:
            print(f"Reached max iterations ({self.max_iterations})")
        
        return self
    
    def predict(self, data):
        """
        Assign new data points to the nearest centroid.
        """
        return self._assign_clusters(data)


def generate_blob(center, n_points, spread=0.5):
    """
    Generate a cluster of points around a center.
    Used for creating synthetic test data.
    """
    points = []
    for _ in range(n_points):
        point = [c + random.gauss(0, spread) for c in center]
        points.append(point)
    return points


if __name__ == "__main__":
    # Generate some synthetic 2D data with 3 clear clusters
    # I'm creating three "blobs" of points to test the algorithm
    print("Generating synthetic data with 3 clusters...")
    
    cluster1 = generate_blob([2.0, 2.0], 30, spread=0.4)
    cluster2 = generate_blob([8.0, 3.0], 30, spread=0.5)
    cluster3 = generate_blob([5.0, 8.0], 30, spread=0.6)
    
    all_data = cluster1 + cluster2 + cluster3
    random.shuffle(all_data)  # Shuffle so clusters aren't in order
    
    print(f"Generated {len(all_data)} points")
    print("\nRunning K-Means with k=3...")
    
    # Fit the model
    kmeans = KMeans(k=3, max_iterations=100, tolerance=1e-4)
    kmeans.fit(all_data)
    
    # Display results
    print("\nFinal centroids:")
    for i, centroid in enumerate(kmeans.centroids):
        print(f"  Cluster {i}: ({centroid[0]:.2f}, {centroid[1]:.2f})")
    
    # Count points in each cluster
    print("\nCluster sizes:")
    for i in range(kmeans.k):
        count = kmeans.labels.count(i)
        print(f"  Cluster {i}: {count} points")
    
    # Test prediction on a new point
    test_point = [[2.5, 2.5]]
    prediction = kmeans.predict(test_point)
    print(f"\nTest point {test_point[0]} assigned to cluster {prediction[0]}")