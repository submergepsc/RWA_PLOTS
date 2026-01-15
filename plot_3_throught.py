#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plot 4: RWA-FastOracle 吞吐量稳定性分析 (Throughput Stability)
对应文件夹: figures/04_throughput/
说明: 
1. PoW 网络使用纵向断轴 (上下分割)，解决竞品 TPS 过低导致的时间轴压缩问题。
2. PoS 网络使用横向断轴 (左右分割)，解决长时间运行后期的偶发波动展示问题。
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
PLOT_TYPE_NAME = "03_throughput"

PROTOCOLS: Dict[str, Dict[str, str]] = {
    "committee": {"label": "Ours", "color": "#1f77b4"},
    "daon": {"label": "Daon", "color": "#ff7f0e"},
    "decentruth": {"label": "Decentruth", "color": "#2ca02c"},
    "seenfeed": {"label": "Seenfeed", "color": "#d62728"},
    "deepthought": {"label": "Deepthought", "color": "#9467bd"},
}

# 样式配置 (保留原脚本的高字号设置)
AXIS_LABEL_SIZE = 44
TICK_LABEL_SIZE = 40
LEGEND_FONT_SIZE = 38
DEFAULT_FIGSIZE = (12, 9)
SAVEFIG_KWARGS = {"bbox_inches": "tight", "pad_inches": 0.1}

# ================= 辅助函数 =================

def format_tick_to_k(value: float, _position: int) -> str:
    """将 >= 1000 的数值格式化为 'k' 后缀"""
    abs_value = abs(value)
    if abs_value >= 1000:
        value_k = value / 1000.0
        if abs(value_k - int(value_k)) < 1e-6:
            return f"{int(value_k)}k"
        return f"{value_k:.1f}k"
    return f"{value:g}"

def load_data(network: str) -> pd.DataFrame:
    """加载总处理数数据"""
    filename = f"total_handled_num_{network}.csv"
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f"[Error] Data file not found: {path}")
    return pd.read_csv(path)

def calculate_throughput(df_handled: pd.DataFrame) -> pd.DataFrame:
    """从累计处理数计算瞬时 TPS (差分法)"""
    time_col = df_handled['time']
    df_tps = pd.DataFrame({'time': time_col})
    # 防止除零错误
    dt = time_col.diff().fillna(1.0).replace(0, 1e-9)
    
    for col in PROTOCOLS.keys():
        if col in df_handled.columns:
            dH = df_handled[col].diff().fillna(0)
            df_tps[col] = (dH / dt).clip(lower=0)
    return df_tps

# ================= 绘图核心逻辑 =================

