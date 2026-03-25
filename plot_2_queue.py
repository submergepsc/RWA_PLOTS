import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import numpy as np

# ================= 全局配置 =================
DATA_DIR = "."
FIGURES_ROOT = "figures"
PLOT_TYPE_NAME = "02_queue"

PROTOCOLS = {
    "committee":   {"label": "FastOracle", "color": "#1f77b4", "z": 10, "lw": 4,   "marker": "o"},
    "deepthought": {"label": "Deep.",      "color": "#9467bd", "z": 1,  "lw": 2.5, "marker": "v"},
    "seenfeed":    {"label": "Seen.",      "color": "#d62728", "z": 1,  "lw": 2.5, "marker": "D"},
    "decentruth":  {"label": "Decen.",      "color": "#2ca02c", "z": 1,  "lw": 2.5, "marker": "^"},
    "daon":        {"label": "Daon.",      "color": "#ff7f0e", "z": 1,  "lw": 2.5, "marker": "s"},
}

L_SIZE, T_SIZE, LEG_SIZE = 44, 40, 32
DEFAULT_FIGSIZE = (12, 9)
FIGURE_MARGINS = dict(left=0.14, right=0.97, bottom=0.16, top=0.95)

def format_k(x, _):
    return f"{int(x/1000)}k" if x >= 1000 else f"{x:g}"

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
        'font.family': 'sans-serif', 'font.sans-serif': ['Arial'],
        'axes.labelsize': L_SIZE, 'xtick.labelsize': T_SIZE, 'ytick.labelsize': T_SIZE,
        'legend.fontsize': LEG_SIZE, 'grid.linestyle': '--', 'grid.alpha': 0.45
    })

    csv_path = os.path.join(DATA_DIR, f"total_q_len_{network}.csv")
    if not os.path.exists(csv_path): return
    df = pd.read_csv(csv_path)

    fig, ax = plt.subplots(figsize=DEFAULT_FIGSIZE)

    # 1. 绘制所有曲线（包括 Deep.）
    max_time_others = 0
    for key, cfg in PROTOCOLS.items():
        if key in df.columns:
            if network == 'pos':
                x_plot, y_plot = df['time'], df[key]
                indices = get_marker_indices(df[key], num_markers=10)
                is_ours = (key == 'committee')
                
                # 画真实线，不带 label（避免带 markevery 的实线在图例中丢失 markers）
                ax.plot(x_plot.values, y_plot.values, 
                        color=cfg['color'], linewidth=5 if is_ours else 3.5, zorder=cfg['z'],
                        marker=cfg['marker'], markersize=24 if is_ours else 18, alpha=0.9, markevery=indices, 
                        markeredgewidth=1, markeredgecolor='white')
                
                # 画专属图例的代理空线，带有 label 和 marker，但无 markevery（保证图例中标记正常显示）
                ax.plot([], [], label=cfg['label'], color=cfg['color'], linewidth=5 if is_ours else 3.5,
                        marker=cfg['marker'], markersize=20 if is_ours else 16, alpha=0.9,
                        markeredgewidth=1, markeredgecolor='white')
            else:
                x_plot, y_plot = df['time'], df[key]
                ax.plot(x_plot, y_plot, label=cfg['label'], color=cfg['color'], linewidth=cfg['lw'], zorder=cfg['z'])
            
            # 记录除 Deep 以外其他协议的最大结束时间，用于确定裁剪边界
            if key != 'deepthought':
                # 假设队列回到  0 或接近 0 的时间点
                active_data = df[df[key] > 10] # 过滤掉末尾的 0 值
                if not active_data.empty:
                    max_time_others = max(max_time_others, active_data['time'].max())

    # 2. 核心裁剪逻辑
    crop_limit = 20000 if network == 'pos' else 22000
    ax.set_xlim(0, crop_limit)
    print(f"   [Crop] {network.upper()} X-axis cropped at {crop_limit}s.")

    # 3. 装饰
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Queue Length")
    ax.xaxis.set_major_formatter(FuncFormatter(format_k))
    ax.grid(True)
    
    # 使用 plt.legend 重新设置图例位置到右上角
    plt.legend(loc='upper right', frameon=True, framealpha=0.95)
    fig.subplots_adjust(**FIGURE_MARGINS)

    save_path = os.path.join(out_dir, f"queue_dynamics_{network}.pdf")
    fig.savefig(save_path, format="pdf")
    plt.close()

if __name__ == "__main__":
    target_dir = os.path.join(FIGURES_ROOT, PLOT_TYPE_NAME)
    os.makedirs(target_dir, exist_ok=True)
    for net in ['pos', 'pow']:
        plot_queue_dynamics(net, target_dir)



"""

k_b - k_a &> \frac{1}{\lambda L} \ln \left( \frac{6}{1 - \exp(-\lambda L)} \right)\nonumber &=\frac{1}{\lambda L}(\ln6 \lambda L - \ln(\exp(\lambda L) - 1))\nonumber & = \ln 6 - \frac{\ln(\exp(\lambda L) - 1)}{\lambda L}



