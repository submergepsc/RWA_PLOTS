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
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter, MultipleLocator
import pandas as pd
import numpy as np
from typing import Dict

# ================= 全局配置区域 =================

DATA_DIR = "." 
FIGURES_ROOT = "figures"
PLOT_TYPE_NAME = "03_throughput"

PROTOCOLS: Dict[str, Dict[str, str]] = {
    "committee": {"label": "FastOracle", "color": "#DF3156"},
    "deepthought": {"label": "Deep.", "color": "#4A0080"},
    "seenfeed": {"label": "Sen.", "color": "#E69F00"},
    "decentruth": {"label": "DECEN.", "color": "#009E73"},
    "daon": {"label": "DAON", "color": "#56B4E9"},
}

# 样式配置 (保留原脚本高字号)
AXIS_LABEL_SIZE = 28
TICK_LABEL_SIZE = 24
LEGEND_FONT_SIZE = 14
DEFAULT_FIGSIZE = (8, 6)
SAVEFIG_KWARGS = {} 
FIGURE_MARGINS = dict(left=0.12, right=0.97, bottom=0.16, top=0.93)
POW_BOXPLOT_MARGINS = dict(left=0.22, right=0.96, bottom=0.16, top=0.88)
POW_PANEL_TITLE_SIZE = 20
POW_PANEL_TICK_LABEL_SIZE = 24
POW_PANEL_HSPACE = 0.24
POW_PANEL_LEGEND_FONT_SIZE = 21
POW_DEEP_PANEL_HEIGHT_RATIO = 1.6
POW_DEEP_KEY = "deepthought"
POW_COMBINED_Y_TICK_STEP = 20.0
POW_DEEP_Y_TICK_STEP = 0.10
POW_RANGE_IGNORED_KEYS = {"decentruth"}
POW_LINE_WIDTH_FAST = 2.2
POW_LINE_WIDTH_BASELINE = 1.6
POW_VLINE_WIDTH = 1.4
POS_FIGURE_MARGINS = dict(left=0.22, right=0.97, bottom=0.18, top=0.95)
POS_AXIS_LABEL_SIZE = 28
POS_TICK_LABEL_SIZE = 24
POS_LEGEND_FONT_SIZE = 14
POS_ANNOTATION_FONT_SIZE = 18
POS_LINE_WIDTH_FAST = 2.2
POS_LINE_WIDTH_BASELINE = 1.6
POS_VLINE_WIDTH = 1.5
POS_ANNOTATION_BOX_STYLE = dict(
    boxstyle='round,pad=0.55',
    facecolor='white',
    edgecolor='black',
    alpha=0.95,
)
POW_AXIS_CONFIG = {
    "committee": {
        "xlim": (13, 72),
        "ticks": [13, 33, 53, 72],
        "labels": ["13", "33", "53", "72"],
    },
    "deepthought": {
        "xlim": (0.01, 0.09),
        "ticks": [0.01, 0.04, 0.06, 0.09],
        "labels": ["0.01", "0.04", "0.06", "0.09"],
    },
    "seenfeed": {
        "xlim": (13, 15.8),
        "ticks": [13, 14, 15],
        "labels": ["13", "14", "15"],
    },
    "decentruth": {
        "xlim": (9.0, 11.0),
        "ticks": [9.0, 9.6, 10.0, 11.0],
        "labels": ["9.0", "9.6", "10", "11"],
    },
    "daon": {
        "xlim": (0.0, 38.0),
        "ticks": [0, 13, 25, 38],
        "labels": ["0.00", "13", "25", "38"],
    },
}
ANNOTATION_TEXT = "All requests\nhave been handled"
ANNOTATION_TEXT_COLOR = "black"
ANNOTATION_FONT_SIZE = 18
ANNOTATION_BOX_STYLE = dict(
    boxstyle='round,pad=0.75',
    facecolor='white',
    edgecolor='black',
    alpha=0.95,
)
    
ANNOTATION_ARROW_STYLE = dict(arrowstyle='->', color='black', lw=1.5)
X_MAX_SECONDS = 22000
SECONDS_PER_MINUTE = 60
X_TICK_MINUTES = 40

# ================= 辅助函数 =================

def format_time_to_min(value: float, _position: int) -> str:
    return f"{value:.0f}"

def format_tick_to_k(value: float, _position: int) -> str:
    abs_value = abs(value)
    if abs_value >= 1000:
        value_k = value / 1000.0
        if abs(value_k - int(value_k)) < 1e-6:
            return f"{int(value_k)}k"
        return f"{value_k:.1f}k"
    return f"{value:g}"

