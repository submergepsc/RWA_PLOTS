#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plot 4: RWA-FastOracle 吞吐量稳定性分析 (Throughput Stability)
优化说明:
1. 还原了 PoW 的绘图逻辑（滑动平均平滑曲线）。
2. 修改图例为全局 fig.legend，固定在右上角，横跨断轴子图。
"""

import os
import matplotlib.pyplot as plt
from matplotlib.patches import ConnectionPatch
from matplotlib.ticker import FuncFormatter
import pandas as pd
import numpy as np
from typing import Dict

# ================= 全局配置区域 =================

DATA_DIR = "." 
FIGURES_ROOT = "figure"
PLOT_TYPE_NAME = "03_throughput"

PROTOCOLS: Dict[str, Dict[str, str]] = {
    "committee": {"label": "FastOracle", "color": "#1f77b4"},
    "deepthought": {"label": "Deep.", "color": "#9467bd"},
    "seenfeed": {"label": "Seen.", "color": "#d62728"},
    "decentruth": {"label": "Decen.", "color": "#2ca02c"},
    "daon": {"label": "Daon.", "color": "#ff7f0e"},
}

# 样式配置 (保留原脚本高字号)
AXIS_LABEL_SIZE = 44
TICK_LABEL_SIZE = 40
LEGEND_FONT_SIZE = 30
DEFAULT_FIGSIZE = (12, 9)
SAVEFIG_KWARGS = {}
FIGURE_MARGINS = dict(left=0.12, right=0.97, bottom=0.16, top=0.93)
ANNOTATION_TEXT = "All requests have been handled."
ANNOTATION_TEXT_COLOR = "black"
ANNOTATION_FONT_SIZE = 25 # 文本框字体大小
ANNOTATION_BOX_STYLE = dict(
    boxstyle='round,pad=0.5',
    facecolor='white',
    edgecolor='black',
    alpha=0.95,
)
ANNOTATION_ARROW_STYLE = dict(arrowstyle='->', color='black', lw=1.5)

# ================= 辅助函数 =================

def format_tick_to_k(value: float, _position: int) -> str:
    abs_value = abs(value)
    if abs_value >= 1000:
        value_k = value / 1000.0
        if abs(value_k - int(value_k)) < 1e-6:
            return f"{int(value_k)}k"
        return f"{value_k:.1f}k"
    return f"{value:g}"

def load_data(network: str) -> pd.DataFrame:
    filename = f"total_handled_num_{network}.csv"
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f"[Error] Data file not found: {path}")
    return pd.read_csv(path)

def calculate_throughput(df_handled: pd.DataFrame) -> pd.DataFrame:
    time_col = df_handled['time']
    df_tps = pd.DataFrame({'time': time_col})
    dt = time_col.diff().fillna(1.0).replace(0, 1e-9)
    
    for col in PROTOCOLS.keys():
        if col in df_handled.columns:
            dH = df_handled[col].diff().fillna(0)
            df_tps[col] = (dH / dt).clip(lower=0)
    return df_tps

# ================= 绘图核心逻辑 =================

def plot_throughput_stability(network: str, out_dir: str):
    print(f"-> Processing {network.upper()} throughput stability...")
    
    plt.rcParams.update({
        'font.family': 'sans-serif', 
        'font.sans-serif': ['Arial', 'DejaVu Sans'],
        'axes.unicode_minus': False,
        'axes.labelsize': AXIS_LABEL_SIZE,
        'xtick.labelsize': TICK_LABEL_SIZE,
        'ytick.labelsize': TICK_LABEL_SIZE,
        'legend.fontsize': LEGEND_FONT_SIZE,
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
        # 还原绘图逻辑
        for key, config in PROTOCOLS.items():
            if key in df_tps.columns:
                raw_tps = df_tps.loc[mask, key]
                # 还原：此处可根据需要保留 rolling 或直接 raw
                rolling_mean = raw_tps 
                
                zorder = 10 if key == 'committee' else 1
                alpha = 0.9 if key == 'committee' else 0.7
                lw = 3.0
                
                ax1.plot(x_vals, rolling_mean, label=config['label'], color=config['color'],
                         linewidth=lw, alpha=alpha, zorder=zorder)
                ax2.plot(x_vals, rolling_mean, label=config['label'], color=config['color'],
                         linewidth=lw, alpha=alpha, zorder=zorder)

        ax1.set_ylim(250, 1000)
        ax2.set_ylim(-2, 250)
        ax2.set_xlim(left=0, right=22000)

        ax1.spines['bottom'].set_visible(False)
        ax2.spines['top'].set_visible(False)
        ax1.tick_params(labeltop=False, bottom=False)
        ax2.xaxis.tick_bottom()

        # 断轴标记
        d = .015 
        kwargs = dict(transform=ax1.transAxes, color='k', clip_on=False)
        ax1.plot((-d, +d), (-d, +d), **kwargs)        
        ax1.plot((1 - d, 1 + d), (-d, +d), **kwargs)  
        kwargs.update(transform=ax2.transAxes)
        ax2.plot((-d, +d), (1 - d, 1 + d), **kwargs)  
        ax2.plot((1 - d, 1 + d), (1 - d, 1 + d), **kwargs)

        ax2.set_ylabel("Throughput (TPS)")
        ax2.yaxis.set_label_coords(-0.08, 0.5, transform=ax2.transAxes)
        ax1.grid(True)
        ax2.grid(True)
        ax2.xaxis.set_major_formatter(FuncFormatter(format_tick_to_k))
        
        # 调整布局，为顶部的全局图例腾出空间
        fig.subplots_adjust(hspace=0.05, **FIGURE_MARGINS)

    # ---------------------------------------------------------
    # 场景 B: PoS (横向断轴 - 左右分割)
    # ---------------------------------------------------------
    else:
        fig, (ax1, ax2) = plt.subplots(
            1, 2, sharey=True, figsize=DEFAULT_FIGSIZE,
            gridspec_kw={'width_ratios': [4, 1]}
        )
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


        # 为每个协议添加"处理完成"标注
        # 预先计算每个协议完成处理的时间点（累计值达到最大值）
        completion_times = {}
        for key in PROTOCOLS.keys():
            if key in df.columns:
                col_data = df.loc[mask, key].to_numpy()
                max_val = col_data.max()
                reach_max_indices = np.where(col_data >= max_val - 1)[0]
                if reach_max_indices.size > 0:
                    completion_times[key] = x_vals.to_numpy()[reach_max_indices[0]]

        # 保留 5 个箭头，但指向同一个共享文本框的不同位置
        shared_box_pos   = (0.40, 0.68)
        shared_box_anchor_points = {
            'committee': (0.37, 0.71),
            'daon': (0.39, 0.65),
            'seenfeed': (0.44, 0.65),
            'decentruth': (0.50, 0.65),
            'deepthought': (0.53, 0.65),
        }
        fig.text(
            shared_box_pos[0],
            shared_box_pos[1],
            ANNOTATIO   N_TEXT,
            transform=fig.transFigure,
            fontsize=ANNOTATION_FONT_SIZE,
            color=ANNOTATION_TEXT_COLOR,
            ha='center',
            va='center',
            bbox=ANNOTATION_BOX_STYLE,
        )

        for key in PROTOCOLS.keys():
            if key in completion_times:
                x0 = completion_times[key]
                x_arr = x_vals.to_numpy()
                idx = np.argmin(np.abs(x_arr - x0))
                y0 = df_tps.loc[mask, key].rolling(window=20, min_periods=1).mean().to_numpy()[idx]
                target_ax = ax1 if x0 <= 22000 else ax2
                target_point = shared_box_anchor_points.get(key, shared_box_pos)

                arrow = ConnectionPatch(
                    xyA=(x0, y0),
                    coordsA='data',
                    axesA=target_ax,
                    xyB=target_point,
                    coordsB=fig.transFigure,
                    arrowstyle='->',
                    color='black',
                    lw=1.5,
                    shrinkB=4,
                )
                fig.add_artist(arrow)

        ax1.set_xlim(0, 22000)
        if len(x_vals) > 0:
            total_time = x_vals.max()
            if total_time > 27000:
                ax2.set_xlim(total_time - 5000, total_time+2000)

        ax1.spines['right'].set_visible(False)
        ax2.spines['left'].set_visible(False)
        ax1.tick_params(labelright=False, right=False)
        ax2.tick_params(labelleft=False, left=False)   
        ax2.yaxis.tick_right() 

        d = .015 
        kwargs = dict(transform=ax1.transAxes, color='k', clip_on=False)
        ax1.plot((1 - d, 1 + d), (-d, +d), **kwargs) 
        ax1.plot((1 - d, 1 + d), (1 - d, 1 + d), **kwargs) 
        kwargs.update(transform=ax2.transAxes)
        ax2.plot((-d, +d), (-d, +d), **kwargs) 
        ax2.plot((-d, +d), (1 - d, 1 + d), **kwargs) 

        ax1.set_ylabel("Throughput (TPS)")
        ax1.grid(True)
        ax2.grid(True)
        ax1.xaxis.set_major_formatter(FuncFormatter(format_tick_to_k))
        ax2.xaxis.set_major_formatter(FuncFormatter(format_tick_to_k))
        
        fig.subplots_adjust(wspace=0.05, **FIGURE_MARGINS)

    # ================= 统一图例修改 (全局右上角) =================
    
    # 从第一个子图中获取线条对象和标签
    handles, labels = ax1.get_legend_handles_labels()
    
    # 恢复为全局 fig.legend，并将位置微调向右
    fig.legend(
        handles, 
        labels, 
        loc='upper right', 
        bbox_to_anchor=(0.98, 0.88), # 横轴从0.80改为了0.87，向右移动一点
        ncol=1, 
        fontsize=LEGEND_FONT_SIZE,
        frameon=True,
        edgecolor='gray',
        facecolor='white',
        framealpha=0.8
    )

    # 通用标签设置
    fig.text(0.5, 0.02, x_label, ha='center', va='center', fontsize=AXIS_LABEL_SIZE)
    
    save_filename = f"throughput_stability_{network}.pdf"
    save_path = os.path.join(out_dir, save_filename)
    
    fig.savefig(save_path, format="pdf", **SAVEFIG_KWARGS)
    # fig.savefig(save_path.replace('.pdf', '.png'), format="png", **SAVEFIG_KWARGS)
    print(f"   [OK] Saved: {save_path}")
    plt.close()

# ================= 运行入口 =================

if __name__ == "__main__":
    target_dir = os.path.join(FIGURES_ROOT, PLOT_TYPE_NAME)
    os.makedirs(target_dir, exist_ok=True)
    
    print(f"=== Starting Plotting Routine: {PLOT_TYPE_NAME} ===")
    networks = ['pos', 'pow']
    for net in networks:
        plot_throughput_stability(net, target_dir)
    print("=== Done ===")
