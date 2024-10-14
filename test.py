from collections import defaultdict

# List of tuples
tuple_list = [(3, 4), (1, 2), (5, 6), (2, 8), (3, 9), (1, 7)]

# Dictionary to group pairs by the first int
grouped_pairs = defaultdict(list)

# Iterate over the list and group by the first element of each tuple
for pair in tuple_list:
    grouped_pairs[pair[0]].append(pair)

# Convert defaultdict back to a regular dict (optional)
grouped_pairs = dict(grouped_pairs)

# Print the grouped pairs
for key, value in grouped_pairs.items():
    print(f"{key}: {value}")
