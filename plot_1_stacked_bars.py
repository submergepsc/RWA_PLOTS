#!/usr/bin/env python3
# -*- coding: utf-8 -*- 
# Plot 1: RWA-FastOracle 基础堆叠柱状图 (Time Breakdown)

import os
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
from typing import Dict

# ================= 全局配置区域 =================

DATA_DIR = "." 
FIGURES_ROOT = "figures"
PLOT_TYPE_NAME = "01_breakdown"

# 定义方案及其对应颜色
PROTOCOLS: Dict[str, Dict[str, str]] = {
    "committee": {"label": "FastOracle", "color": "#1f77b4"},
    "deepthought": {"label": "Deep.", "color": "#9467bd"},
    "seenfeed": {"label": "Sen.", "color": "#d62728"},
    "decentruth": {"label": "DECEN.", "color": "#2ca02c"},
    "daon": {"label": "DAON", "color": "#ff7f0e"},
}

SAVEFIG_KWARGS = {"bbox_inches": "tight", "pad_inches": 0.05}

# ================= 数据处理 =================

def clean_time_data(series: pd.Series) -> pd.Series:
    extracted = series.astype(str).str.extract(r"^(\d+\.?\d*)\s*(ms|s|ns)?$")
    values = pd.to_numeric(extracted[0], errors="coerce").fillna(0.0)
    units = extracted[1]
    factor = np.ones(len(values))
    factor[units == "ms"] = 0.001
    factor[units == "ns"] = 1e-9
    return values * factor

def load_metric(metric: str, network: str) -> pd.DataFrame:
    filename = f"{metric}_{network}.csv"
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f"[Error] Data file not found: {path}")
    return pd.read_csv(path)

# ================= 绘图核心逻辑 =================

