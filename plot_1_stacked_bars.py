#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plot 1: RWA-FastOracle 基础堆叠柱状图 (Time Breakdown)
对应文件夹: figures/01_breakdown/
说明: 生成 pos 和 pow 的堆叠图并保存在同一目录下
"""

import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from typing import Dict

# ================= 全局配置区域 =================

# 数据文件存放的目录 (如果是当前目录请用 ".")
DATA_DIR = "." 

# 图片输出的总根目录
FIGURES_ROOT = "figures"

# 本脚本对应的子文件夹名称
PLOT_TYPE_NAME = "01_breakdown"


PROTOCOLS: Dict[str, Dict[str, str]] = {
    "committee": {"label": "Ours", "color": "#1f77b4"},
    "daon": {"label": "Daon", "color": "#ff7f0e"},
    "decentruth": {"label": "Decentruth", "color": "#2ca02c"},
    "seenfeed": {"label": "Seenfeed", "color": "#d62728"},
    "deepthought": {"label": "Deepthought", "color": "#9467bd"},
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
        "legend.fontsize": 24,
        "figure.figsize": (12, 8),
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

        # 数据聚合
        bars = []
        labels = []
        for key, cfg in PROTOCOLS.items():
            if key in search_df.columns:
                s = clean_time_data(search_df[key]).mean()
                c = clean_time_data(consensus_df[key]).mean()
                o = clean_time_data(onchain_df[key]).mean()
                bars.append((s, c, o))
                labels.append(cfg["label"])

        if not bars: 
            print("   No valid data found.")
            return

        bars_arr = np.array(bars)
        y = np.arange(len(labels))
        shadow_total = bars_arr.sum(axis=1) 
        
        sorted_vals = np.sort(shadow_total)
        max_val = sorted_vals[-1]
        second_val = sorted_vals[-2] if len(sorted_vals) > 1 else max_val

        # 内部绘图函数
        def draw_bars_on_ax(ax, *, show_labels=False):
            ax.barh(y, shadow_total, color="black", alpha=0.05, height=0.6, zorder=1)
            left = np.zeros(len(labels))
            names = ["Search", "Consensus", "On-chain"]
            colors = ["#6baed6", "#9ecae1", "#c6dbef"]
            hatches = ["//", "\\\\", "xx"]

            for idx in range(3):
                ax.barh(
                    y, bars_arr[:, idx], left=left, color=colors[idx],
                    hatch=hatches[idx], edgecolor="black", linewidth=1.0, alpha=0.9,
                    height=0.6, label=names[idx] if show_labels else None, zorder=2,
                )
                left += bars_arr[:, idx]

            ax.set_ylim(-0.6, len(labels) - 0.4)
            ax.grid(axis="x", linestyle="--", alpha=0.5, zorder=0)
            ax.set_yticks(y)
            ax.set_yticklabels(labels if show_labels else [""] * len(labels))

        # 场景 A: PoW (断轴)
        if network == 'pow':
            fig, (ax_left, ax_right) = plt.subplots(
                1, 2, sharey=True,
                gridspec_kw={"width_ratios": [3, 1], "wspace": 0.05},
            )
            draw_bars_on_ax(ax_left, show_labels=True)
            draw_bars_on_ax(ax_right, show_labels=False)

            ax_left.set_xlim(0, second_val * 1.2)
            ax_right.set_xlim(max_val * 0.75, max_val * 1.05)

            ax_left.spines["right"].set_visible(False)
            ax_right.spines["left"].set_visible(False)
            ax_right.tick_params(labelleft=False, left=False)

            d = 0.015
            kwargs = dict(transform=ax_left.transAxes, color="k", clip_on=False)
            ax_left.plot((1 - d, 1 + d), (-d, +d), **kwargs)
            ax_left.plot((1 - d, 1 + d), (1 - d, 1 + d), **kwargs)
            kwargs.update(transform=ax_right.transAxes)
            ax_right.plot((-d, +d), (-d, +d), **kwargs)
            ax_right.plot((-d, +d), (1 - d, 1 + d), **kwargs)

            axes = [ax_left, ax_right]
            fig.text(0.04, 0.5, "Protocol", va="center", rotation="vertical", fontsize=local_style["axes.labelsize"])

        # 场景 B: PoS (普通)
        else:
            fig, ax = plt.subplots()
            draw_bars_on_ax(ax, show_labels=True)
            ax.set_xlim(0, max_val * 1.15) 
            axes = [ax]

        handles, stack_labels = axes[0].get_legend_handles_labels()
        fig.legend(handles, stack_labels, loc="lower right", bbox_to_anchor=(0.95, 0.2), frameon=True, framealpha=0.9)

        if network == 'pow':
            fig.text(0.5, 0.04, "Time (s)", ha="center", fontsize=local_style["axes.labelsize"])
            plt.tight_layout(rect=[0.10, 0.12, 0.96, 0.92])
        else:
            fig.text(0.06, 0.5, "Protocol", va="center", rotation="vertical", fontsize=local_style["axes.labelsize"])
            fig.text(0.5, 0.04, "Time (s)", ha="center", fontsize=local_style["axes.labelsize"])
            plt.tight_layout(rect=[0.01, 0.1, 0.98, 0.95])

        # 【核心修改】：直接保存到 out_dir，文件名包含 network
        save_filename = f"stacked_breakdown_{network}.pdf"
        save_path = os.path.join(out_dir, save_filename)
        
        plt.savefig(save_path, format="pdf", **SAVEFIG_KWARGS)
        plt.close()
        print(f"   [OK] Saved: {save_path}")

# ================= 运行入口 =================

if __name__ == "__main__":
    # 拼接目标路径：figures/01_breakdown
    target_dir = os.path.join(FIGURES_ROOT, PLOT_TYPE_NAME)
    
    # 确保目标文件夹存在
    os.makedirs(target_dir, exist_ok=True)
    
    print(f"=== Starting Plotting Routine: {PLOT_TYPE_NAME} ===")
    print(f"Target Directory: {target_dir}")
    
    networks = ["pos", "pow"]
    
    for net in networks:
        # 这里的 target_dir 已经是最终的文件夹，不再往下分层
        plot_stacked_time_bars(net, target_dir)
        
    print("=== Done ===")