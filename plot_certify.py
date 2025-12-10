#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
证书生成性能分析脚本 (CDF & PDF)
"""

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import pandas as pd
import numpy as np
import os
import seaborn as sns

# ================= 全局配置区域 (参考 plot_full_8_analysis.py) =================

PROTOCOLS = {
    'committee': {'label': 'Ours', 'color': '#1f77b4'},
    'daon': {'label': 'Daon', 'color': '#ff7f0e'},
    'decentruth': {'label': 'Decentruth', 'color': '#2ca02c'},
    'seenfeed': {'label': 'Seenfeed', 'color': '#d62728'}
}
DEFAULT_FIGSIZE = (12, 9)
AXIS_LABEL_SIZE = 44
TICK_LABEL_SIZE = 40
LEGEND_FONT_SIZE = 38
SAVEFIG_KWARGS = {'bbox_inches': 'tight', 'pad_inches': 0.1}

# ================= 辅助函数区域 =================

def format_tick_to_k(value: float, _position: int) -> str:
    """Format tick labels >= 1000 using 'k' suffix while keeping smaller values intact."""
    abs_value = abs(value)
    if abs_value >= 1000:
        value_k = value / 1000.0
        if abs(value_k - int(value_k)) < 1e-6:
            return f"{int(value_k)}k"
        return f"{value_k:.1f}k"
    return f"{value:g}"

# ================= 绘图函数区域 =================

def plot_cert_interval_cdf(network: str, out_dir: str):
    """【图1】证书生成间隔 CDF (Inter-Arrival Time)"""
    plt.rcParams.update({
        'font.family': 'sans-serif', 'font.sans-serif': ['Arial', 'DejaVu Sans'],
        'axes.unicode_minus': False,
        'font.size': 14,
        'axes.labelsize': AXIS_LABEL_SIZE,
        'axes.titlesize': 18,
        'xtick.labelsize': TICK_LABEL_SIZE,
        'ytick.labelsize': TICK_LABEL_SIZE,
        'legend.fontsize': LEGEND_FONT_SIZE,
        'figure.figsize': DEFAULT_FIGSIZE,
        'grid.linestyle': '--', 'grid.alpha': 0.6
    })
    print(f"-> [1/2] Plotting Certificate Inter-Arrival CDF for {network.upper()}...")
    
    try:
        df = pd.read_csv(f"certif_gen_{network}.csv")
    except FileNotFoundError:
        print(f"   [Error] File not found: certif_gen_{network}.csv. Skipping CDF plot.")
        return

    plt.figure(figsize=DEFAULT_FIGSIZE)
    
    for key, config in PROTOCOLS.items():
        if key in df.columns:
            # since_time 是累积时间，求差分得到每个证书的生成间隔
            intervals = df[key].diff().dropna()
            intervals = intervals[intervals > 0] # 过滤异常值
            if intervals.empty:
                continue

            data = np.sort(intervals)
            cdf = np.arange(1, len(data) + 1) / len(data)
            
            lw = 4.0 if key == 'committee' else 2.5
            zorder = 10 if key == 'committee' else 1
            plt.plot(data, cdf, label=config['label'], color=config['color'], linewidth=lw, zorder=zorder)

    plt.xlabel("Certificate Inter-Arrival Time (s)")
    plt.ylabel("Cumulative Probability")
    plt.xscale('log')
    plt.legend(loc='lower right')
    plt.grid(True, which="both", linestyle='--')
    plt.gca().xaxis.set_major_formatter(FuncFormatter(format_tick_to_k))
    plt.tight_layout()
    
    save_path = os.path.join(out_dir, "cert_interval_cdf.pdf")
    plt.savefig(save_path, format="pdf", **SAVEFIG_KWARGS)
    plt.close()
    print(f"   [OK] Saved: {save_path}")

def plot_cert_interval_kde(network: str, out_dir: str):
    """【图2】证书生成间隔 PDF/KDE (Inter-Arrival Time)"""
    plt.rcParams.update({
        'font.family': 'sans-serif', 'font.sans-serif': ['Arial', 'DejaVu Sans'],
        'axes.unicode_minus': False,
        'font.size': 14,
        'axes.labelsize': AXIS_LABEL_SIZE,
        'axes.titlesize': 18,
        'xtick.labelsize': TICK_LABEL_SIZE,
        'ytick.labelsize': TICK_LABEL_SIZE,
        'legend.fontsize': LEGEND_FONT_SIZE,
        'figure.figsize': DEFAULT_FIGSIZE,
        'grid.linestyle': '--', 'grid.alpha': 0.6
    })
    print(f"-> [2/2] Plotting Certificate Inter-Arrival KDE for {network.upper()}...")

    try:
        df = pd.read_csv(f"certif_gen_{network}.csv")
    except FileNotFoundError:
        print(f"   [Error] File not found: certif_gen_{network}.csv. Skipping KDE plot.")
        return

    plt.figure(figsize=DEFAULT_FIGSIZE)
    ax = plt.gca()

    for key, config in PROTOCOLS.items():
        if key in df.columns:
            intervals = df[key].diff().dropna()
            intervals = intervals[intervals > 0]
            if intervals.empty:
                continue
            
            sns.kdeplot(
                data=intervals, color=config['color'], fill=True, alpha=0.1, 
                linewidth=2.5, ax=ax, label=config['label'], warn_singular=False
            )

    plt.xlabel("Certificate Inter-Arrival Time (s)")
    plt.ylabel("Density")
    plt.legend(loc='upper right')
    plt.grid(True, linestyle='--')
    ax.xaxis.set_major_formatter(FuncFormatter(format_tick_to_k))
    
    # 根据网络类型调整x轴范围，避免图像过于拥挤
    if network == 'pow':
        plt.xlim(left=0, right=max(100, df.diff().max().max() * 0.6)) # 动态调整
    else:
        plt.xlim(left=0)

    plt.tight_layout()
    
    save_path = os.path.join(out_dir, "cert_interval_kde.pdf")
    plt.savefig(save_path, format="pdf", **SAVEFIG_KWARGS)
    plt.close()
    print(f"   [OK] Saved: {save_path}")

# ================= 主程序入口 =================

def main():
    networks = ['pow', 'pos']
    
    for network in networks:
        # 根据 plot_full_8_analysis.py 的目录结构进行适配
        base_dir = f"figs_{network}_basic3"
        certif_dir = os.path.join(base_dir, "certif")
        os.makedirs(certif_dir, exist_ok=True)
        
        print(f"\n{'='*20} Processing {network.upper()} Certificate Plots {'='*20}")
        
        plot_cert_interval_cdf(network, certif_dir)
        plot_cert_interval_kde(network, certif_dir)
        
        print(f"Certificate charts saved to -> {certif_dir}")

if __name__ == "__main__":
    main()
