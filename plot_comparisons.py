"""
Algorithm comparison scatter plots — replicating the paper style from:
"Bisection Value Iteration" (Lu & Xu, APSEC 2022)

Reads:  Output/compiled_results.csv  (produced by parse_results.py)
Writes: Output/plots/  — one PNG per algorithm pair, per metric (time / iterations)
        Plus one overview grid PNG per metric.
"""

import os
import itertools
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

matplotlib.rcParams.update({
    "font.family":      "serif",
    "font.serif":       ["Times New Roman", "DejaVu Serif"],
    "axes.titlesize":   10,
    "axes.labelsize":   9,
    "xtick.labelsize":  8,
    "ytick.labelsize":  8,
    "legend.fontsize":  8,
    "figure.dpi":       150,
    "axes.linewidth":   0.8,
    "grid.linewidth":   0.4,
    "lines.linewidth":  0.8,
})

# Algorithm display order 
ALGORITHMS = ["BVI-P", "BVI-GS", "BVI-NP", "BVI-AR", "II", "OVI"]

STYLE = {
    "MDP":  {"marker": "o", "color": "#d62728", "label": "MDP instance",  "s": 30, "zorder": 3},
    "DTMC": {"marker": "v", "color": "#1f77b4", "label": "DTMC instance", "s": 30, "zorder": 3},
}