def format_panel_tick(value: float) -> str:
    if abs(value) >= 10:
        return f"{value:.0f}"
    if abs(value) >= 1:
        return f"{value:.1f}"
    return f"{value:.2f}"

def get_nice_throughput_axis(max_value: float) -> tuple[float, float]:
    if max_value <= 0:
        return 1.0, 0.25
    if max_value <= 0.2:
        step = 0.05
    elif max_value <= 1:
        step = 0.2
    elif max_value <= 3:
        step = 0.5
    elif max_value <= 5:
        step = 1.0
    elif max_value <= 15:
        step = 5.0
    else:
        step = 10.0
    upper = np.ceil(max_value * 1.05 / step) * step
    return float(max(upper, step)), step

def get_nice_time_axis(max_minutes: float) -> tuple[float, float]:
    if not np.isfinite(max_minutes) or max_minutes <= 0:
        return X_MAX_SECONDS / SECONDS_PER_MINUTE, X_TICK_MINUTES
    if max_minutes <= 80:
        step = 10.0
    elif max_minutes <= 180:
        step = 20.0
    else:
        step = 40.0
    upper = np.ceil(max_minutes * 1.03 / step) * step
    return float(max(upper, step)), step

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
        'font.sans-serif': ['DejaVu Sans', 'Arial'],
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
    x_vals = (df_tps.loc[mask, 'time'] - bios_val) / SECONDS_PER_MINUTE
    x_label = "Time (min)"
    legend_handles = None
    legend_labels = None
    legend_bbox = (0.985, 0.93)
    legend_ncol = 1
    legend_font_size_final = 21
    x_label_font_size = AXIS_LABEL_SIZE
    legend_font_size = LEGEND_FONT_SIZE

    completion_indices = {}
    if len(x_vals) > 0:
        for key in PROTOCOLS.keys():
            if key not in df.columns:
                continue
            col_data = df.loc[mask, key].to_numpy()
            if col_data.size == 0:
                continue
            max_val = col_data.max()
            reach_max_indices = np.where(col_data >= max_val - 1)[0]
            if reach_max_indices.size > 0:
                completion_indices[key] = int(reach_max_indices[0])

    # ---------------------------------------------------------
    # 场景 A: PoW (吞吐量折线图，Deep. 单独分面)
    # ---------------------------------------------------------
    if network == 'pow':
        protocols_present = [k for k in PROTOCOLS.keys() if k in df.columns]
        pow_series = {}

        if df.loc[mask].empty:
            print(f"   [WARN] No data after bios cut for {network}")
            return

        df_masked = df.loc[mask].copy().reset_index(drop=True)
        df_masked['minute'] = (df_masked['time'] - bios_val) / SECONDS_PER_MINUTE
        df_masked['minute_bin'] = ((df_masked['time'] - bios_val) // SECONDS_PER_MINUTE).astype(int)

        for key in protocols_present:
            key_df = df_masked
            if key in completion_indices:
                stop_idx = completion_indices[key]
                key_df = df_masked.iloc[:stop_idx + 1].copy()

            grouped = key_df.groupby('minute_bin')
            x_plot = grouped['minute'].last().to_numpy()
            y_plot = ((grouped[key].last() - grouped[key].first()) / SECONDS_PER_MINUTE).clip(lower=0).to_numpy()

            if len(x_plot) == 0:
                continue
            pow_series[key] = dict(
                x=x_plot,
                y=y_plot,
                label=PROTOCOLS[key]['label'],
                color=PROTOCOLS[key]['color'],
                completion=(x_plot[-1], y_plot[-1]),
            )

        if len(pow_series) == 0:
            print(f"   [WARN] No protocol data for {network}")
            return

        combined_keys = [
            key for key in PROTOCOLS.keys()
            if key != POW_DEEP_KEY and key in pow_series
        ]
        panel_specs = []
        if combined_keys:
            panel_specs.append((combined_keys, ""))
        if POW_DEEP_KEY in pow_series:
            panel_specs.append(([POW_DEEP_KEY], ""))
        if not panel_specs:
            print(f"   [WARN] No grouped protocol data for {network}")
            return

        fig, axes = plt.subplots(
            len(panel_specs),
            1,
            figsize=DEFAULT_FIGSIZE,
            sharey=False,
            sharex=False,
            gridspec_kw={
                'hspace': POW_PANEL_HSPACE,
                'height_ratios': [
                    POW_DEEP_PANEL_HEIGHT_RATIO if keys == [POW_DEEP_KEY] else len(keys)
                    for keys, _axis_config in panel_specs
                ],
            },
        )
        axes = np.atleast_1d(axes)
        ax1 = axes[0]
        legend_handles = []
        legend_labels = []
        legend_bbox = (0.985, 0.965)
        legend_ncol = 2
        legend_font_size_final = POW_PANEL_LEGEND_FONT_SIZE

        for ax, (panel_keys, title) in zip(axes, panel_specs):
            group_max = 0.0
            group_x_max = 0.0
            panel_legend_handles = []
            panel_legend_labels = []
            for key in panel_keys:
                item = pow_series[key]
                zorder = 10 if key == 'committee' else 1
                alpha = 0.9 if key == 'committee' else 0.78
                lw = POW_LINE_WIDTH_FAST if key == 'committee' else POW_LINE_WIDTH_BASELINE
                line, = ax.plot(
                    item['x'],
                    item['y'],
                    label=item['label'],
                    color=item['color'],
                    linewidth=lw,
                    alpha=alpha,
                    zorder=zorder,
                )
                panel_legend_handles.append(line)
                panel_legend_labels.append(item['label'])

                finite_y = item['y'][np.isfinite(item['y'])]
                if finite_y.size > 0:
                    group_max = max(group_max, float(finite_y.max()))
                if key not in POW_RANGE_IGNORED_KEYS:
                    finite_x = item['x'][np.isfinite(item['x'])]
                    if finite_x.size > 0:
                        group_x_max = max(group_x_max, float(finite_x.max()))

                x0, y0 = item['completion']
                ax.vlines(
                    x=x0,
                    ymin=0,
                    ymax=y0,
                    colors=item['color'],
                    linewidth=POW_VLINE_WIDTH,
                    alpha=0.9,
                    zorder=6,
                )

            y_upper, y_step = get_nice_throughput_axis(group_max)
            x_upper, x_step = X_MAX_SECONDS / SECONDS_PER_MINUTE, X_TICK_MINUTES
            ax.set_xlim(0, x_upper)
            ax.xaxis.set_major_locator(MultipleLocator(x_step))
            ax.xaxis.set_major_formatter(FuncFormatter(format_time_to_min))
            ax.set_ylim(0, y_upper)
            y_tick_step = POW_DEEP_Y_TICK_STEP if panel_keys == [POW_DEEP_KEY] else POW_COMBINED_Y_TICK_STEP
            ax.yaxis.set_major_locator(MultipleLocator(y_tick_step))
            ax.yaxis.set_major_formatter(FuncFormatter(lambda value, pos: format_panel_tick(value)))
            ax.tick_params(axis='both', labelsize=POW_PANEL_TICK_LABEL_SIZE)
            ax.grid(True)
            if title:
                ax.text(
                    0.985,
                    0.82,
                    title,
                    transform=ax.transAxes,
                    fontsize=POW_PANEL_TITLE_SIZE,
                    ha='right',
                    va='center',
                    bbox=dict(facecolor='white', edgecolor='none', alpha=0.75, pad=1.5),
                )

            if panel_legend_handles:
                ax.legend(
                    panel_legend_handles,
                    panel_legend_labels,
                    loc='upper right',
                    ncol=2 if len(panel_legend_handles) > 1 else 1,
                    fontsize=legend_font_size_final,
                    frameon=True,
                    edgecolor='gray',
                    facecolor='white',
                    framealpha=0.85,
                )

        axes[-1].set_xlabel("Time (min)", fontsize=AXIS_LABEL_SIZE, labelpad=8)

        fig.text(
            0.055,
            0.50,
            "Throughput (TPS)",
            ha='center',
            va='center',
            rotation='vertical',
            fontsize=AXIS_LABEL_SIZE,
        )

        fig.subplots_adjust(**POW_BOXPLOT_MARGINS)

        x_label = ""
        x_label_font_size = AXIS_LABEL_SIZE

    # ---------------------------------------------------------
    # 场景 B: PoS (横向断轴 - 左右分割)
    # ---------------------------------------------------------
    else:
        fig, ax1 = plt.subplots(figsize=DEFAULT_FIGSIZE)
        x_label = ""
        x_label_font_size = POS_AXIS_LABEL_SIZE
        legend_font_size = POS_LEGEND_FONT_SIZE

        completion_points = {}
        for key, config in PROTOCOLS.items():
            if key in df_tps.columns:
                raw_tps = df_tps.loc[mask, key].rolling(window=20, min_periods=1).mean().to_numpy()
                x_arr = x_vals.to_numpy()

                if key in completion_indices:
                    stop_idx = completion_indices[key]
                    x_plot = x_arr[:stop_idx + 1]
                    y_plot = raw_tps[:stop_idx + 1]
                else:
                    x_plot = x_arr
                    y_plot = raw_tps
                
                zorder = 10 if key == 'committee' else 1
                alpha = 0.9 if key == 'committee' else 0.7
                lw = POS_LINE_WIDTH_FAST if key == 'committee' else POS_LINE_WIDTH_BASELINE

                ax1.plot(
                    x_plot,
                    y_plot,
                    label=config['label'],
                    color=config['color'],
                    linewidth=lw,
                    alpha=alpha,
                    zorder=zorder,
                )

                if len(x_plot) > 0:
                    completion_points[key] = (x_plot[-1], y_plot[-1])

        ax1.set_xlim(0, X_MAX_SECONDS / SECONDS_PER_MINUTE)
        ax1.set_xlabel("Time (min)", fontsize=POS_AXIS_LABEL_SIZE, labelpad=8)
        ax1.set_ylabel("Throughput (TPS)", fontsize=POS_AXIS_LABEL_SIZE)
        ax1.xaxis.set_major_locator(MultipleLocator(X_TICK_MINUTES))
        ax1.xaxis.set_major_formatter(FuncFormatter(format_time_to_min))
        ax1.tick_params(axis='both', labelsize=POS_TICK_LABEL_SIZE)
        ax1.grid(True)

        # 仅保留结束点的竖直向下线（按用户要求）
        for key, (x0, y0) in completion_points.items():
            line_color = PROTOCOLS[key]['color'] if key in PROTOCOLS else 'black'
            ax1.vlines(
                x=x0,
                ymin=0,
                ymax=y0,
                colors=line_color,
                linewidth=POS_VLINE_WIDTH,
                alpha=0.95,
                zorder=6,
            )

        # 恢复说明框与箭头（保持原样）
        box_pos = (0.45, 0.64)
        box_anchor_points = {
            'committee': (0.46, 0.67),
            'deepthought': (0.44, 0.77),
            'seenfeed': (0.42, 0.70),
            'decentruth': (0.46, 0.70),
            'daon': (0.35, 0.74),
        }
        fig.text(
            box_pos[0],
            box_pos[1],
            ANNOTATION_TEXT,
            transform=fig.transFigure,
            fontsize=POS_ANNOTATION_FONT_SIZE,
            color=ANNOTATION_TEXT_COLOR,
            ha='center',
            va='center',
            bbox=POS_ANNOTATION_BOX_STYLE,
        )

        # 仅保留一个结束圈注与一个箭头（优先 FastOracle）
        selected_key = 'committee' if 'committee' in completion_points else (next(iter(completion_points)) if completion_points else None)
        if selected_key is not None:
            x0, y0 = completion_points[selected_key]
            edge_color = PROTOCOLS[selected_key]['color'] if selected_key in PROTOCOLS else 'black'
            ax1.scatter(
                [x0], [y0],
                s=200,
                facecolors='none',
                edgecolors='black',
                linewidths=1.5,
                zorder=40,
            )
            ax1.scatter(
                [x0], [y0],
                s=24,
                c=edge_color,
                marker='o',
                linewidths=0,
                zorder=21,
            )

            arrow_target = box_anchor_points.get(selected_key, box_pos)
            arrow = ConnectionPatch(
                xyA=(x0, y0),
                coordsA='data',
                axesA=ax1,
                xyB=arrow_target,
                coordsB=fig.transFigure,
                arrowstyle='<-',
                color='black',
                lw=1.0,
                shrinkB=4,
            )
            fig.add_artist(arrow)

        fig.subplots_adjust(**POS_FIGURE_MARGINS)

    # ================= 统一图例修改 (全局右上角) =================
    
    # 从第一个子图中获取线条对象和标签
    if legend_handles is None or legend_labels is None:
        handles, labels = ax1.get_legend_handles_labels()
    else:
        handles, labels = legend_handles, legend_labels
    
    # 恢复为全局 fig.legend，并将位置微调向右
    if handles and labels:
        fig.legend(
            handles, 
            labels, 
            loc='upper right', 
            bbox_to_anchor=legend_bbox,
            ncol=legend_ncol, 
            fontsize=legend_font_size_final,
            frameon=True,
            edgecolor='gray',
            facecolor='white',
            framealpha=0.8
        )

    # 通用标签设置
    fig.text(0.5, 0.02, x_label, ha='center', va='center', fontsize=x_label_font_size)
    
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
