"""
Date: 2026-08-04
Implemented k-means clustering without any ML libraries to really understand how centroid updates and cluster assignments work under the hood.
"""

#!/usr/bin/env python3
"""
K-Means Clustering from Scratch
================================
A clean implementation of k-means using only Python's standard library.
I wanted to really understand how the algorithm converges by watching
centroids move around iteration by iteration.
"""

import random
import math


class KMeans:
    """
    K-Means clustering algorithm implementation.
    
    The algorithm alternates between:
    1. Assigning points to nearest centroid
    2. Updating centroids to mean of assigned points
    """
    
    def __init__(self, k=3, max_iterations=100, tolerance=1e-4):
        """
        Initialize K-Means clustering.
        
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
        
    def _euclidean_distance(self, point1, point2):
        """Calculate Euclidean distance between two points."""
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(point1, point2)))
    
    def _initialize_centroids(self, data):
        """
        Initialize centroids using random points from the dataset.
        
        K-means++ would be better here, but keeping it simple for now.
        Just picking k random points as starting centroids.
        """
        return random.sample(data, self.k)
    
    def _assign_clusters(self, data):
        """
        Assign each point to the nearest centroid.
        
        Returns:
            List of cluster indices (0 to k-1) for each data point
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
        
        This is where the "means" in k-means comes from.
        """
        new_centroids = []
        dimensions = len(data[0])
        
        for cluster_idx in range(self.k):
            # Get all points assigned to this cluster
            cluster_points = [data[i] for i in range(len(data)) 
                            if labels[i] == cluster_idx]
            
            if not cluster_points:
                # If a cluster has no points, keep the old centroid
                # This can happen with unlucky initialization
                new_centroids.append(self.centroids[cluster_idx])
            else:
                # Calculate mean across each dimension
                new_centroid = [
                    sum(point[dim] for point in cluster_points) / len(cluster_points)
                    for dim in range(dimensions)
                ]
                new_centroids.append(new_centroid)
        
        return new_centroids
    
    def _has_converged(self, old_centroids, new_centroids):
        """Check if centroids have stopped moving significantly."""
        total_movement = sum(
            self._euclidean_distance(old, new)
            for old, new in zip(old_centroids, new_centroids)
        )
        return total_movement < self.tolerance
    
    def fit(self, data):
        """
        Run the k-means algorithm on the data.
        
        Args:
            data: List of points, where each point is a list of coordinates
        """
        # Start with random centroids
        self.centroids = self._initialize_centroids(data)
        
        for iteration in range(self.max_iterations):
            # Assign each point to nearest centroid
            self.labels = self._assign_clusters(data)
            
            # Calculate new centroids
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
        """Assign new data points to nearest cluster."""
        return self._assign_clusters(data)


def generate_sample_data():
    """
    Generate some 2D sample data with obvious clusters.
    
    Creating three blobs of points that should naturally cluster.
    """
    random.seed(42)  # For reproducibility
    data = []
    
    # Cluster 1: around (2, 2)
    for _ in range(30):
        data.append([random.gauss(2, 0.5), random.gauss(2, 0.5)])
    
    # Cluster 2: around (8, 8)
    for _ in range(30):
        data.append([random.gauss(8, 0.5), random.gauss(8, 0.5)])
    
    # Cluster 3: around (2, 8)
    for _ in range(30):
        data.append([random.gauss(2, 0.5), random.gauss(8, 0.5)])
    
    return data


def visualize_clusters_ascii(data, labels, centroids):
    """
    Create a simple ASCII visualization of the clusters.
    
    Not pretty but helps see if the clustering makes sense.
    """
    print("\nCluster Visualization (ASCII):")
    print("=" * 50)
    
    # Create a grid
    grid_size = 20
    grid = [[' ' for _ in range(grid_size)] for _ in range(grid_size)]
    
    # Scale data to fit grid
    all_x = [p[0] for p in data]
    all_y = [p[1] for p in data]
    x_min, x_max = min(all_x), max(all_x)
    y_min, y_max = min(all_y), max(all_y)
    
    symbols = ['o', 'x', '+']
    
    # Plot points
    for point, label in zip(data, labels):
        x = int((point[0] - x_min) / (x_max - x_min) * (grid_size - 1))
        y = int((point[1] - y_min) / (y_max - y_min) * (grid_size - 1))
        grid[grid_size - 1 - y][x] = symbols[label]
    
    # Plot centroids with uppercase
    for i, centroid in enumerate(centroids):
        x = int((centroid[0] - x_min) / (x_max - x_min) * (grid_size - 1))
        y = int((centroid[1] - y_min) / (y_max - y_min) * (grid_size - 1))
        grid[grid_size - 1 - y][x] = str(i)
    
    for row in grid:
        print(''.join(row))
    print("=" * 50)


if __name__ == "__main__":
    print("K-Means Clustering Demo")
    print("Generating synthetic 2D data with 3 natural clusters...\n")
    
    # Generate data
    data = generate_sample_data()
    
    # Run k-means
    kmeans = KMeans(k=3, max_iterations=100, tolerance=1e-4)
    kmeans.fit(data)
    
    # Show results
    print(f"\nFinal centroids:")
    for i, centroid in enumerate(kmeans.centroids):
        print(f"  Cluster {i}: ({centroid[0]:.2f}, {centroid[1]:.2f})")
    
    # Count points per cluster
    cluster_counts = [kmeans.labels.count(i) for i in range(kmeans.k)]
    print(f"\nPoints per cluster: {cluster_counts}")
    
    # Visualize
    visualize_clusters_ascii(data, kmeans.labels, kmeans.centroids)
    
    # Test prediction on a new point
    new_point = [[2.5, 2.5]]
    prediction = kmeans.predict(new_point)
    print(f"\nPrediction for point {new_point[0]}: Cluster {prediction[0]}")