def load_data(csv_path):
    df = pd.read_csv(csv_path)
    for col in ["Time (s)", "Total Iterations"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def pivot_metric(df, metric):
    key_cols = ["Model", "Type", "Parameter", "Property"]
    sub = df[key_cols + ["Algorithm", metric]].dropna(subset=[metric])
    pivoted = sub.pivot_table(
        index=key_cols,
        columns="Algorithm",
        values=metric,
        aggfunc="first",
    ).reset_index()
    pivoted.columns.name = None
    return pivoted


def padded_limits(vals, pad=0.05, force_zero_origin=True):
    clean = [v for v in vals if np.isfinite(v)]
    if not clean:
        return 0.0, 1.0
    vmin = float(np.min(clean))
    vmax = float(np.max(clean))
    rng  = vmax - vmin if vmax > vmin else max(vmax, 1e-9)
    lo   = vmin - rng * pad
    hi   = vmax + rng * pad
    if force_zero_origin and vmin >= 0:
        lo = max(0.0, lo)
    return lo, hi


def use_log_scale(vals):
    clean = [v for v in vals if np.isfinite(v) and v > 0]
    if len(clean) < 2:
        return False
    return max(clean) / min(clean) > 30


def draw_scatter(ax, pivoted, alg_x, alg_y, metric):
    if alg_x not in pivoted.columns or alg_y not in pivoted.columns:
        return False

    x_vals, y_vals = [], []
    has_data = False

    for mtype, st in STYLE.items():
        sub = pivoted[pivoted["Type"] == mtype][[alg_x, alg_y]].dropna()
        if sub.empty:
            continue
        has_data = True
        ax.scatter(
            sub[alg_x], sub[alg_y],
            marker=st["marker"], c=st["color"], s=st["s"],
            alpha=0.75, linewidths=0.3, edgecolors="white",
            label=st["label"], zorder=st["zorder"],
        )
        x_vals.extend(sub[alg_x].tolist())
        y_vals.extend(sub[alg_y].tolist())

    if not has_data:
        return False

    all_vals = [v for v in x_vals + y_vals if np.isfinite(v)]
    use_log  = use_log_scale(all_vals)

    if use_log:
        ax.set_xscale("log")
        ax.set_yscale("log")
        pos = [v for v in all_vals if v > 0]
        lo  = min(pos) * 0.5
        hi  = max(pos) * 1.5
        diag = np.logspace(np.log10(lo), np.log10(hi), 300)
    else:
        lo, hi = padded_limits(all_vals)
        diag = np.linspace(lo, hi, 300)

    ax.set_xlim(lo, hi)
    ax.set_ylim(lo, hi)

    ax.plot(diag, diag, color="black", linewidth=0.9,
            linestyle="--", zorder=2, alpha=0.55)

    unit  = "(s)" if "Time" in metric else ""
    label = "time" if "Time" in metric else "iterations"
    ax.set_xlabel(f"{alg_x} {label} {unit}".strip())
    ax.set_ylabel(f"{alg_y} {label} {unit}".strip())
    ax.grid(True, which="both", linestyle=":", alpha=0.35)
    ax.tick_params(direction="in", length=3)

    handles, labels_l = ax.get_legend_handles_labels()
    seen = dict(zip(labels_l, handles))
    if seen:
        ax.legend(seen.values(), seen.keys(),
                  loc="upper left", framealpha=0.7,
                  edgecolor="grey", handletextpad=0.4)
    return True


def save_individual_plots(pivoted, metric, out_dir, algs):
    tag = "time" if "Time" in metric else "iterations"
    for alg_x, alg_y in itertools.combinations(algs, 2):
        fig, ax = plt.subplots(figsize=(4.2, 4.2))
        ok = draw_scatter(ax, pivoted, alg_x, alg_y, metric)
        if not ok:
            plt.close(fig)
            continue
        fig.tight_layout()
        fname = f"{alg_x}_vs_{alg_y}_{tag}.png"
        fig.savefig(os.path.join(out_dir, fname), bbox_inches="tight")
        plt.close(fig)
        print(f"  Saved {fname}")


def save_overview_grid(pivoted, metric, out_dir, algs):
    pairs = list(itertools.combinations(algs, 2))
    if not pairs:
        return

    tag   = "time" if "Time" in metric else "iterations"
    ncols = min(3, len(pairs))
    nrows = (len(pairs) + ncols - 1) // ncols

    fig, axes = plt.subplots(nrows, ncols,
                             figsize=(4.2 * ncols, 4.2 * nrows),
                             squeeze=False)
    axes_flat = axes.flatten()

    for idx, (alg_x, alg_y) in enumerate(pairs):
        draw_scatter(axes_flat[idx], pivoted, alg_x, alg_y, metric)

    for idx in range(len(pairs), len(axes_flat)):
        axes_flat[idx].set_visible(False)

    unit_str = "(s)" if "Time" in metric else "(iterations)"
    fig.suptitle(
        f"Algorithm comparison — {tag} {unit_str}",
        fontsize=12, fontweight="bold", y=1.01,
    )
    fig.tight_layout()
    fname = f"overview_{tag}.png"
    fig.savefig(os.path.join(out_dir, fname), bbox_inches="tight", dpi=150)
    plt.close(fig)
    print(f"  Saved overview grid: {fname}")


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path   = os.path.join(script_dir, "Output", "NEWcompiled_results.csv")
    plots_dir  = os.path.join(script_dir, "Output", "Finalplots")
    os.makedirs(plots_dir, exist_ok=True)

    if not os.path.exists(csv_path):
        print(f"ERROR: {csv_path} not found.\nRun parse_results.py first.")
        return

    print(f"Loading {csv_path} …")
    df = load_data(csv_path)
    print(f"  {len(df)} rows loaded.")

    algs = [a for a in ALGORITHMS if a in df["Algorithm"].unique()]
    print(f"  Algorithms present: {algs}")
    if len(algs) < 2:
        print("Need at least 2 algorithms to compare.")
        return

    for metric in ["Time (s)", "Total Iterations"]:
        print(f"\n── Metric: {metric} ──")
        pivoted = pivot_metric(df, metric)
        if pivoted.empty:
            print("  No data, skipping.")
            continue
        save_individual_plots(pivoted, metric, plots_dir, algs)
        save_overview_grid(pivoted, metric, plots_dir, algs)

    print(f"\nAll plots saved to: {plots_dir}")


if __name__ == "__main__":
    main()