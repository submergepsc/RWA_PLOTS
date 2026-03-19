#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plot 5: RWA-FastOracle 证书生成时间 CDF (Certificate Generation CDF)
对应文件夹: figures/05_certificate/
说明: 
1. 读取 certif_gen_{network}.csv 文件。
2. 绘制 CDF 及其右侧延伸填充。
3. 【调整绘图顺序】先画表现较差的协议(背景)，最后画 Ours(前景)，防止阴影遮挡。
4. 【调整图例顺序】强制图例显示顺序为 Ours 在第一位。
"""

import os
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import pandas as pd
import numpy as np
from typing import Dict

# ================= 全局配置区域 =================

DATA_DIR = "." 
FIGURES_ROOT = "figures"
PLOT_TYPE_NAME = "04_certificate"

# 定义协议配置 (这是我们希望在 Legend 中显示的顺序: Ours 第一)
PROTOCOLS: Dict[str, Dict[str, str]] = {
    "committee": {"label": "FastOracle", "color": "#1f77b4"},
    "deepthought": {"label": "Deep.", "color": "#9467bd"},
    "seenfeed": {"label": "Seen.", "color": "#d62728"},
    "decentruth": {"label": "Decen.", "color": "#2ca02c"},
    "daon": {"label": "Daon.", "color": "#ff7f0e"},
}

# 样式配置
AXIS_LABEL_SIZE = 44
TICK_LABEL_SIZE = 40
LEGEND_FONT_SIZE = 38
DEFAULT_FIGSIZE = (12, 9)
SAVEFIG_KWARGS = {}
FIGURE_MARGINS = dict(left=0.14, right=0.97, bottom=0.16, top=0.95)

# ================= 辅助函数 =================

def load_data(network: str) -> pd.DataFrame:
    filename = f"certif_gen_{network}.csv"
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f"[Error] Data file not found: {path}")
    return pd.read_csv(path)

# ================= 绘图核心逻辑 =================

def plot_certificate_cdf(network: str, out_dir: str):
    print(f"-> Processing {network.upper()} certificate CDF (Optimized Order)...")
    
    plt.rcParams.update({
        'font.family': 'sans-serif', 
        'font.sans-serif': ['Arial', 'DejaVu Sans'],
        'axes.unicode_minus': False,
        'font.size': 14,
        'axes.labelsize': AXIS_LABEL_SIZE,
        'axes.titlesize': 18,
        'xtick.labelsize': TICK_LABEL_SIZE,
        'ytick.labelsize': TICK_LABEL_SIZE,
        'legend.fontsize': LEGEND_FONT_SIZE,
        'figure.figsize': DEFAULT_FIGSIZE,
        'grid.linestyle': '--', 
        'grid.alpha': 0.6
    })

    try:
        df = load_data(network)
    except FileNotFoundError as e:
        print(e)
        return

    fig, ax = plt.subplots(figsize=DEFAULT_FIGSIZE)
    
    # --- 1. 计算全局最大时间 (用于右边界) ---
    max_times = []
    for key in PROTOCOLS.keys():
        if key in df.columns:
            data_col = df[key].dropna()
            if not data_col.empty:
                max_times.append(data_col.max())
    
    if not max_times:
        print("   No valid data found.")
        return
    
    global_max_time = max(max_times) * 1.02
    
    # --- 2. 确定绘图顺序 (Drawing Order) ---
    # 我们希望最后画 'committee' (Ours)，这样它的线条和阴影在最上层
    # 因此我们将 PROTOCOLS 列表反转来进行绘图遍历
    draw_order = list(PROTOCOLS.items())  [::-1]

    for key, config in draw_order:
        if key in df.columns:
            data_col = df[key].dropna()
            if data_col.empty:
                continue
            
            sorted_data = np.sort(data_col)
            yvals = np.arange(1, len(sorted_data) + 1) / len(sorted_data)
            
            # 构造延伸数据点
            x_extended = np.concatenate(([0], sorted_data, [global_max_time]))
            y_extended = np.concatenate(([0], yvals, [1.0]))
            
            lw = 4.0 if key == 'committee' else 2.5
            alpha_line = 1.0 if key == 'committee' else 0.8
            # 虽然调整了绘图顺序，保留 zorder 也是双重保险
            zorder = 10 if key == 'committee' else 2
            
            # 绘制线条
            ax.plot(x_extended, y_extended, label=config['label'], color=config['color'], 
                    linewidth=lw, alpha=alpha_line, zorder=zorder)
            
            # 绘制填充 (由于 loop 是反向的，大面积的填充会先画，Ours 的小面积填充最后画)
            ax.fill_between(x_extended, y_extended, color=config['color'], alpha=0.1, zorder=1)

    # --- 3. 布局与图例重排序 (Legend Reordering) ---
    ax.set_xlabel("Generation Time (s)")
    ax.set_ylabel("CDF")
    ax.set_xlim(left=0, right=global_max_time)
    ax.set_ylim(bottom=0, top=1.02)
    ax.grid(True, linewidth=1.5)

    # 获取当前图上的所有 handles 和 labels (此时顺序是反的，因为我们反向遍历了)
    handles, labels = ax.get_legend_handles_labels()
    
    # 创建一个字典方便查找
    by_label = dict(zip(labels, handles))
    
    # 按照 PROTOCOLS 定义的原始顺序 (Ours 第一) 重新构建列表
    ordered_labels = [cfg['label'] for cfg in PROTOCOLS.values() if cfg['label'] in by_label]
    ordered_handles = [by_label[l] for l in ordered_labels]

    # 显示重排序后的图例
    ax.legend(ordered_handles, ordered_labels, loc='lower right')
    
    fig.subplots_adjust(**FIGURE_MARGINS)
    
    save_filename = f"certificate_cdf_{network}.pdf"
    save_path = os.path.join(out_dir, save_filename)
    fig.savefig(save_path, format="pdf", **SAVEFIG_KWARGS)
    print(f"   [OK] Saved: {save_path}")
    plt.close()

# ================= 运行入口 =================

if __name__ == "__main__":
    target_dir = os.path.join(FIGURES_ROOT, PLOT_TYPE_NAME)
    os.makedirs(target_dir, exist_ok=True)
    
    print(f"=== Starting Plotting Routine: {PLOT_TYPE_NAME} ===")
    print(f"Target Directory: {target_dir}")
    
    networks = ['pos', 'pow']
    for net in networks:
        plot_certificate_cdf(net, target_dir)
        
    print("=== Done ===")