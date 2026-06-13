"""
Date: 2026-06-13
Built k-means clustering using only the standard library to really understand how the algorithm converges and assigns clusters.
"""

#!/usr/bin/env python3
"""
K-Means Clustering Implementation from Scratch
No external dependencies - just Python stdlib and math
"""

import random
import math
from collections import defaultdict


class KMeans:
    """
    K-Means clustering implementation using Lloyd's algorithm.
    Assigns data points to k clusters by minimizing within-cluster variance.
    """
    
    def __init__(self, k=3, max_iterations=100, random_seed=42):
        """
        Initialize K-Means clusterer.
        
        Args:
            k: Number of clusters
            max_iterations: Max iterations before stopping (prevents infinite loops)
            random_seed: Seed for reproducible centroid initialization
        """
        self.k = k
        self.max_iterations = max_iterations
        self.random_seed = random_seed
        self.centroids = []
        self.labels = []
        
    def _euclidean_distance(self, point1, point2):
        """Calculate Euclidean distance between two points."""
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(point1, point2)))
    
    def _initialize_centroids(self, data):
        """
        Randomly select k data points as initial centroids.
        Using random.sample ensures we don't pick duplicates.
        """
        random.seed(self.random_seed)
        self.centroids = random.sample(data, self.k)
    
    def _assign_clusters(self, data):
        """
        Assign each point to the nearest centroid.
        Returns a list of cluster labels (0 to k-1) for each data point.
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
        This is where the "means" in k-means comes from.
        """
        new_centroids = []
        for cluster_id in range(self.k):
            # Get all points belonging to this cluster
            cluster_points = [data[i] for i in range(len(data)) 
                            if labels[i] == cluster_id]
            
            if cluster_points:
                # Calculate mean across each dimension
                dimensions = len(cluster_points[0])
                centroid = [sum(point[d] for point in cluster_points) / len(cluster_points)
                           for d in range(dimensions)]
                new_centroids.append(centroid)
            else:
                # Edge case: empty cluster, keep the old centroid
                new_centroids.append(self.centroids[cluster_id])
        
        return new_centroids
    
    def _centroids_converged(self, old_centroids, new_centroids, tolerance=1e-4):
        """Check if centroids have stopped moving (algorithm has converged)."""
        for old, new in zip(old_centroids, new_centroids):
            if self._euclidean_distance(old, new) > tolerance:
                return False
        return True
    
    def fit(self, data):
        """
        Run the k-means algorithm on the data.
        Iteratively assigns points and updates centroids until convergence.
        
        Args:
            data: List of data points (each point is a list/tuple of coordinates)
        """
        self._initialize_centroids(data)
        
        for iteration in range(self.max_iterations):
            # Assignment step: assign each point to nearest centroid
            self.labels = self._assign_clusters(data)
            
            # Update step: recalculate centroids
            old_centroids = self.centroids.copy()
            self.centroids = self._update_centroids(data, self.labels)
            
            # Check for convergence
            if self._centroids_converged(old_centroids, self.centroids):
                print(f"Converged after {iteration + 1} iterations")
                break
        else:
            print(f"Reached max iterations ({self.max_iterations})")
    
    def calculate_inertia(self, data):
        """
        Calculate within-cluster sum of squares (inertia).
        Lower is better - measures how tight the clusters are.
        Used for the elbow method to find optimal k.
        """
        inertia = 0
        for i, point in enumerate(data):
            centroid = self.centroids[self.labels[i]]
            inertia += self._euclidean_distance(point, centroid) ** 2
        return inertia


def generate_sample_data(n_samples=150, n_features=2, n_clusters=3):
    """
    Generate synthetic clustered data for testing.
    Creates blob-like clusters with some randomness.
    """
    random.seed(42)
    data = []
    
    # Create n_clusters distinct blobs
    for cluster in range(n_clusters):
        # Random center for this cluster
        center = [random.uniform(0, 100) for _ in range(n_features)]
        
        # Generate points around this center
        for _ in range(n_samples // n_clusters):
            point = [center[i] + random.gauss(0, 5) for i in range(n_features)]
            data.append(point)
    
    random.shuffle(data)
    return data


def print_ascii_elbow_plot(inertias, k_values):
    """
    Print a simple ASCII visualization of the elbow curve.
    Helps identify the optimal number of clusters visually.
    """
    print("\nElbow Plot (Inertia vs K):")
    print("=" * 50)
    
    # Normalize inertias to fit in terminal width
    max_inertia = max(inertias)
    scale = 40 / max_inertia
    
    for k, inertia in zip(k_values, inertias):
        bar_length = int(inertia * scale)
        bar = '█' * bar_length
        print(f"k={k}: {bar} ({inertia:.2f})")
    
    print("=" * 50)


if __name__ == "__main__":
    print("K-Means Clustering Demo")
    print("-" * 50)
    
    # Generate synthetic data
    data = generate_sample_data(n_samples=150, n_features=2, n_clusters=3)
    print(f"Generated {len(data)} data points with {len(data[0])} features\n")
    
    # Fit k-means with k=3
    print("Fitting K-Means with k=3...")
    kmeans = KMeans(k=3, max_iterations=100)
    kmeans.fit(data)
    
    print("\nFinal centroids:")
    for i, centroid in enumerate(kmeans.centroids):
        print(f"  Cluster {i}: {[f'{c:.2f}' for c in centroid]}")
    
    # Count points per cluster
    cluster_counts = defaultdict(int)
    for label in kmeans.labels:
        cluster_counts[label] += 1
    
    print("\nCluster sizes:")
    for cluster_id in sorted(cluster_counts.keys()):
        print(f"  Cluster {cluster_id}: {cluster_counts[cluster_id]} points")
    
    # Elbow method to find optimal k
    print("\n" + "=" * 50)
    print("Running Elbow Method (k=1 to k=8)...")
    print("=" * 50)
    
    k_values = range(1, 9)
    inertias = []
    
    for k in k_values:
        km = KMeans(k=k, max_iterations=100)
        km.fit(data)
        inertia = km.calculate_inertia(data)
        inertias.append(inertia)
    
    print_ascii_elbow_plot(inertias, k_values)
    print("\nLook for the 'elbow' - where inertia stops decreasing rapidly!")