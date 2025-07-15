import numpy as np
from typing import List


def max_profit_route(
    reward: np.ndarray, cost: np.ndarray, start: int, end: int, K: int = None
) -> list:
    """
    Finds the most profitable route from a start node to an end node, maximizing the sum of rewards minus the sum of costs.

    The path can be of any length unless an exact number of edges (K) is specified. In that case, only paths with exactly K edges
    (i.e., K + 1 nodes) are considered.

    :param reward: 1D numpy array of rewards for each node. reward[i] is the reward for visiting node i.
    :param cost: 2D numpy array (NxN) where cost[i][j] is the cost to travel from node i to node j. Use np.inf for unreachable nodes.
    :param start: Index of the start node.
    :param end: Index of the end node.
    :param K: Optional integer representing the exact number of edges (hops) allowed in the path. If None, all lengths are allowed.
    :return: A list of node indices representing the most profitable path from start to end. Returns an empty list if no valid path exists.
    """
    N = len(reward)
    max_K = (
        K if K is not None else N - 1
    )  # If K is not given, search up to N-1 steps (no cycles assumed)

    # dp[v][k] stores the max profit to reach node v in k steps (i.e., k edges)
    dp = -np.inf * np.ones((N, max_K + 1))
    prev = -np.ones((N, max_K + 1), dtype=int)  # To track the path

    dp[start][0] = reward[
        start
    ]  # Starting condition: 0 steps, just the reward of start node

    # Fill the DP table
    for k in range(1, max_K + 1):  # For each step count
        for u in range(N):  # From each node u
            if dp[u][k - 1] == -np.inf:
                continue  # Skip unreachable states
            for v in range(N):  # Try going to each node v
                if np.isinf(cost[u][v]):
                    continue  # Skip if no edge from u to v
                profit = (
                    dp[u][k - 1] + reward[v] - cost[u][v]
                )  # Profit from previous state + reward - cost
                if profit > dp[v][k]:
                    dp[v][k] = profit
                    prev[v][k] = u  # Track the best previous node

    # Select the best path to end node
    if K is not None:
        best_k = K
        best_profit = dp[end][K]
    else:
        best_k = int(np.argmax(dp[end]))
        best_profit = dp[end][best_k]

    if best_profit == -np.inf:
        return []  # No path found

    # Backtrack to reconstruct the path
    path = []
    node = end
    k = best_k
    while node != -1 and k >= 0:
        path.append(node)
        node = prev[node][k]
        k -= 1

    return path[::-1]  # Return path in forward direction


def mcl(
    matrix: np.ndarray,
    expansion: int = 2,
    inflation: float = 2.0,
    threshold: float = 1e-6,
    tol=1e-6,
    max_iter: int = 1000,
) -> List[List[int]]:
    """
    Cluster a transitory matrix using the Markov chain.
    The clusters are formed by the nodes that are connected to each other.

    :param matrix: The transitory matrix.
    :param expansion: The expansion factor for the clusters.
    :param inflation: The inflation factor for the clusters.
    :param threshold: The threshold for the clusters.
    :param tol: The tolerance for convergence.
    :param max_iter: The maximum number of iterations.
    :return: A list of clusters, each cluster is a list of node indices.
    """
    n = matrix.shape[0]
    M = matrix.copy()

    for _ in range(max_iter):
        M_old = M.copy()

        # Step 3: Expansion
        M = np.linalg.matrix_power(M, expansion)

        # Step 4: Inflation
        M = np.power(M, inflation)

        # Step 5: Prune small values
        M[M < threshold] = 0

        # Step 6: Re-normalize
        column_sums = M.sum(axis=0, keepdims=True)
        column_sums[column_sums == 0] = 1  # Avoid division by zero
        M = M / column_sums

        # Step 7: Check convergence
        if np.allclose(M, M_old, atol=tol):
            break

    # Step 8: Interpret the final matrix
    clusters = []
    seen = set()

    for i in range(n):
        if i in seen:
            continue
        cluster = set(np.where(M[i] > 0)[0])
        if cluster:
            clusters.append(sorted(list(cluster)))
            seen.update(cluster)

    return clusters


def mcc(adj_matrix: np.ndarray) -> np.ndarray:
    """
    Approximates edge betweenness centrality using a Markov chain approach.
    The edge betweenness is approximated based on the stationary distribution of the Markov chain.

    :param adj_matrix: NxN adjacency matrix of the graph.
    :return: NxN matrix of edge betweenness centrality scores.
    """
    n = len(adj_matrix)

    # Step 1: Construct the transition matrix (Markov chain)
    row_sums = adj_matrix.sum(axis=1)
    transition_matrix = np.divide(adj_matrix.T, row_sums, where=row_sums != 0).T

    # Step 2: Compute the stationary distribution (Eigenvector of the transition matrix)
    # Use the fact that stationary distribution π satisfies π * P = π, or (P - I) * π = 0.
    # We solve for the eigenvector corresponding to eigenvalue 1.
    eigvals, eigvecs = np.linalg.eig(transition_matrix.T)
    stationary_dist = np.real(eigvecs[:, np.isclose(eigvals, 1)].flatten())

    # Normalize the stationary distribution
    stationary_dist /= stationary_dist.sum()

    # Step 3: Approximate edge betweenness using stationary distribution
    edge_centrality = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            if adj_matrix[i, j] != 0:
                # Approximate flow between i and j using the stationary distribution
                flow = stationary_dist[i] * stationary_dist[j]
                edge_centrality[i, j] += flow
                edge_centrality[j, i] += flow  # For undirected graphs, mirror the flow

    return edge_centrality


def markov_chain(
    transition_matrix: np.ndarray,
    v: np.ndarray = None,
    max_iter: int = 100,
    tol: float = 1e-6,
) -> np.ndarray:
    """
    Computes the steady state distribution of a Markov chain using power iteration.
    :param transition_matrix: The transition matrix of the Markov chain. Rows should sum to 1.
    :param v: Initial distribution. If None, uniform distribution is used.
    :param max_iter: Maximum number of iterations.
    :param tol: Tolerance for convergence.
    :return: Steady state distribution.
    """
    num_nodes = transition_matrix.shape[0]
    if v is None:
        v = np.ones(num_nodes) / num_nodes
    else:
        v = v
    for _ in range(max_iter):
        v_next = np.dot(transition_matrix.T, v)
        if np.linalg.norm(v - v_next) < tol:
            break
        v = v_next
    return v
