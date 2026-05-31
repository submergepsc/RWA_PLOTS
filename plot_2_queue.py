import os

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib.ticker import FixedLocator, LogLocator, NullFormatter
import numpy as np

# ================= 全局配置 =================
DATA_DIR = "."
FIGURES_ROOT = "figures"
PLOT_TYPE_NAME = "02_queue"

PROTOCOLS = { 
    "committee":   {"label": "FastOracle[15]", "color": "#DF3156", "z": 10, "lw": 4,   "marker": "o"}, 
    "deepthought": {"label": "Deep.[14]",      "color": "#4A0080", "z": 1,  "lw": 2.5, "marker": "v"}, 
    "seenfeed":    {"label": "Sen.[11]",       "color": "#E69F00", "z": 1,  "lw": 2.5, "marker": "D"}, 
    "decentruth":  {"label": "DECEN.[13]",     "color": "#009E73", "z": 1,  "lw": 2.5, "marker": "^"}, 
    "daon":        {"label": "DAON[12]",       "color": "#56B4E9", "z": 1,  "lw": 2.5, "marker": "s"}, 
}

L_SIZE, T_SIZE, LEG_SIZE = 28, 24, 14
DEFAULT_FIGSIZE = (8, 6)
FIGURE_MARGINS = dict(left=0.20, right=0.97, bottom=0.18, top=0.96)

def format_scientific(x, _):
    if abs(x) >= 1000:
        mantissa, exponent = f"{x:.1e}".split("e")
        return f"{float(mantissa):g}e{int(exponent)}"
    return f"{x:g}"

def get_marker_indices(y_values, num_markers=10):
    val_y = np.asarray(y_values)
    active_idx = np.where(val_y > 10)[0]
    if len(active_idx) == 0:
        max_idx = len(val_y) - 1
    else:
        max_idx = active_idx[-1]
    
    # Generate exactly `num_markers` evenly spaced indices up to the point it drains to 0
    indices = np.linspace(0, max_idx, num_markers, dtype=int)
    return indices.tolist()

# ================= 绘图核心逻辑 =================

def plot_queue_dynamics(network: str, out_dir: str):
    print(f"-> Drawing {network.upper()} Queue Dynamics (Cropped)...")
    
    plt.rcParams.update({
        'font.family': 'sans-serif', 'font.sans-serif': ['DejaVu Sans', 'Arial'],
        'axes.labelsize': L_SIZE, 'xtick.labelsize': T_SIZE, 'ytick.labelsize': T_SIZE,
        'legend.fontsize': LEG_SIZE, 'grid.linestyle': '--', 'grid.alpha': 0.45
    })

    csv_path = os.path.join(DATA_DIR, f"total_q_len_{network}.csv")
    if not os.path.exists(csv_path): return
    df = pd.read_csv(csv_path)
    df['time_min'] = df['time'] / 60.0

    fig, ax = plt.subplots(figsize=DEFAULT_FIGSIZE)

    # 1. 绘制所有曲线（包括 Deep.）
    max_time_others = 0
    for key, cfg in PROTOCOLS.items():
        if key in df.columns:
            x_plot, y_plot = df['time_min'], df[key]
            indices = get_marker_indices(df[key], num_markers=10)
            is_ours = (key == 'committee')

            ax.plot(
                x_plot.values,
                y_plot.values,
                color=cfg['color'],
                linewidth=3.0 if is_ours else 2.0,
                zorder=cfg['z'],
                marker=cfg['marker'],
                markersize=14,
                alpha=0.9,
                markevery=indices,
                markeredgewidth=1,
                markeredgecolor='white',
            )

            # Use a proxy line so legend markers remain visible despite markevery.
            ax.plot(
                [],
                [],
                label=cfg['label'],
                color=cfg['color'],
                linewidth=3.0 if is_ours else 2.0,
                marker=cfg['marker'],
                markersize=24 if is_ours else 18,
                alpha=0.9,
                markeredgewidth=1,
                markeredgecolor='white',
            )
            
            # Use the full active queue duration so slower schemes are not cut off.
            active_data = df[df[key] > 10]
            if not active_data.empty:
                max_time_others = max(max_time_others, active_data['time_min'].max())

    # 2. 核心裁剪逻辑
    min_crop_limit = 2000.0 if network == 'pos' else 120000.0
    crop_limit = max(max_time_others * 1.05, min_crop_limit)
    ax.set_xlim(1, crop_limit)

    max_y = 28000
    ax.set_ylim(top=max_y)

    print(f"   [Crop] {network.upper()} X-axis cropped at {crop_limit:.1f} min.")

    # 3. 装饰
    ax.set_xlabel("Runtime (min)")
    ax.set_ylabel("Queue length")
    ax.set_xscale("log")
    ax.xaxis.set_major_locator(FixedLocator([1, 10, 100, 1000, 10000]))
    ax.xaxis.set_minor_locator(LogLocator(base=10.0, subs=(2.0, 5.0)))
    ax.xaxis.set_major_formatter(FuncFormatter(format_scientific))
    ax.xaxis.set_minor_formatter(NullFormatter())
    ax.yaxis.set_major_formatter(FuncFormatter(format_scientific))
    ax.grid(True, which="both")

    handles, labels = ax.get_legend_handles_labels()
    legend_items = [
        ("FastOracle[15]", True),
        ("Deep.[14]", True),
        ("", False),
        ("DECEN.[13]", True),
        ("DAON[12]", True),
        ("Sen.[11]", True)
    ]
    ordered_handles = []
    ordered_labels = []
    for name, is_real in legend_items:
        if not is_real:
            ordered_handles.append(plt.Line2D([], [], color='none', alpha=0))
            ordered_labels.append("")
        else:
            idx = labels.index(name)
            h = handles[idx]
            h.set_markersize(10)
            ordered_handles.append(h)
            ordered_labels.append(labels[idx])

    leg = ax.legend(
        handles=ordered_handles,
        labels=ordered_labels,
        loc='upper right',
        bbox_to_anchor=(0.995, 0.995),
        ncol=2,
        fontsize=21,
        frameon=True,
        framealpha=0.45,
        columnspacing=1.2,
        handletextpad=0.6,
        borderaxespad=0.3,
        handlelength=2.0
    )
    leg.set_zorder(0)

    fig.subplots_adjust(**FIGURE_MARGINS)

    save_path = os.path.join(out_dir, f"queue_dynamics_{network}.pdf")
    fig.savefig(save_path, format="pdf")
    plt.close()

if __name__ == "__main__":
    target_dir = os.path.join(FIGURES_ROOT, PLOT_TYPE_NAME)
    os.makedirs(target_dir, exist_ok=True)
    for net in ['pos', 'pow']:
        plot_queue_dynamics(net, target_dir)