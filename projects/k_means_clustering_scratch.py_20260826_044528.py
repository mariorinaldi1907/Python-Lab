"""
Date: 2026-08-26
Implemented k-means clustering without any ML libraries to really understand how the Lloyd's algorithm works under the hood.
"""

"""
K-Means Clustering from Scratch
--------------------------------
A pure Python implementation of the k-means clustering algorithm.
Uses Lloyd's algorithm with k-means++ initialization for better convergence.
"""

import random
import math


class KMeans:
    """
    K-Means clustering implementation using Lloyd's algorithm.
    
    This was fun to build because it really shows how simple the core idea is:
    just keep assigning points to nearest centroids and updating centroids
    until things stop moving around.
    """
    
    def __init__(self, k=3, max_iterations=100, tolerance=1e-4):
        """
        Initialize the k-means clusterer.
        
        Args:
            k: Number of clusters to find
            max_iterations: Stop after this many iterations even if not converged
            tolerance: If centroids move less than this, consider it converged
        """
        self.k = k
        self.max_iterations = max_iterations
        self.tolerance = tolerance
        self.centroids = None
        self.labels = None
    
    def _distance(self, point1, point2):
        """Calculate Euclidean distance between two points."""
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(point1, point2)))
    
    def _initialize_centroids_plus_plus(self, data):
        """
        Use k-means++ initialization instead of random selection.
        This spreads out initial centroids to improve convergence.
        
        The idea: pick first centroid randomly, then each subsequent centroid
        is chosen with probability proportional to squared distance from nearest
        existing centroid.
        """
        centroids = [random.choice(data)]
        
        for _ in range(1, self.k):
            distances = []
            for point in data:
                # Find distance to nearest existing centroid
                min_dist = min(self._distance(point, c) for c in centroids)
                distances.append(min_dist ** 2)
            
            # Weighted random selection
            total = sum(distances)
            if total == 0:
                # All points are on top of existing centroids somehow
                centroids.append(random.choice(data))
            else:
                probabilities = [d / total for d in distances]
                centroids.append(self._weighted_choice(data, probabilities))
        
        return centroids
    
    def _weighted_choice(self, items, weights):
        """Choose an item with probability proportional to its weight."""
        r = random.random() * sum(weights)
        cumulative = 0
        for item, weight in zip(items, weights):
            cumulative += weight
            if r <= cumulative:
                return item
        return items[-1]
    
    def _assign_clusters(self, data):
        """Assign each point to the nearest centroid."""
        labels = []
        for point in data:
            distances = [self._distance(point, centroid) for centroid in self.centroids]
            labels.append(distances.index(min(distances)))
        return labels
    
    def _update_centroids(self, data, labels):
        """Recalculate centroids as the mean of assigned points."""
        new_centroids = []
        for cluster_id in range(self.k):
            # Get all points in this cluster
            cluster_points = [data[i] for i in range(len(data)) if labels[i] == cluster_id]
            
            if cluster_points:
                # Calculate mean for each dimension
                dimensions = len(cluster_points[0])
                centroid = [
                    sum(point[d] for point in cluster_points) / len(cluster_points)
                    for d in range(dimensions)
                ]
                new_centroids.append(centroid)
            else:
                # Empty cluster - keep old centroid or reinitialize
                new_centroids.append(self.centroids[cluster_id])
        
        return new_centroids
    
    def fit(self, data):
        """
        Run k-means clustering on the data.
        
        Args:
            data: List of points, where each point is a list/tuple of coordinates
        """
        # Initialize centroids using k-means++
        self.centroids = self._initialize_centroids_plus_plus(data)
        
        for iteration in range(self.max_iterations):
            # Assign points to nearest centroid
            self.labels = self._assign_clusters(data)
            
            # Update centroids
            new_centroids = self._update_centroids(data, self.labels)
            
            # Check for convergence - did centroids move significantly?
            max_shift = max(
                self._distance(old, new)
                for old, new in zip(self.centroids, new_centroids)
            )
            
            self.centroids = new_centroids
            
            if max_shift < self.tolerance:
                print(f"Converged after {iteration + 1} iterations")
                break
        else:
            print(f"Stopped after {self.max_iterations} iterations")
        
        return self
    
    def predict(self, data):
        """Assign cluster labels to new data points."""
        return self._assign_clusters(data)


if __name__ == "__main__":
    # Generate some synthetic 2D data with obvious clusters
    # I'm making three blobs at different locations
    random.seed(42)
    
    def make_blob(center_x, center_y, n_points=20, spread=0.5):
        """Create a cluster of points around a center."""
        return [
            [center_x + random.gauss(0, spread), center_y + random.gauss(0, spread)]
            for _ in range(n_points)
        ]
    
    # Three clusters centered at different locations
    blob1 = make_blob(0, 0, n_points=25)
    blob2 = make_blob(5, 5, n_points=25)
    blob3 = make_blob(1, 5, n_points=25)
    
    data = blob1 + blob2 + blob3
    
    print("K-Means Clustering Demo")
    print("=" * 50)
    print(f"Generated {len(data)} points in 3 clusters\n")
    
    # Fit k-means
    kmeans = KMeans(k=3, max_iterations=50)
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
    test_points = [[0, 0], [5, 5], [1, 5]]
    predictions = kmeans.predict(test_points)
    
    print("\nTest predictions:")
    for point, label in zip(test_points, predictions):
        print(f"  Point {point} -> Cluster {label}")