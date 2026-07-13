"""
Date: 2026-07-13
Implemented k-means clustering algorithm without any ML libraries to really understand how the centroid updates and assignment steps work together.
"""

"""
K-Means Clustering Implementation from Scratch
I wanted to understand the actual mechanics of k-means without scikit-learn doing
the heavy lifting, so I built it using only standard library math functions.
"""

import random
import math


class KMeans:
    """
    K-Means clustering algorithm implementation.
    
    The algorithm works by:
    1. Randomly initializing k centroids
    2. Assigning each point to the nearest centroid
    3. Updating centroids to be the mean of assigned points
    4. Repeating steps 2-3 until convergence or max iterations
    """
    
    def __init__(self, k=3, max_iterations=100, tolerance=1e-4):
        """
        Initialize the K-Means clusterer.
        
        Args:
            k: Number of clusters
            max_iterations: Maximum number of iterations to run
            tolerance: Convergence threshold (if centroids move less than this, stop)
        """
        self.k = k
        self.max_iterations = max_iterations
        self.tolerance = tolerance
        self.centroids = []
        self.labels = []
    
    def _euclidean_distance(self, point1, point2):
        """
        Calculate Euclidean distance between two points.
        
        I'm using the standard sqrt(sum of squared differences) formula here.
        """
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(point1, point2)))
    
    def _initialize_centroids(self, data):
        """
        Randomly initialize k centroids from the dataset.
        
        This is a simple approach - just pick k random points.
        Smarter methods like k-means++ exist but this works fine for my purposes.
        """
        return random.sample(data, self.k)
    
    def _assign_clusters(self, data):
        """
        Assign each data point to the nearest centroid.
        
        Returns a list of cluster labels (indices) for each point.
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
        Update centroids to be the mean of all points assigned to each cluster.
        
        This is where the "means" in k-means comes from.
        """
        new_centroids = []
        for i in range(self.k):
            # Get all points assigned to cluster i
            cluster_points = [data[j] for j in range(len(data)) if labels[j] == i]
            
            if cluster_points:
                # Calculate mean of all dimensions
                dimensions = len(cluster_points[0])
                new_centroid = [
                    sum(point[dim] for point in cluster_points) / len(cluster_points)
                    for dim in range(dimensions)
                ]
                new_centroids.append(new_centroid)
            else:
                # If a cluster has no points, keep the old centroid
                # This can happen with unlucky initialization
                new_centroids.append(self.centroids[i])
        
        return new_centroids
    
    def _has_converged(self, old_centroids, new_centroids):
        """
        Check if centroids have moved less than the tolerance threshold.
        
        This lets us stop early if the algorithm has stabilized.
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
            # Assign points to nearest centroid
            self.labels = self._assign_clusters(data)
            
            # Update centroids based on assignments
            new_centroids = self._update_centroids(data, self.labels)
            
            # Check for convergence
            if self._has_converged(self.centroids, new_centroids):
                print(f"Converged after {iteration + 1} iterations")
                break
            
            self.centroids = new_centroids
        else:
            print(f"Reached max iterations ({self.max_iterations})")
        
        return self
    
    def predict(self, point):
        """
        Predict which cluster a new point belongs to.
        """
        distances = [self._euclidean_distance(point, centroid) 
                    for centroid in self.centroids]
        return distances.index(min(distances))


def generate_synthetic_data(n_samples=150, n_clusters=3):
    """
    Generate synthetic 2D data with clear clusters for testing.
    
    Each cluster is generated around a random center with some gaussian noise.
    """
    data = []
    samples_per_cluster = n_samples // n_clusters
    
    for i in range(n_clusters):
        # Random center for this cluster
        center_x = random.uniform(-10, 10)
        center_y = random.uniform(-10, 10)
        
        # Generate points around this center
        for _ in range(samples_per_cluster):
            # Add gaussian-ish noise (using uniform as approximation)
            x = center_x + random.uniform(-2, 2)
            y = center_y + random.uniform(-2, 2)
            data.append([x, y])
    
    return data


if __name__ == "__main__":
    # Set seed for reproducibility in this demo
    random.seed(42)
    
    print("Generating synthetic 2D data with 3 clusters...")
    data = generate_synthetic_data(n_samples=150, n_clusters=3)
    
    print("\nRunning K-Means clustering...")
    kmeans = KMeans(k=3, max_iterations=100)
    kmeans.fit(data)
    
    print("\nFinal centroids:")
    for i, centroid in enumerate(kmeans.centroids):
        print(f"  Cluster {i}: ({centroid[0]:.2f}, {centroid[1]:.2f})")
    
    # Count points in each cluster
    cluster_sizes = [kmeans.labels.count(i) for i in range(kmeans.k)]
    print("\nCluster sizes:")
    for i, size in enumerate(cluster_sizes):
        print(f"  Cluster {i}: {size} points")
    
    # Test prediction on a new point
    test_point = [5.0, 5.0]
    predicted_cluster = kmeans.predict(test_point)
    print(f"\nTest point {test_point} assigned to cluster {predicted_cluster}")