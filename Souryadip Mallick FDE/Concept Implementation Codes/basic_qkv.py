import numpy as np

# Step 1: Input Embeddings Matrix X (Shape: 3 tokens x 4 embedding dims)
# Tokens: "it", "was", "tired"
X = np.array([
    [1.0, 0.0, 1.0, 0.0],  # "it"
    [0.0, 2.0, 0.0, 1.0],  # "was"
    [1.0, 1.0, 0.0, 2.0]   # "tired"
], dtype=float)

# Step 2: Learned Weight Matrices (Shape: 4 embedding dims x 3 head dims)
W_Q = np.array([
    [1, 0, 1],
    [0, 1, 0],
    [1, 0, 0],
    [0, 0, 1]
], dtype=float)

W_K = np.array([
    [0, 1, 0],
    [1, 0, 1],
    [0, 1, 0],
    [1, 0, 0]
], dtype=float)

W_V = np.array([
    [0, 0, 1],
    [0, 1, 0],
    [1, 0, 0],
    [0, 1, 1]
], dtype=float)

print("--- STEP 3: Projection ---")
# Compute Query, Key, and Value Matrices via Matrix Multiplication (@)
Q = X @ W_Q
K = X @ W_K
V = X @ W_V

print("Query Matrix (Q):\n", Q)
print("\nKey Matrix (K):\n", K)
print("\nValue Matrix (V):\n", V)

print("\n--- STEP 4: Attention Calculation ---")

# A. Calculate Raw Attention Scores (Q multiplied by K transpose)
raw_scores = Q @ K.T
print("Raw Scores (Q * K^T):\n", raw_scores)

# B. Scale by the square root of d_k (head dimension = 3)
d_k = K.shape[1]
scaled_scores = raw_scores / np.sqrt(d_k)
print("\nScaled Scores:\n", np.round(scaled_scores, 2))


# C. Stable Softmax over each row (probabilities sum to 1)
def softmax(matrix):
    # Subtracting row max protects against numerical overflow
    exp_matrix = np.exp(matrix - np.max(matrix, axis=1, keepdims=True))
    return exp_matrix / np.sum(exp_matrix, axis=1, keepdims=True)


attention_weights = softmax(scaled_scores)
print("\nAttention Weights (Softmax):\n", np.round(attention_weights, 2))

# D. Compute Final Contextual Output Vectors
output = attention_weights @ V
print("\nFinal Output Vectors (Context-Rich Embeddings):\n", np.round(output, 2))
