import numpy as np
from sklearn.metrics import silhouette_score


class FeatureClusterLimit:

    def __init__(self, X, limit_value):
        self.X = X
        self.limit_value = limit_value

    def check(self, labels):
        for i in np.unique(labels):
            cluster = self.X[labels == i]
            if np.sum(cluster) > self.limit_value:
                return False
        return True


class ClusterLimits:

    def __init__(self, limits, size_limit=None):
        self.limits = limits
        self.size_limit = size_limit

    def check_limits(self, labels):
        for limit in self.limits:
            if limit.check(labels) is False:
                return False
        return True

    def check_size_limit(self, X, labels):
        if self.size_limit is not None:
            for i in np.unique(labels):
                cluster = X[labels == i]
                if cluster.shape[0] > self.size_limit:
                    return False
        return True


class ClusteringModel:

    def __init__(self, n_clusters, n_epochs=300, tol=0.0001):
        self.n_clusters = n_clusters
        self.n_epochs = n_epochs
        self.tol = tol

    def distance_matrix(self, X_1, X_2):
        return np.linalg.norm(X_1[:, np.newaxis] - X_2, axis=2) ** 2

    def sse(self, X, centroids, labels):
        distances = np.linalg.norm(X - centroids[labels], axis=1) ** 2
        return np.sum(distances)

    def init_centroids(self, X):
        n_samples = X.shape[0]
        centroids = []
        indexes = np.arange(n_samples)
        mask = np.ones(n_samples, dtype=bool)

        first_index = np.random.choice(indexes)
        centroids.append(X[first_index])
        mask[first_index] = False

        for _ in range(1, self.n_clusters):
            masked_X = X[mask]
            distances = np.min(self.distance_matrix(masked_X, centroids), axis=1)
            probabilities = distances / np.sum(distances)

            new_index = np.random.choice(indexes[mask], p=probabilities)
            centroids.append(X[new_index])
            mask[new_index] = False

        return np.array(centroids)

    def update_centroids(self, X, labels):
        return np.array([np.mean(X[labels == i], axis=0) for i in range(self.n_clusters)])

    def fit_predict(self, X):
        centroids = self.init_centroids(X)
        labels = None
        inertia = 0
        is_tol = False

        for _ in range(self.n_epochs):
            labels = np.argmin(self.distance_matrix(X, centroids), axis=1)
            cur_inertia = self.sse(X, centroids, labels)
            if np.abs(cur_inertia - inertia) < self.tol:
                is_tol = True
                break
            inertia = cur_inertia
            centroids = self.update_centroids(X, labels)

        if is_tol:
            return labels

        return np.argmin(self.distance_matrix(X, centroids), axis=1)


class BestClusteringModel(ClusteringModel):

    def __init__(self, n_clusters, n_epochs=300, tol=0.0001, n_init=30):
        super().__init__(n_clusters, n_epochs, tol)
        self.n_init = n_init

    def best_fit_predict(self, X, limits=None):
        best_labels = None
        best_score = -1

        if limits is not None:
            for _ in range(self.n_init):
                labels = self.fit_predict(X)
                score = silhouette_score(X, labels)
                if limits.check_limits(labels) and limits.check_size_limit(X, labels):
                    if score > best_score:
                        best_labels = labels
                        best_score = score
        else:
            for _ in range(self.n_init):
                labels = self.fit_predict(X)
                score = silhouette_score(X, labels)
                if score > best_score:
                    best_labels = labels
                    best_score = score

        return best_labels
