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
    "deepthought": {"label": "Deep.", "color": "#0088B2"},
    "seenfeed": {"label": "Sen.", "color": "#E69F00"},
    "decentruth": {"label": "DECEN.", "color": "#009E73"},
    "daon": {"label": "DAON", "color": "#56B4E9"},
}

# 样式配置 (保留原脚本高字号)
AXIS_LABEL_SIZE = 24
TICK_LABEL_SIZE = 20
LEGEND_FONT_SIZE = 14
DEFAULT_FIGSIZE = (8, 6)
SAVEFIG_KWARGS = {} 
FIGURE_MARGINS = dict(left=0.12, right=0.97, bottom=0.16, top=0.93)
POW_BOXPLOT_MARGINS = dict(left=0.24, right=0.96, bottom=0.16, top=0.96)
POW_PANEL_TITLE_SIZE = 20
POW_PANEL_TICK_LABEL_SIZE = 18
POS_FIGURE_MARGINS = dict(left=0.16, right=0.97, bottom=0.16, top=0.95)
POS_AXIS_LABEL_SIZE = 24
POS_TICK_LABEL_SIZE = 20
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
    # 场景 A: PoW (箱线图)
    # ---------------------------------------------------------
    if network == 'pow':
        protocols_present = [k for k in PROTOCOLS.keys() if k in df.columns]
        keys_used = []
        data_list = []
        labels = []
        colors = []

        if df.loc[mask].empty:
            print(f"   [WARN] No data after bios cut for {network}")
            return

        df_masked = df.loc[mask].copy().reset_index(drop=True)
        df_masked['minute_bin'] = ((df_masked['time'] - bios_val) // SECONDS_PER_MINUTE).astype(int)

        for key in protocols_present:
            key_df = df_masked
            if key in completion_indices:
                stop_idx = completion_indices[key]
                key_df = df_masked.iloc[:stop_idx + 1].copy()

            grp = key_df.groupby('minute_bin')[key]
            diff_per_min = grp.last() - grp.first()
            active_diff = diff_per_min[diff_per_min > 0]
            used_diff = active_diff if len(active_diff) > 0 else diff_per_min
            tps_per_min = (used_diff / SECONDS_PER_MINUTE).to_numpy()
            tps_per_min = tps_per_min[np.isfinite(tps_per_min) & (tps_per_min > 0)]
            if tps_per_min.size == 0:
                continue
            keys_used.append(key)
            data_list.append(tps_per_min)
            labels.append(PROTOCOLS[key]['label'])
            colors.append(PROTOCOLS[key]['color'])

        if len(data_list) == 0:
            print(f"   [WARN] No protocol data for {network}")
            return

        fig, axes = plt.subplots(
            len(data_list),
            1,
            figsize=DEFAULT_FIGSIZE,
            sharey=False,
            gridspec_kw={'hspace': 0.62},
        )
        axes = np.atleast_1d(axes)

        for idx, (ax, key, label, color, vals) in enumerate(zip(axes, keys_used, labels, colors, data_list)):
            bplot = ax.boxplot(
                [vals],
                vert=False,
                patch_artist=True,
                tick_labels=[""],
                showfliers=False,
                whis=(10, 90),
                showmeans=True,
                widths=0.75,
                meanprops=dict(marker='D', markerfacecolor='white', markeredgecolor='black', markersize=4),
                medianprops=dict(color='black', linewidth=1.6),
                boxprops=dict(linewidth=1.2),
                whiskerprops=dict(linewidth=1.2),
                capprops=dict(linewidth=1.2),
                flierprops=dict(marker='o', markersize=4, markeredgecolor='gray', alpha=0.8)
            )
            for patch in bplot['boxes']:
                patch.set_facecolor(color)
                patch.set_alpha(0.65)

            axis_config = POW_AXIS_CONFIG.get(key)
            if axis_config is None:
                x_min, x_max = np.nanpercentile(vals, [10, 90])
                x_min = float(x_min)
                x_max = float(x_max)
                if abs(x_max - x_min) < 1e-9:
                    x_min = float(np.nanmin(vals))
                    x_max = float(np.nanmax(vals))
                x_span = max(x_max - x_min, max(abs(x_max), 1.0) * 0.04)
                x_left = max(0, x_min - x_span * 0.12)
                x_right = x_max + x_span * 0.12
                tick_values = np.linspace(x_left, x_right, 4)
                ax.set_xlim(x_left, x_right)
                ax.set_xticks(tick_values)
                ax.set_xticklabels([format_panel_tick(v) for v in tick_values])
            else:
                ax.set_xlim(*axis_config["xlim"])
                ax.set_xticks(axis_config["ticks"])
                ax.set_xticklabels(axis_config["labels"])
            ax.set_ylabel(label, fontsize=POW_PANEL_TITLE_SIZE, rotation=0, labelpad=58, va='center')
            ax.tick_params(axis='x', labelsize=POW_PANEL_TICK_LABEL_SIZE)
            ax.tick_params(axis='y', left=False, labelleft=False)
            ax.grid(True, axis='x', linestyle='--', alpha=0.45)

        fig.text(0.5, 0.04, "Throughput (TPS)", ha='center', va='center', fontsize=AXIS_LABEL_SIZE)

        fig.subplots_adjust(**POW_BOXPLOT_MARGINS)

        legend_handles = []
        legend_labels = []
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
                s=90,
                facecolors='none',
                edgecolors='black',
                linewidths=1.4,
                zorder=20,
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
            bbox_to_anchor=(0.985, 0.93),
            ncol=1, 
            fontsize=21,
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
