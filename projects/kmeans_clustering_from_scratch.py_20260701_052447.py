"""
Date: 2026-07-01
Built k-means clustering from scratch to really understand how centroid updates work — includes demo with random 2D data points.
"""

import random
import math


class KMeans:
    """
    K-Means clustering implementation from scratch.
    
    I wanted to understand how centroids actually move during iterations,
    so I built this without numpy or sklearn. Uses Euclidean distance and
    iterative centroid updates until convergence (or max iterations).
    """
    
    def __init__(self, k=3, max_iterations=100, tolerance=1e-4):
        """
        Initialize K-Means clustering.
        
        Args:
            k: Number of clusters
            max_iterations: Stop after this many iterations even if not converged
            tolerance: If centroids move less than this, we've converged
        """
        self.k = k
        self.max_iterations = max_iterations
        self.tolerance = tolerance
        self.centroids = None
        self.labels = None
    
    def _euclidean_distance(self, point1, point2):
        """Calculate Euclidean distance between two points."""
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(point1, point2)))
    
    def _initialize_centroids(self, data):
        """
        Pick k random data points as initial centroids.
        
        I chose random initialization over k-means++ here because
        I wanted to keep it simple and see how well it works anyway.
        """
        return random.sample(data, self.k)
    
    def _assign_clusters(self, data):
        """
        Assign each point to the nearest centroid.
        
        Returns a list of cluster indices (0 to k-1) for each data point.
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
        Recalculate centroids as the mean of all points in each cluster.
        
        This is the core of k-means — centroids "move" toward the center
        of their assigned points.
        """
        new_centroids = []
        
        for cluster_idx in range(self.k):
            # Get all points assigned to this cluster
            cluster_points = [data[i] for i in range(len(data)) 
                            if labels[i] == cluster_idx]
            
            if cluster_points:
                # Calculate mean of each dimension
                dimensions = len(cluster_points[0])
                centroid = []
                for dim in range(dimensions):
                    mean_value = sum(point[dim] for point in cluster_points) / len(cluster_points)
                    centroid.append(mean_value)
                new_centroids.append(centroid)
            else:
                # If a cluster is empty, keep the old centroid
                # (in practice, this shouldn't happen often)
                new_centroids.append(self.centroids[cluster_idx])
        
        return new_centroids
    
    def _has_converged(self, old_centroids, new_centroids):
        """Check if centroids have stopped moving significantly."""
        for old, new in zip(old_centroids, new_centroids):
            if self._euclidean_distance(old, new) > self.tolerance:
                return False
        return True
    
    def fit(self, data):
        """
        Run the k-means algorithm on the data.
        
        Args:
            data: List of points, where each point is a list of coordinates
        
        Returns:
            self (for method chaining if desired)
        """
        # Start with random centroids
        self.centroids = self._initialize_centroids(data)
        
        for iteration in range(self.max_iterations):
            # Assign each point to nearest centroid
            self.labels = self._assign_clusters(data)
            
            # Update centroids based on assignments
            new_centroids = self._update_centroids(data, self.labels)
            
            # Check for convergence
            if self._has_converged(self.centroids, new_centroids):
                print(f"Converged after {iteration + 1} iterations")
                self.centroids = new_centroids
                break
            
            self.centroids = new_centroids
        else:
            print(f"Stopped after {self.max_iterations} iterations (max reached)")
        
        return self
    
    def predict(self, data):
        """Assign cluster labels to new data points using fitted centroids."""
        if self.centroids is None:
            raise ValueError("Model hasn't been fitted yet. Call fit() first.")
        return self._assign_clusters(data)


def generate_clustered_data(n_points=100, n_clusters=3, spread=1.0):
    """
    Generate random 2D data with natural clusters for testing.
    
    I made this to create data that k-means should be able to handle well.
    Each cluster has a random center and points are scattered around it.
    """
    data = []
    points_per_cluster = n_points // n_clusters
    
    for _ in range(n_clusters):
        # Random center for this cluster
        center_x = random.uniform(-10, 10)
        center_y = random.uniform(-10, 10)
        
        # Generate points around this center
        for _ in range(points_per_cluster):
            x = center_x + random.gauss(0, spread)
            y = center_y + random.gauss(0, spread)
            data.append([x, y])
    
    return data


if __name__ == "__main__":
    # Set seed for reproducibility in demo
    random.seed(42)
    
    print("K-Means Clustering Demo")
    print("=" * 50)
    
    # Generate some test data with 3 natural clusters
    print("\nGenerating 150 random 2D points in 3 clusters...")
    data = generate_clustered_data(n_points=150, n_clusters=3, spread=1.5)
    
    # Run k-means
    print(f"\nRunning k-means with k=3...")
    kmeans = KMeans(k=3, max_iterations=100, tolerance=1e-4)
    kmeans.fit(data)
    
    # Show final centroids
    print("\nFinal centroids:")
    for i, centroid in enumerate(kmeans.centroids):
        print(f"  Cluster {i}: ({centroid[0]:.2f}, {centroid[1]:.2f})")
    
    # Show cluster sizes
    print("\nCluster sizes:")
    for i in range(kmeans.k):
        count = kmeans.labels.count(i)
        print(f"  Cluster {i}: {count} points")
    
    # Test prediction on a new point
    test_point = [[0.0, 0.0]]
    predicted_cluster = kmeans.predict(test_point)[0]
    print(f"\nTest point {test_point[0]} assigned to cluster {predicted_cluster}")
    
    print("\n✓ Demo complete!")