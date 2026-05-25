#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plot 5: RWA-FastOracle 证书生成时间 CDF (Certificate Generation CDF)
对应文件夹: figures/05_certificate/
说明: 
1. 读取 certif_gen_{network}.csv 文件。
2. 绘制各协议证书生成时间的累积分布函数 (CDF)。
3. 针对 Ours (Committee) 协议自动标注 P90 关键点。
"""

import os
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import pandas as pd
import numpy as np
from typing import Dict

# ================= 全局配置区域 =================

# 数据文件存放的目录
DATA_DIR = "." 

# 图片输出的总根目录
FIGURES_ROOT = "figures"

# 本脚本对应的子文件夹名称
PLOT_TYPE_NAME = "05_certificate"

PROTOCOLS: Dict[str, Dict[str, str]] = {
    "committee": {"label": "Ours", "color": "#DF3156"},
    "daon": {"label": "Daon", "color": "#56B4E9"},
    "decentruth": {"label": "Decentruth", "color": "#009E73"},
    "seenfeed": {"label": "Seenfeed", "color": "#E69F00"},
    "deepthought": {"label": "Deepthought", "color": "#4A0080"},
}

# 样式配置 (保持与前序图表一致的论文级样式)
AXIS_LABEL_SIZE = 44
TICK_LABEL_SIZE = 40
LEGEND_FONT_SIZE = 38
DEFAULT_FIGSIZE = (12, 9)
SAVEFIG_KWARGS = {"bbox_inches": "tight", "pad_inches": 0.1}

# ================= 辅助函数 =================

def load_data(network: str) -> pd.DataFrame:
    """加载证书生成数据"""
    filename = f"certif_gen_{network}.csv"
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f"[Error] Data file not found: {path}")
    return pd.read_csv(path)

# ================= 绘图核心逻辑 =================

def plot_certificate_cdf(network: str, out_dir: str):
    print(f"-> Processing {network.upper()} certificate CDF...")
    
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
    
    # 遍历协议配置，确保颜色和顺序统一
    for key, config in PROTOCOLS.items():
        # 如果 CSV 中包含该协议列
        if key in df.columns:
            # 提取数据并清洗
            data_col = df[key].dropna()
            if data_col.empty:
                continue
            
            # 数据排序
            sorted_data = np.sort(data_col)
            # 计算 CDF Y轴 (从 1/n 到 1)
            yvals = np.arange(1, len(sorted_data) + 1) / len(sorted_data)
            
            # 视觉增强: 突出显示 Ours
            lw = 4.0 if key == 'committee' else 2.5
            alpha = 1.0 if key == 'committee' else 0.8
            zorder = 10 if key == 'committee' else 2
            
            # 绘制 CDF 曲线
            plt.plot(sorted_data, yvals, label=config['label'], color=config['color'], 
                     linewidth=lw, alpha=alpha, zorder=zorder)
            
            # 绘制阴影填充 (仅稍微增加一点层次感)
            plt.fill_between(sorted_data, yvals, color=config['color'], alpha=0.05, zorder=1)

            # --- 特殊处理: 为 Ours 添加 P90 标注 ---
            if key == 'committee':
                p90_idx = int(len(yvals) * 0.9)
                if p90_idx < len(yvals):
                    val_p90 = sorted_data[p90_idx]
                    
                    # 绘制 P90 辅助虚线
                    plt.axvline(x=val_p90, color='gray', linestyle='--', alpha=0.8, linewidth=3, zorder=5)
                    plt.axhline(y=0.9, color='gray', linestyle='--', alpha=0.8, linewidth=3, zorder=5)
                    
                    # 添加文本标注框
                    plt.text(
                        val_p90 * 1.1,  # X坐标微调
                        0.82,           # Y坐标微调
                        f"P90 ≈ {val_p90:.2f}s", 
                        fontsize=25, 
                        color='#333333', 
                        fontweight='bold',
                        bbox=dict(facecolor='white', alpha=0.9, edgecolor='none', pad=2),
                        zorder=20
                    )

    # 布局与美化
    plt.xlabel("Generation Time (s)")
    plt.ylabel("CDF")
    # plt.title("Certificate Generation Time CDF") # 论文通常不需要图内标题
    
    # 如果数据跨度大，可以考虑 Log 轴 (根据之前代码习惯，这里保持线性，如需 Log 可取消注释)
    # plt.xscale('log') 
    
    plt.legend(loc='lower right')
    plt.grid(True, linewidth=1.5)
    
    plt.tight_layout()
    
    # 保存文件: certificate_cdf_pow.pdf / certificate_cdf_pos.pdf
    save_filename = f"certificate_cdf_{network}.pdf"
    save_path = os.path.join(out_dir, save_filename)
    
    plt.savefig(save_path, format="pdf", **SAVEFIG_KWARGS)
    print(f"   [OK] Saved: {save_path}")
    plt.close()

# ================= 运行入口 =================

if __name__ == "__main__":
    # 目标路径: figures/05_certificate
    target_dir = os.path.join(FIGURES_ROOT, PLOT_TYPE_NAME)
    os.makedirs(target_dir, exist_ok=True)
    
    print(f"=== Starting Plotting Routine: {PLOT_TYPE_NAME} ===")
    print(f"Target Directory: {target_dir}")
    
    networks = ['pos', 'pow']
    for net in networks:
        plot_certificate_cdf(net, target_dir)
        
    print("=== Done ===")
