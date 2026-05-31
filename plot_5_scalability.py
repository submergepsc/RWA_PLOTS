import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from matplotlib.ticker import FuncFormatter, LogLocator, NullFormatter, MultipleLocator
from typing import Dict

# ================= 全局配置 =================
DATA_DIR = "." 
FIGURES_ROOT = "figures"
SUB_DIR_NAME = "05_scalability" 

SCENARIOS = {
    "pow": "total_handled_num_pow.csv",
    "pos": "total_handled_num_pos.csv"
}

PROTOCOLS: Dict[str, Dict[str, str]] = {
    "daon":       {"label": "DAON[12]",       "color": "#56B4E9", "marker": "s"},
    "decentruth": {"label": "DECEN.[13]",     "color": "#009E73", "marker": "^"},
    "committee":  {"label": "FastOracle[15]", "color": "#DF3156", "marker": "o"},
    "seenfeed":   {"label": "Sen.[11]",       "color": "#E69F00", "marker": "D"},
    "deepthought":{"label": "Deep.[14]",      "color": "#4A0080", "marker": "v"},
}

AXIS_LABEL_SIZE = 28
TICK_LABEL_SIZE = 24
LEGEND_FONT_SIZE = 32
DEFAULT_FIGSIZE = (12, 7)

def clean_sci_formatter(x, pos):
    if x == 0:
        return '0'
    exp = np.floor(np.log10(abs(x)))
    val = x / (10 ** exp)
    if val.is_integer():
        return f"{int(val)}e{int(exp)}"
    return f"{val:.1f}e{int(exp)}"

# ================= 绘图核心逻辑 =================
def plot_scalability_optimized(df: pd.DataFrame, scenario: str, out_dir: str, global_max_x: float):
    print(f"   -> Processing {scenario} with Log-Y optimization...")
    
    fig, ax = plt.subplots(figsize=DEFAULT_FIGSIZE)
    
    max_x_limit = 0
    max_y_limit = 0

    for method, config in PROTOCOLS.items():
        if method in df.columns:
            valid_data = df[method].dropna()
            if valid_data.empty: continue
            
            x_raw = valid_data.values
            y_raw = valid_data.index.values # 索引为时间

            max_val = x_raw.max()
            stop_idx = np.where(x_raw == max_val)[0][0] 
            x_data = x_raw[:stop_idx + 1]
            y_data = y_raw[:stop_idx + 1]

            interval = 2000
            x_sampled = np.arange(0, x_data.max() + interval, interval)
            y_sampled = np.interp(x_sampled, x_data, y_data)

            is_ours = (method == 'committee')
            is_deep = (method == 'deepthought')
            is_decentruth = (method == 'decentruth')

            if is_decentruth:
                zorder_val = 30  # decen 在图例上面
            elif is_deep:
                zorder_val = 25  # deep 在图例上面
            elif is_ours:
                zorder_val = 10
            else:
                zorder_val = 5

            ax.plot(x_sampled, y_sampled, 
                label=config['label'], 
                color=config['color'],
                marker=config['marker'],
                markersize=24 if is_ours else 18,
                linewidth=7 if is_ours else 4,
                alpha=0.9,
                zorder=zorder_val)
            
            max_x_limit = max(max_x_limit, x_data.max())
            max_y_limit = max(max_y_limit, y_data.max())

    ax.set_xlabel("Processed request number", fontsize=AXIS_LABEL_SIZE, labelpad=15)
    ax.set_ylabel("Cumulative process latency", fontsize=AXIS_LABEL_SIZE*0.8, labelpad=15)
    
    # ✅ X 轴干净科学计数法
    ax.xaxis.set_major_formatter(FuncFormatter(clean_sci_formatter))
    
    ax.xaxis.set_major_locator(MultipleLocator(5000))
    y_interval = 10000 if scenario == "pos" else 4000
    ax.yaxis.set_major_locator(MultipleLocator(y_interval))

    ax.tick_params(axis='both', which='major', labelsize=TICK_LABEL_SIZE, width=2, length=12)
    ax.tick_params(axis='both', which='minor', width=1, length=6)

    # ✅ Y 轴干净科学计数法
    ax.yaxis.set_major_formatter(FuncFormatter(clean_sci_formatter))

    ax.set_xlim(0, global_max_x * 1.05)
    if scenario == "pow":
        ax.set_ylim(0, max_y_limit * 0.016 * 1.15)
    else:
        ax.set_ylim(0, max_y_limit * 1.15)
    
    ax.grid(True, which="both", linestyle='--', linewidth=1.2, alpha=0.3)
    legend_loc = 'upper left'
    # loc 保持 upper left，配合 bbox_to_anchor 右移
    leg = ax.legend(loc='upper left', 
                bbox_to_anchor=(0.05, 0.95),  # 控制位置：x增大 → 右移；y微调上下
                fontsize=LEGEND_FONT_SIZE * 0.8, 
                frameon=True, framealpha=0.9, 
                ncol=2, handlelength=1.2, handleheight=0.6, 
                columnspacing=-0.8, handletextpad=0.5)
    leg.set_zorder(20)

    for spine in ['top', 'right']: ax.spines[spine].set_visible(False)
    for spine in ['left', 'bottom']: ax.spines[spine].set_linewidth(2)

    plt.tight_layout()
    save_path = os.path.join(out_dir, f"{scenario}_quantity_vs_time.pdf")
    plt.savefig(save_path, format="pdf", bbox_inches='tight')
    plt.close()

# ================= 主程序 =================
if __name__ == "__main__":
    target_dir = os.path.join(FIGURES_ROOT, SUB_DIR_NAME)
    os.makedirs(target_dir, exist_ok=True)
    
    global_max_x = 0
    for name, path in SCENARIOS.items():
        if os.path.exists(path):
            df = pd.read_csv(path, index_col=0)
            global_max_x = max(global_max_x, df.values.max())
    
    for name, path in SCENARIOS.items():
        if os.path.exists(path):
            df_in = pd.read_csv(path, index_col=0)
            plot_scalability_optimized(df_in, name, target_dir, global_max_x)