def plot_stacked_time_bars(network: str, out_dir: str) -> None:
    # 样式配置
    local_style = {
        "font.family": "sans-serif",
        "font.sans-serif": ["DejaVu Sans", "Arial"],
        "axes.unicode_minus": False,
        "grid.linestyle": "--",
        "grid.alpha": 0.4,
        "font.size": 28,
        "axes.labelsize": 32,
        "xtick.labelsize": 24,
        "ytick.labelsize": 24,
    
        "legend.fontsize": 22, 
        "figure.figsize": (12, 8),
        "hatch.linewidth": 0.7,  # 全局控制纹理线条的粗细
    }

    print(f"-> Processing {network.upper()} stacked bars...")

    with plt.rc_context(local_style):
        try:
            search_df = load_metric("searchTime", network)
            consensus_df = load_metric("consensusTime", network)
            onchain_df = load_metric("onChainTime", network)
        except FileNotFoundError as e:
            print(e)
            return

        # --- 数据聚合 ---
        bars = []
        labels = []
        current_colors = [] 
            
        for key, cfg in PROTOCOLS.items():
            if key in search_df.columns:
                s = clean_time_data(search_df[key]).mean()
                c = clean_time_data(consensus_df[key]).mean()
                o = clean_time_data(onchain_df[key]).mean()
                bars.append((s, c, o))
                labels.append(cfg["label"])
                current_colors.append(cfg["color"])

        if not bars: 
            print("   No valid data found.")
            return

        bars_arr = np.array(bars)
        y = np.arange(len(labels))
        shadow_total = bars_arr.sum(axis=1) 
        
        sorted_vals = np.sort(shadow_total)
        max_val = sorted_vals[-1]
        second_val = sorted_vals[-2] if len(sorted_vals) > 1 else max_val

        # --- 内部绘图函数 ---
        def draw_bars_on_ax(ax, *, show_labels=False):
            # 阴影底色 (灰色背景条，辅助对齐)
            ax.barh(y, shadow_total, color="black", alpha=0.05, height=0.6, zorder=1)
            
            left = np.zeros(len(labels))
            # 纹理定义
            hatches = ["//", "\\\\", "xx"] 
            
            for idx in range(3):
                ax.barh(
                    y, 
                    bars_arr[:, idx], 
                    left=left, 
                    color=current_colors, 
                    hatch=hatches[idx],   
                    edgecolor="black",    # 【关键修改】改为黑色边框
                    linewidth=0.7,        # 线宽适中
                    alpha=0.9,            # 颜色透明度，防止太深看不清黑色纹理
                    height=0.6, 
                    zorder=2,
                )
                left += bars_arr[:, idx]

            ax.set_ylim(-0.6, len(labels) - 0.4)
            ax.grid(axis="x", linestyle="--", alpha=0.5, zorder=0)
            ax.set_yticks(y)
            ax.set_yticklabels(labels if show_labels else [""] * len(labels))

        # --- 场景分支 ---
        if network == 'pow':
            fig, (ax_left, ax_right) = plt.subplots(
                1, 2, sharey=False,
                gridspec_kw={"width_ratios": [3, 1], "wspace": 0.03},
            )
            draw_bars_on_ax(ax_left, show_labels=True)
            draw_bars_on_ax(ax_right, show_labels=False)
            ax_right.set_ylim(ax_left.get_ylim())
            ax_left.set_xlim(0, second_val * 1.2)
            ax_right.set_xlim(max_val * 0.75, max_val * 1.05)
            
            ax_left.spines["right"].set_visible(False)
            ax_right.spines["left"].set_visible(False)
            ax_right.tick_params(labelleft=True, left=False)
            


            # 断轴标记
            d = 0.024
            kwargs = dict(transform=ax_left.transAxes, color="k", clip_on=False)
            ax_left.plot((1-d/3,1+d/3), (-d, +d), **kwargs)
            ax_left.plot((1 - d/3, 1 + d/3), (1 - d, 1 + d), **kwargs)
            # d1=3*d
            kwargs.update(transform=ax_right.transAxes)
            ax_right.plot((-d, +d), (-d, +d), **kwargs)
            ax_right.plot((-d, +d), (1 - d, 1 + d), **kwargs)

        else:
            fig, ax = plt.subplots()
            draw_bars_on_ax(ax, show_labels=True)
            ax.set_xlim(0, max_val * 1.15) 

        # --- 图例处理 ---
        
        # 1. 方案图例 (Bottom Right)
        scheme_handles = []
        for cfg in PROTOCOLS.values():
            # 这里不需要hatch，只要展示颜色块
            patch = mpatches.Patch(facecolor=cfg["color"], edgecolor='black', linewidth=0.5, label=cfg["label"])
            scheme_handles.append(patch)
            
        # 2. 阶段图例 (Top Center)
        breakdown_labels = ["Search", "Consensus", "On-chain"]
        breakdown_hatches = ["//", "\\\\", "xx"]
        breakdown_handles = []
        for h_pat, label_text in zip(breakdown_hatches, breakdown_labels):
            # 白底黑纹，黑色边框
            patch = mpatches.Patch(
                facecolor='white', 
                edgecolor='black', 
                hatch=h_pat, 
                label=label_text
            )
            breakdown_handles.append(patch)
        
        # 根据网络设置图例参数 
        
        bbox_anchor = (0.90, 0.88) if network == 'pow' else (0.94, 0.86)
        fig.legend(
            handles=breakdown_handles,
            loc='upper right', 
            bbox_to_anchor=bbox_anchor,
            ncol=1,
            frameon=True,              
            facecolor='white',
            framealpha=1.0,
            edgecolor='black',
            fontsize=26
        )

        # 轴标签

        if network == 'pow':
            fig.text(0.04, 0.5, "Protocol", va="center", rotation="vertical", fontsize=local_style["axes.labelsize"])
            fig.text(0.5, 0.04, "Time (s)", ha="center", fontsize=local_style["axes.labelsize"])
            plt.subplots_adjust(left=0.20, right=0.96, bottom=0.18, top=0.92, wspace=0.03)

        else:
            fig.text(0.04, 0.5, "Protocol", va="center", rotation="vertical", fontsize=local_style["axes.labelsize"])
            fig.text(0.5, 0.04, "Time (s)", ha="center", fontsize=local_style["axes.labelsize"])
            plt.subplots_adjust(left=0.20, right=0.96, bottom=0.18, top=0.92)

        save_filename = f"stacked_breakdown_{network}.pdf"
        save_path = os.path.join(out_dir, save_filename)

        plt.savefig(save_path, format="pdf", **SAVEFIG_KWARGS)
        plt.close()
        print(f"   [OK] Saved: {save_path}")

if __name__ == "__main__":
    target_dir = os.path.join(FIGURES_ROOT, PLOT_TYPE_NAME)
    os.makedirs(target_dir, exist_ok=True)
    
    print(f"=== Starting Plotting Routine: {PLOT_TYPE_NAME} ===")
    networks = ["pos", "pow"]
    for net in networks:
        plot_stacked_time_bars(net, target_dir)
    print("=== Done ===")
