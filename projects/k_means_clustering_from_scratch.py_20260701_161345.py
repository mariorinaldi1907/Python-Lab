"""
Date: 2026-07-01
Built k-means clustering from scratch to really understand how the algorithm converges through iterative centroid updates.
"""

"""
K-Means Clustering Implementation from Scratch

I wanted to understand how k-means actually works under the hood, so I built this
without any ML libraries. The algorithm is simple but powerful: pick k random
centroids, assign points to nearest centroid, recalculate centroids, repeat.
"""

import random
import math


class KMeans:
    """
    K-Means clustering implementation using only Python standard library.
    
    The algorithm iteratively assigns data points to the nearest centroid,
    then recalculates centroids based on the mean of assigned points.
    """
    
    def __init__(self, k=3, max_iterations=100, random_seed=42):
        """
        Initialize the K-Means clusterer.
        
        Args:
            k: Number of clusters to form
            max_iterations: Maximum iterations before stopping (prevents infinite loops)
            random_seed: Seed for reproducibility when selecting initial centroids
        """
        self.k = k
        self.max_iterations = max_iterations
        self.random_seed = random_seed
        self.centroids = []
        self.clusters = []
    
    def _euclidean_distance(self, point1, point2):
        """
        Calculate Euclidean distance between two points.
        
        I'm using the standard sqrt of sum of squared differences here.
        Works for any dimensional space as long as both points have same dims.
        """
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(point1, point2)))
    
    def _initialize_centroids(self, data):
        """
        Randomly select k data points as initial centroids.
        
        There are fancier ways to do this (k-means++), but random selection
        works fine for most cases and is super simple to implement.
        """
        random.seed(self.random_seed)
        self.centroids = random.sample(data, self.k)
    
    def _assign_clusters(self, data):
        """
        Assign each data point to the nearest centroid.
        
        Returns a list of cluster assignments where each index corresponds
        to a data point and the value is the cluster (0 to k-1).
        """
        assignments = []
        for point in data:
            # Find the centroid with minimum distance to this point
            distances = [self._euclidean_distance(point, centroid) 
                        for centroid in self.centroids]
            closest_centroid = distances.index(min(distances))
            assignments.append(closest_centroid)
        return assignments
    
    def _update_centroids(self, data, assignments):
        """
        Recalculate centroids as the mean of all points in each cluster.
        
        This is the key step that makes k-means work — we're literally finding
        the center of mass for each cluster and moving the centroid there.
        """
        new_centroids = []
        for cluster_idx in range(self.k):
            # Get all points assigned to this cluster
            cluster_points = [data[i] for i, assignment in enumerate(assignments) 
                            if assignment == cluster_idx]
            
            if cluster_points:
                # Calculate mean across each dimension
                dimensions = len(cluster_points[0])
                centroid = []
                for dim in range(dimensions):
                    mean_value = sum(point[dim] for point in cluster_points) / len(cluster_points)
                    centroid.append(mean_value)
                new_centroids.append(centroid)
            else:
                # If a cluster is empty, keep the old centroid
                # (This can happen with unlucky initialization)
                new_centroids.append(self.centroids[cluster_idx])
        
        return new_centroids
    
    def fit(self, data):
        """
        Run the k-means algorithm on the provided data.
        
        Returns the final cluster assignments after convergence or max iterations.
        """
        self._initialize_centroids(data)
        
        for iteration in range(self.max_iterations):
            # Assign points to nearest centroid
            assignments = self._assign_clusters(data)
            
            # Calculate new centroids
            new_centroids = self._update_centroids(data, assignments)
            
            # Check for convergence (centroids didn't move)
            if new_centroids == self.centroids:
                print(f"Converged after {iteration + 1} iterations")
                break
            
            self.centroids = new_centroids
        else:
            print(f"Stopped after {self.max_iterations} iterations (max reached)")
        
        # Store final assignments
        self.clusters = assignments
        return assignments
    
    def predict(self, point):
        """
        Assign a new point to the nearest cluster.
        
        Useful after training to classify new data points.
        """
        distances = [self._euclidean_distance(point, centroid) 
                    for centroid in self.centroids]
        return distances.index(min(distances))


def generate_sample_data():
    """
    Generate some dummy 2D data with clear clusters for testing.
    
    I'm creating three distinct groups here so we can visually verify
    that k-means is finding the right clusters.
    """
    random.seed(42)
    data = []
    
    # Cluster 1: points around (2, 2)
    for _ in range(30):
        data.append([random.gauss(2, 0.5), random.gauss(2, 0.5)])
    
    # Cluster 2: points around (8, 8)
    for _ in range(30):
        data.append([random.gauss(8, 0.5), random.gauss(8, 0.5)])
    
    # Cluster 3: points around (2, 8)
    for _ in range(30):
        data.append([random.gauss(2, 0.5), random.gauss(8, 0.5)])
    
    return data


if __name__ == "__main__":
    print("K-Means Clustering Demo")
    print("=" * 50)
    
    # Generate synthetic data with 3 clear clusters
    data = generate_sample_data()
    print(f"\nGenerated {len(data)} data points in 2D space")
    
    # Run k-means with k=3
    kmeans = KMeans(k=3, max_iterations=100, random_seed=42)
    assignments = kmeans.fit(data)
    
    # Show the final centroids
    print("\nFinal Centroids:")
    for i, centroid in enumerate(kmeans.centroids):
        print(f"  Cluster {i}: ({centroid[0]:.2f}, {centroid[1]:.2f})")
    
    # Count points in each cluster
    print("\nCluster Sizes:")
    for i in range(kmeans.k):
        count = assignments.count(i)
        print(f"  Cluster {i}: {count} points")
    
    # Test prediction on a new point
    test_point = [2.5, 2.5]
    predicted_cluster = kmeans.predict(test_point)
    print(f"\nTest point {test_point} assigned to cluster {predicted_cluster}")
    
    print("\n✓ K-means clustering completed successfully!")