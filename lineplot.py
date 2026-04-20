import pandas as pd
import matplotlib.pyplot as plt
import os

csv_file = "NEWcompiled_results.csv"

df = pd.read_csv(csv_file)

# -----------------------------
# Remove runs with 0 seconds
# -----------------------------
df = df[df["Time (s)"] > 0]

algorithms = [
    "BVI-P",
    "BVI-NP",
    "BVI-GS",
    "BVI-AR",
    "II",
    "OVI"
]

df = df[df["Algorithm"].isin(algorithms)]

# -----------------------------
# Create instance identifier
# -----------------------------
df["Instance"] = df["Model"] + "_" + df["Property"].astype(str)

# -----------------------------
# Remove instances where ANY algorithm > 600s
# -----------------------------
max_times = df.groupby("Instance")["Time (s)"].max()
valid_instances = max_times[max_times <= 600].index
df = df[df["Instance"].isin(valid_instances)]

# -----------------------------
# Pivot table
# -----------------------------
pivot = df.pivot_table(
    index="Instance",
    columns="Algorithm",
    values="Time (s)",
    aggfunc="mean"
)

# -----------------------------
# Ensure all algorithms share same instances
# -----------------------------
pivot = pivot.dropna()

# -----------------------------
# Colors and markers
# -----------------------------
colors = {
    "BVI-P": "#66c2a5",
    "BVI-NP": "#fc8d62",
    "BVI-GS": "#8da0cb",
    "BVI-AR": "#e78ac3",
    "II": "#a6d854",
    "OVI": "#ffd92f"
}

markers = {
    "BVI-P": "o",
    "BVI-NP": "s",
    "BVI-GS": "D",
    "BVI-AR": "^",
    "II": "v",
    "OVI": "x"
}

# -----------------------------
# Plot only ranks 50–80
# -----------------------------
plt.figure(figsize=(10, 6))

# Convert rank range to indices
start = 49   # rank 50
end = 80     # exclusive (up to rank 80)

n = len(pivot)
start = max(0, min(start, n))
end = max(start, min(end, n))

for algo in algorithms:
    if algo in pivot.columns:
        values = pivot[algo].values

        # Sort independently
        values_sorted = sorted(values)

        # Slice the desired rank window
        subset = values_sorted[start:end]

        x = range(len(subset))

        plt.plot(
            x,
            subset,
            label=algo,
            linewidth=2.2,
            color=colors.get(algo),
            marker=markers.get(algo),
            markersize=4,
            markevery=max(len(subset)//10, 1)
        )

# -----------------------------
# Labels and styling
# -----------------------------
plt.xlabel("Instance Rank (50–80, per algorithm)")
plt.ylabel("Time (s)")
plt.title("Runtime Distribution (Ranks 50–80, <600s instances)")

plt.legend()
plt.grid(alpha=0.3)

plt.tight_layout()

# -----------------------------
# Save PNG
# -----------------------------
output_path = os.path.join(os.path.dirname(csv_file), "model_checking_times_50_80.png")
plt.savefig(output_path, dpi=300)

plt.show()

print("Saved figure to:", output_path)