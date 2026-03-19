#!/usr/bin/env python3
# -*- coding: utf-8 -*- 



import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from matplotlib.ticker import FuncFormatter, LogLocator, NullFormatter
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
    "committee":  {"label": "FastOracle", "color": "#1f77b4", "marker": "o"},
    "daon":       {"label": "Daon.",      "color": "#ff7f0e", "marker": "s"},
    "decentruth": {"label": "Decen.",      "color": "#2ca02c", "marker": "^"},
    "seenfeed":   {"label": "Seen.",      "color": "#d62728", "marker": "D"},
    "deepthought":{"label": "Deep.",      "color": "#9467bd", "marker": "v"},
}

AXIS_LABEL_SIZE = 44
TICK_LABEL_SIZE = 38
LEGEND_FONT_SIZE = 35
DEFAULT_FIGSIZE = (12, 9)

# 格式化函数
def k_formatter(x, pos):
    return f'{x/1000:.0f}k' if x >= 1000 else f'{int(x)}'

# ================= 绘图核心逻辑 =================

def plot_scalability_optimized(df: pd.DataFrame, scenario: str, out_dir: str, global_max_x: float):
    print(f"   -> Processing {scenario} with Log-Y optimization...")
    
    fig, ax = plt.subplots(figsize=DEFAULT_FIGSIZE)
    
    # 【修改 1】移除对数坐标，使用线性坐标
    
    max_x_limit = 0
    max_y_limit = 0

    for method, config in PROTOCOLS.items():
        if method in df.columns:
            valid_data = df[method].dropna()
            if valid_data.empty: continue
            
            x_raw = valid_data.values
            y_raw = valid_data.index.values # 索引为时间

            # 【修改 2】解决垂直线：截断处理完成后多余的计时
            max_val = x_raw.max()
            stop_idx = np.where(x_raw == max_val)[0][0] 
            x_data = x_raw[:stop_idx + 1]
            y_data = y_raw[:stop_idx + 1]

            # 【修改 3】按照 x 轴距离均匀采样，绘制更稠密点
            interval = 2000  # 每 20 个单位一个点，更稠密
            x_sampled = np.arange(0, x_data.max() + interval, interval)
            y_sampled = np.interp(x_sampled, x_data, y_data)

            is_ours = (method == 'committee')
            ax.plot(x_sampled, y_sampled, 
                    label=config['label'], 
                    color=config['color'],
                    marker=config['marker'],
                    markersize=24 if is_ours else 18,
                    linewidth=7 if is_ours else 4,
                    alpha=0.9,
                    zorder=10 if is_ours else 5)
            
            max_x_limit = max(max_x_limit, x_data.max())
            max_y_limit = max(max_y_limit, y_data.max())

    # --- 坐标轴格式化 ---
    ax.set_xlabel("Processed Request Number", fontsize=AXIS_LABEL_SIZE, labelpad=15)
    ax.set_ylabel("Processing Time (s)", fontsize=AXIS_LABEL_SIZE, labelpad=15)
    
    # X轴设为 k 单位
    ax.xaxis.set_major_formatter(FuncFormatter(k_formatter))
    
    # 【修改 4】Y轴刻度优化，使用线性刻度
    ax.yaxis.set_major_locator(plt.MaxNLocator(6))
    ax.yaxis.set_minor_locator(plt.MaxNLocator(12))

    ax.tick_params(axis='both', which='major', labelsize=TICK_LABEL_SIZE, width=2, length=12)
    ax.tick_params(axis='both', which='minor', width=1, length=6)

    # 范围调整
    ax.set_xlim(0, global_max_x * 1.05)
    if scenario == "pow":
        ax.set_ylim(0, max_y_limit * 0.016)
    
    ax.grid(True, which="both", linestyle='--', linewidth=1.2, alpha=0.3)
    legend_loc = 'upper left' if scenario == 'pow' else 'upper left'
    ax.legend(loc=legend_loc, fontsize=LEGEND_FONT_SIZE, frameon=True, framealpha=0.9)

    # 美化边框
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
    
    # 计算全局最大 x 值
    global_max_x = 0
    for name, path in SCENARIOS.items():
        if os.path.exists(path):
            df = pd.read_csv(path, index_col=0)
            global_max_x = max(global_max_x, df.values.max())
    
    for name, path in SCENARIOS.items():
        if os.path.exists(path):
            df_in = pd.read_csv(path, index_col=0)
            plot_scalability_optimized(df_in, name, target_dir, global_max_x)

    print(f"\n[Done] Y轴已优化。PoW采用对数刻度显示对比，PoS保持线性显示。")


