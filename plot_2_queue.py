#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plot 3: RWA-FastOracle 队列消减动力学 (Queue Log-Dynamics)
对应文件夹: figures/03_queue/
说明: 
1. PoW 网络: 使用 Log(t - bios) 时间轴，有效压缩漫长的预热期，突出消减趋势。
2. PoS 网络: 使用线性标准时间轴。
"""

import os
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import pandas as pd
import numpy as np
from typing import Dict

# ================= 全局配置区域 =================

# 数据文件存放的目录 (如果是当前目录请用 ".")
DATA_DIR = "." 

# 图片输出的总根目录
FIGURES_ROOT = "figures"

# 本脚本对应的子文件夹名称
PLOT_TYPE_NAME = "02_queue"

PROTOCOLS: Dict[str, Dict[str, str]] = {
    "committee": {"label": "Ours", "color": "#1f77b4"},
    "daon": {"label": "Daon", "color": "#ff7f0e"},
    "decentruth": {"label": "Decentruth", "color": "#2ca02c"},
    "seenfeed": {"label": "Seenfeed", "color": "#d62728"},
    "deepthought": {"label": "Deepthought", "color": "#9467bd"},
}

# 样式配置
AXIS_LABEL_SIZE = 44
TICK_LABEL_SIZE = 40
LEGEND_FONT_SIZE = 38
DEFAULT_FIGSIZE = (12, 9)
SAVEFIG_KWARGS = {"bbox_inches": "tight", "pad_inches": 0.1}

# ================= 辅助函数 =================

def format_tick_to_k(value: float, _position: int) -> str:
    """Format tick labels >= 1000 using 'k' suffix."""
    abs_value = abs(value)
    if abs_value >= 1000:
        value_k = value / 1000.0
        if abs(value_k - int(value_k)) < 1e-6:
            return f"{int(value_k)}k"
        return f"{value_k:.1f}k"
    return f"{value:g}"

def get_log_time(time_series: pd.Series, bios: float = 550) -> tuple[np.ndarray, pd.Series]:
    """计算 log(t - bios) 并返回有效掩码"""
    valid_mask = time_series > bios
    # 避免 log(0) 或负数
    shifted = (time_series[valid_mask] - bios).clip(lower=1e-9)
    log_t = np.log(shifted)
    return log_t, valid_mask

def load_data(network: str) -> pd.DataFrame:
    filename = f"total_q_len_{network}.csv"
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f"[Error] Data file not found: {path}")
    return pd.read_csv(path)

# ================= 绘图核心逻辑 =================

def plot_queue_log_dynamics(network: str, out_dir: str):
    print(f"-> Processing {network.upper()} queue dynamics...")
    
    # 局部样式配置
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

    plt.figure(figsize=DEFAULT_FIGSIZE)
    
    # ---------------------------------------------------------
    # 坐标轴处理逻辑
    # ---------------------------------------------------------
    bios_val = 550 if network == 'pow' else 0
    
    if network == 'pow':
        # PoW: 对数时间轴，避免前期等待时间过长导致图形右偏
        x_vals, mask = get_log_time(df['time'], bios=bios_val)
        x_label = f"Log Time (t > {bios_val})"
    else:
        # PoS: 线性时间轴，通常从 0 开始
        mask = df['time'] >= bios_val
        x_vals = df.loc[mask, 'time'] - bios_val
        x_label = "Time (s)"
    
    # ---------------------------------------------------------
    # 绘图循环
    # ---------------------------------------------------------
    for key, config in PROTOCOLS.items():
        if key in df.columns:
            y_vals = df.loc[mask, key]
            
            # 视觉增强: 突出显示 Ours (Committee)
            zorder = 10 if key == 'committee' else 1
            lw = 4.0 if key == 'committee' else 2.5
            alpha = 1.0 if key == 'committee' else 0.8
            
            plt.plot(x_vals, y_vals, label=config['label'], color=config['color'],
                     linewidth=lw, alpha=alpha, zorder=zorder)

    # ---------------------------------------------------------
    # 布局与美化
    # ---------------------------------------------------------
    plt.xlabel(x_label)
    plt.ylabel("Queue Length")

    # 根据数据特征调整图例位置
    if network == 'pos':
        plt.legend(loc='upper right')
    else:
        plt.legend(loc='lower left')
        
    plt.grid(True)
    
    # X轴刻度格式化 (k后缀)
    plt.gca().xaxis.set_major_formatter(FuncFormatter(format_tick_to_k))
    
    plt.tight_layout(pad=1.4)
    
    # 保存文件名: queue_log_dynamics_pow.pdf / queue_log_dynamics_pos.pdf
    save_filename = f"queue_log_dynamics_{network}.pdf"
    save_path = os.path.join(out_dir, save_filename)
    
    plt.savefig(save_path, format="pdf", **SAVEFIG_KWARGS)
    print(f"   [OK] Saved: {save_path}")
    plt.close()

# ================= 运行入口 =================

if __name__ == "__main__":
    # 目标路径: figures/03_queue
    target_dir = os.path.join(FIGURES_ROOT, PLOT_TYPE_NAME)
    os.makedirs(target_dir, exist_ok=True)
    
    print(f"=== Starting Plotting Routine: {PLOT_TYPE_NAME} ===")
    print(f"Target Directory: {target_dir}")
    
    networks = ['pos', 'pow']
    for net in networks:
        plot_queue_log_dynamics(net, target_dir)
        
    print("=== Done ===")