def plot_throughput_stability(network: str, out_dir: str):
    print(f"-> Processing {network.upper()} throughput stability...")
    
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

    df_tps = calculate_throughput(df) 
    bios_val = 550 if network == 'pow' else 0
    
    # 滤除预热阶段数据并对时间轴做平移
    mask = df_tps['time'] > bios_val
    x_vals = df_tps.loc[mask, 'time'] - bios_val
    x_label = "Time (s)"

    # ---------------------------------------------------------
    # 场景 A: PoW (纵向断轴 - 上下分割)
    # ---------------------------------------------------------
    if network == 'pow':
        fig, (ax1, ax2) = plt.subplots(
            2, 1, sharex=True, figsize=DEFAULT_FIGSIZE,
            gridspec_kw={'height_ratios': [1, 6]}
        )
        fig.subplots_adjust(hspace=0.05) 

        for key, config in PROTOCOLS.items():
            if key in df_tps.columns:
                raw_tps = df_tps.loc[mask, key]
                # 滑动平均平滑曲线
                rolling_mean = raw_tps
                
                zorder = 10 if key == 'committee' else 1
                alpha = 0.9 if key == 'committee' else 0.7
                lw = 3.0
                
                ax1.plot(x_vals, rolling_mean, label=config['label'], color=config['color'],
                         linewidth=lw, alpha=alpha, zorder=zorder)
                ax2.plot(x_vals, rolling_mean, label=config['label'], color=config['color'],
                         linewidth=lw, alpha=alpha, zorder=zorder)

        # 设置断轴范围 (根据实际数据可能需要微调)

        ax1.set_ylim(250, 1000)   # 上半部分：显示高 TPS (Ours)
        ax2.set_ylim(-2, 250)     # 下半部分：显示低 TPS (竞品)
        ax2.set_xlim(left=0, right=22000)



        # 隐藏多余边框
        ax1.spines['bottom'].set_visible(False)
        ax2.spines['top'].set_visible(False)
        ax1.tick_params(labeltop=False, bottom=False)
        ax2.xaxis.tick_bottom()

        # 绘制断轴处的斜线标记
        d = .015 
        kwargs = dict(transform=ax1.transAxes, color='k', clip_on=False)
        ax1.plot((-d, +d), (-d, +d), **kwargs)        
        ax1.plot((1 - d, 1 + d), (-d, +d), **kwargs)  
        kwargs.update(transform=ax2.transAxes)
        ax2.plot((-d, +d), (1 - d, 1 + d), **kwargs)  
        ax2.plot((1 - d, 1 + d), (1 - d, 1 + d), **kwargs)

        ax2.legend(loc='upper right') 
        ax2.set_ylabel("Throughput (TPS)")
        ax2.yaxis.set_label_coords(-0.08, 0.5, transform=ax2.transAxes)
        ax1.grid(True)
        ax2.grid(True)
        ax2.xaxis.set_major_formatter(FuncFormatter(format_tick_to_k))
        plt.tight_layout()
        plt.subplots_adjust(hspace=0.05)

    # ---------------------------------------------------------
    # 场景 B: PoS (横向断轴 - 左右分割)
    # ---------------------------------------------------------
    else:
        fig, (ax1, ax2) = plt.subplots(
            1, 2, sharey=True, figsize=DEFAULT_FIGSIZE,
            gridspec_kw={'width_ratios': [4, 1]}
        )
        fig.subplots_adjust(wspace=0.05)

        for key, config in PROTOCOLS.items():
            if key in df_tps.columns:
                raw_tps = df_tps.loc[mask, key]
                rolling_mean = raw_tps.rolling(window=20, min_periods=1).mean()
                
                zorder = 10 if key == 'committee' else 1
                alpha = 0.9 if key == 'committee' else 0.7
                lw = 3.0
                
                ax1.plot(x_vals, rolling_mean, label=config['label'], color=config['color'],
                         linewidth=lw, alpha=alpha, zorder=zorder)
                ax2.plot(x_vals, rolling_mean, label=config['label'], color=config['color'],
                         linewidth=lw, alpha=alpha, zorder=zorder)



    
        # 设置断轴范围
        ax1.set_xlim(0, 22000)
        if len(x_vals) > 0:
            total_time = x_vals.max()
            if total_time > 27000:
                ax2.set_xlim(total_time - 5000, total_time+2000)

        # 隐藏多余边框
        ax1.spines['right'].set_visible(False)
        ax2.spines['left'].set_visible(False)
        ax1.tick_params(labelright=False, right=False)
        ax2.tick_params(labelleft=False, left=False)   
        ax2.yaxis.tick_right() 
        ax2.tick_params(right=False) 

        # 绘制断轴处的斜线标记
        d = .015 
        kwargs = dict(transform=ax1.transAxes, color='k', clip_on=False)
        ax1.plot((1 - d, 1 + d), (-d, +d), **kwargs) 
        ax1.plot((1 - d, 1 + d), (1 - d, 1 + d), **kwargs) 

        kwargs.update(transform=ax2.transAxes)
        ax2.plot((-d, +d), (-d, +d), **kwargs) 
        ax2.plot((-d, +d), (1 - d, 1 + d), **kwargs) 

        ax1.set_ylabel("Throughput (TPS)")
        ax2.legend(loc='upper right')
        
        ax1.grid(True)
        ax2.grid(True)
        ax1.xaxis.set_major_formatter(FuncFormatter(format_tick_to_k))
        ax2.xaxis.set_major_formatter(FuncFormatter(format_tick_to_k))
        plt.tight_layout()
        plt.subplots_adjust(wspace=0.05, top=0.9)

    # 通用标签设置
    fig.text(0.5, 0.02, x_label, ha='center', va='center', fontsize=AXIS_LABEL_SIZE)
    
    # 保存文件: throughput_stability_pow.pdf / throughput_stability_pos.pdf
    save_filename = f"throughput_stability_{network}.pdf"
    save_path = os.path.join(out_dir, save_filename)
    
    plt.savefig(save_path, format="pdf", **SAVEFIG_KWARGS)
    print(f"   [OK] Saved: {save_path}")
    plt.close()

# ================= 运行入口 =================

if __name__ == "__main__":
    # 目标路径: figures/04_throughput
    target_dir = os.path.join(FIGURES_ROOT, PLOT_TYPE_NAME)
    os.makedirs(target_dir, exist_ok=True)
    
    print(f"=== Starting Plotting Routine: {PLOT_TYPE_NAME} ===")
    print(f"Target Directory: {target_dir}")
    
    networks = ['pos', 'pow']
    for net in networks:
        plot_throughput_stability(net, target_dir)

    
    print("=== Done ===")