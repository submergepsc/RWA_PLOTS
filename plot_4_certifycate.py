#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plot 5: RWA-FastOracle 证书生成时间 CDF (Certificate Generation CDF)
说明: 
1. 彻底修复箭头坐标系飞出的 bug：拆分文本和箭头，全量使用 data 坐标系绝对定位。
"""

import os
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MultipleLocator
import pandas as pd
import numpy as np
from typing import Dict

# ================= 全局配置区域 =================

DATA_DIR = "." 
FIGURES_ROOT = "figures"
PLOT_TYPE_NAME = "04_certificate"
PEAK_ANNOTATION_ARROW_KEY = "committee"

# 定义协议配置
PROTOCOLS: Dict[str, Dict[str, str]] = {
    "committee": {"label": "FastOracle", "color": "#1f77b4", "marker": "o"},
    "deepthought": {"label": "Deep.", "color": "#9467bd", "marker": "v"},
    "seenfeed": {"label": "Sen.", "color": "#d62728", "marker": "D"},
    "decentruth": {"label": "DECEN.", "color": "#2ca02c", "marker": "^"},
    "daon": {"label": "DAON", "color": "#ff7f0e", "marker": "s"},
}

# 【关键修改】：适合单栏排版的尺寸与字号
AXIS_LABEL_SIZE = 24  # 坐标轴标题
TICK_LABEL_SIZE = 20  # 坐标轴数字
LEGEND_FONT_SIZE = 18 # 图例字号
DEFAULT_FIGSIZE = (8, 6) # 画布尺寸：8宽, 6高 (经典的 4:3 比例)

SAVEFIG_KWARGS = {}
FIGURE_MARGINS = dict(left=0.16, right=0.97, bottom=0.16, top=0.93)
MARKER_SIZE_OURS = 24
MARKER_SIZE_OTHERS = 18
PLATEAU_MARKERS_PER_SEGMENT = 4
Y_AXIS_EXTRA_PADDING = 1.22


def load_data(network: str) -> pd.DataFrame:
    filename = f"certif_gen_{network}.csv"
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f"[Error] Data file not found: {path}")
    return pd.read_csv(path)

def get_marker_indices(total_points: int, num_markers: int = 10):
    if total_points <= 0:
        return []
    if total_points <= num_markers:
        return list(range(total_points))
    return np.linspace(0, total_points - 1, num_markers, dtype=int).tolist()

def compute_shared_y_top(networks):
    max_certs = 1
    for net in networks:
        try:
            df = load_data(net)
        except FileNotFoundError:
            continue
        for key in PROTOCOLS.keys():
            if key in df.columns:
                max_certs = max(max_certs, int(df[key].dropna().shape[0]))
    return max_certs * 1.05

def format_scientific(value: float, _position: int) -> str:
    if abs(value) >= 1000:
        mantissa, exponent = f"{value:.1e}".split("e")
        return f"{float(mantissa):g}e{int(exponent)}"
    return f"{value:g}"

def format_integer(value: float, _position: int) -> str:
    return f"{int(value):d}"

# ================= 绘图核心逻辑 =================

def plot_certificate_cdf(network: str, out_dir: str, shared_y_top: float = None):
    print(f"-> Processing {network.upper()} certificate CDF (Hardcoded Coordinates)...")
    
    plt.rcParams.update({
        'font.family': 'sans-serif', 
        'font.sans-serif': ['DejaVu Sans', 'Arial'],
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
    peak_points = {}
    plateau_segments = []
    
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
    
    draw_order = list(PROTOCOLS.items())[::-1]

    for key, config in draw_order:
        if key in df.columns:
            data_col = df[key].dropna()
            if data_col.empty:
                continue
            
            sorted_data = np.sort(data_col)
            yvals = np.arange(1, len(sorted_data) + 1)
            
            # Draw each protocol up to its own completion time first.
            # The shared top plateau is rendered in colored segments later.
            x_extended = np.concatenate(([0], sorted_data))
            y_extended = np.concatenate(([0], yvals))
            
            lw = 4.0 if key == 'committee' else 2.5
            alpha_line = 1.0 if key == 'committee' else 0.8
            zorder = 10 if key == 'committee' else 2
            marker_idx = get_marker_indices(len(x_extended), num_markers=10)
            
            ax.plot(x_extended, y_extended, label=config['label'], color=config['color'], 
                    linewidth=lw, alpha=alpha_line, zorder=zorder,
                    marker=config['marker'], markersize=MARKER_SIZE_OURS if key == 'committee' else MARKER_SIZE_OTHERS,
                    markevery=marker_idx, markeredgewidth=0.8, markeredgecolor='white')

            peak_points[key] = (float(sorted_data[-1]), float(len(sorted_data)))
            plateau_segments.append(
                {
                    "key": key,
                    "x_end": float(sorted_data[-1]),
                    "y_end": float(len(sorted_data)),
                    "color": config["color"],
                    "zorder": zorder,
                    "lw": lw,
                    "alpha": alpha_line,
                    "marker": config["marker"],
                }
            )

    # Render the final horizontal plateau as colored segments by completion order.
    # Each interval [x_i, x_{i+1}] uses protocol i's final color.
    if plateau_segments:
        plateau_segments.sort(key=lambda item: item["x_end"])
        for idx, seg in enumerate(plateau_segments):
            x_start = seg["x_end"]
            x_stop = plateau_segments[idx + 1]["x_end"] if idx + 1 < len(plateau_segments) else global_max_time
            if x_stop > x_start:
                x_seg = np.linspace(x_start, x_stop, PLATEAU_MARKERS_PER_SEGMENT + 2)
                y_seg = np.full_like(x_seg, seg["y_end"], dtype=float)
                marker_idx = get_marker_indices(len(x_seg), num_markers=PLATEAU_MARKERS_PER_SEGMENT)
                marker_size = MARKER_SIZE_OURS if seg["key"] == "committee" else MARKER_SIZE_OTHERS
                ax.plot(
                    x_seg,
                    y_seg,
                    color=seg["color"],
                    linewidth=seg["lw"],
                    alpha=seg["alpha"],
                    zorder=seg["zorder"],
                    marker=seg["marker"],
                    markersize=marker_size,
                    markevery=marker_idx,
                    markeredgewidth=0.8,
                    markeredgecolor='white',
                )

    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Number of Certificates")
    ax.set_xlim(left=0, right=global_max_time)
    ax.xaxis.set_major_locator(MultipleLocator(5000))
    ax.xaxis.set_major_formatter(FuncFormatter(format_scientific))
    ax.yaxis.set_major_formatter(FuncFormatter(format_scientific))
    
    max_certs = max([len(df[key].dropna()) for key in PROTOCOLS.keys() if key in df.columns]) if not df.empty else 1
    y_top_base = shared_y_top if shared_y_top is not None else (max_certs * 1.05)
    y_top = y_top_base * Y_AXIS_EXTRA_PADDING
    ax.set_ylim(bottom=0, top=y_top)
    
    ax.grid(True, linewidth=1.5)
    ax.yaxis.set_major_locator(MultipleLocator(500))
    ax.yaxis.set_major_formatter(FuncFormatter(format_integer))
    ax.tick_params(axis='y', which='major', direction='out', length=7, width=1.4, pad=6)

    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ordered_labels = [cfg['label'] for cfg in PROTOCOLS.values() if cfg['label'] in by_label]
    ordered_handles = [by_label[l] for l in ordered_labels]
    ax.legend(ordered_handles, ordered_labels, loc='lower right')

    def line_rectangle_edge(start_disp, end_disp, bbox):
        sx, sy = start_disp
        ex, ey = end_disp
        dx = ex - sx
        dy = ey - sy
        candidates = []

        if abs(dx) > 1e-9:
            for x_edge in (bbox.x0, bbox.x1):
                t = (x_edge - sx) / dx
                y_edge = sy + t * dy
                if t > 0 and bbox.y0 <= y_edge <= bbox.y1:
                    candidates.append((t, (x_edge, y_edge)))

        if abs(dy) > 1e-9:
            for y_edge in (bbox.y0, bbox.y1):
                t = (y_edge - sy) / dy
                x_edge = sx + t * dx
                if t > 0 and bbox.x0 <= x_edge <= bbox.x1:
                    candidates.append((t, (x_edge, y_edge)))

        if not candidates:
            return start_disp
        return min(candidates, key=lambda item: item[0])[1]

    # ================= 【修复核心区】绝对数值定位 =================
    if peak_points:
        # 绘制空心大圆圈强调
        for key, (x0, y0) in peak_points.items():
            ax.scatter([x0], [y0], s=420, facecolors='none', edgecolors='black', linewidths=1.5, zorder=20)

        # 获取 FastOracle 的数据点作为起点 (x0, y0)
        arrow_key = PEAK_ANNOTATION_ARROW_KEY if PEAK_ANNOTATION_ARROW_KEY in peak_points else next(iter(peak_points))
        x0, y0 = peak_points[arrow_key]

        # 计算文本框的绝对坐标 (全用 data 坐标系)，并强制限制在坐标轴内部。
        x_text_data = np.clip(global_max_time * 0.52, 0.10 * global_max_time, 0.90 * global_max_time)
        # Put the text box into the enlarged upper blank area.
        y_text_data = np.clip(y_top * 0.92, 0.20 * y_top, 0.97 * y_top)

        # 1. 独立放置文本框
        text_artist = ax.text(
            x=x_text_data, 
            y=y_text_data,
            s="Peak certificates reached.",
            fontsize=18,
            color='black',
            ha='center',
            va='center',
            clip_on=True,
            bbox=dict(boxstyle='round,pad=0.55', facecolor='white', edgecolor='black', alpha=0.92)
        )

        # 2. Draw the arrow from the real text-box edge to the peak point.
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
        text_bbox = text_artist.get_window_extent(renderer=renderer)
        text_center_disp = ax.transData.transform((x_text_data, y_text_data))
        peak_disp = ax.transData.transform((x0, y0))
        arrow_start_disp = line_rectangle_edge(text_center_disp, peak_disp, text_bbox)
        arrow_start_data = ax.transData.inverted().transform(arrow_start_disp)
        ax.annotate(
            text="", 
            xy=(x0, y0),                   # 终点 (数据点)
            xycoords='data',
            xytext=arrow_start_data,
            textcoords='data',
            annotation_clip=True,
            arrowprops=dict(
                arrowstyle='->',
                color='#d62728',
                lw=2.0,
                mutation_scale=14,
                shrinkA=0,
                shrinkB=2                  # B端缩进：碰到边框即止
            )
        )
    
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
    
    networks = ['pos', 'pow']
    shared_y_top = compute_shared_y_top(networks)
    for net in networks:
        plot_certificate_cdf(net, target_dir, shared_y_top=shared_y_top)
        
    print("=== Done ===")
