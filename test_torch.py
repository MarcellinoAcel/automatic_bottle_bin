import numpy as np
import torch

# Create a numpy array
arr = np.array([1, 2, 3])

# Convert to torch tensor
tensor = torch.from_numpy(arr)

print("NumPy array:", arr)
print("PyTorch tensor:", tensor)