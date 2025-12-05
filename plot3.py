#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RWA-FastOracle 基础堆叠柱状图生成脚本 (修复断轴版)
"""

import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from typing import Dict

# ================= 全局配置区域 =================

PROTOCOLS: Dict[str, Dict[str, str]] = {
    "committee": {"label": "Ours", "color": "#1f77b4"},
    "daon": {"label": "Daon", "color": "#ff7f0e"},
    "decentruth": {"label": "Decentruth", "color": "#2ca02c"},
    "seenfeed": {"label": "Seenfeed", "color": "#d62728"},
    "deepthought": {"label": "Deepthought", "color": "#9467bd"},
}

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
    path = f"{metric}_{network}.csv"
    if not os.path.exists(path):
        raise FileNotFoundError(f"Data file not found: {path}")
    return pd.read_csv(path)

def calculate_throughput(df_handled: pd.DataFrame) -> pd.DataFrame:
    """Derive instantaneous TPS from cumulative handled counts."""
    time_col = df_handled["time"]
    df_tps = pd.DataFrame({"time": time_col})
    dt = time_col.diff().fillna(1.0).replace(0, 1e-9)

    for col in PROTOCOLS.keys():
        if col in df_handled.columns:
            dH = df_handled[col].diff().fillna(0)
            df_tps[col] = (dH / dt).clip(lower=0)
    return df_tps

def get_log_time(time_series: pd.Series, bios: float = 550) -> tuple[np.ndarray, pd.Series]:
    """Return log(time - bios) and mask for time > bios."""
    mask = time_series > bios
    shifted = (time_series[mask] - bios).clip(lower=1e-9)
    log_t = np.log(shifted)
    return log_t, mask

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
        "figure.figsize": (10, 8) if network == 'pow' else (10, 6),
    }

    print(f"-> Processing {network.upper()} stacked bars...")
    os.makedirs(out_dir, exist_ok=True)

    with plt.rc_context(local_style):
        # 1. 简化数据加载 (假设文件一定存在)
        search_df = load_metric("searchTime", network)
        consensus_df = load_metric("consensusTime", network)
        onchain_df = load_metric("onChainTime", network)

        # 2. 数据预处理
        bars = []
        labels = []
        for key, cfg in PROTOCOLS.items():
            if key in search_df.columns:
                s = clean_time_data(search_df[key]).mean()
                c = clean_time_data(consensus_df[key]).mean()
                o = clean_time_data(onchain_df[key]).mean()
                bars.append((s, c, o))
                labels.append(cfg["label"])

        if not bars: return

        bars_arr = np.array(bars)
        x = np.arange(len(labels))
        shadow_total = bars_arr.sum(axis=1) # 总高度，用于画灰色背景
        
        # 排序用于计算断轴范围
        sorted_vals = np.sort(shadow_total)
        max_val = sorted_vals[-1]
        second_val = sorted_vals[-2] if len(sorted_vals) > 1 else max_val

        # 通用绘图核心函数
        def draw_bars_on_ax(ax, show_legend=False):
            # 灰色背景
            ax.bar(x, shadow_total, color="black", alpha=0.05, width=0.6, zorder=1)
            
            bottom = np.zeros(len(labels))
            names = ["Search", "Consensus", "On-chain"]
            colors = ["#6baed6", "#9ecae1", "#c6dbef"]
            hatches = ["//", "\\\\", "xx"]
            
            for idx in range(3):
                ax.bar(x, bars_arr[:, idx], bottom=bottom, color=colors[idx],
                       hatch=hatches[idx], edgecolor="black", linewidth=1.0, alpha=0.9, width=0.6,
                       label=names[idx] if show_legend else None, zorder=2)
                bottom += bars_arr[:, idx]
            
            ax.set_xlim(-0.6, len(labels) - 0.4)
            ax.grid(axis='y', linestyle='--', alpha=0.5, zorder=0)

        # ==========================================
        # 场景 A: PoW (启用断轴)
        # ==========================================
        if network == 'pow':
            fig, (ax_top, ax_bottom) = plt.subplots(2, 1, sharex=True, 
                                                  gridspec_kw={"height_ratios": [1, 3], "hspace": 0.05})
            
            # 上下分别画图
            draw_bars_on_ax(ax_top, show_legend=True)
            draw_bars_on_ax(ax_bottom, show_legend=False)

            # 设置断轴范围
            ax_top.set_ylim(max_val * 0.7, max_val * 1.05)  # 顶部只显示最大值的顶部
            ax_bottom.set_ylim(0, second_val * 1.1)        # 底部显示其他较小值

            # 隐藏边框制造断裂感
            ax_top.spines["bottom"].set_visible(False)
            ax_bottom.spines["top"].set_visible(False)
            ax_top.tick_params(bottom=False, labelbottom=False) # 上图无X刻度
            
            # 绘制断裂线 (斜杠)
            d = 0.015
            kwargs = dict(transform=ax_top.transAxes, color="k", clip_on=False)
            ax_top.plot((-d, +d), (-d, +d), **kwargs)        
            ax_top.plot((1 - d, 1 + d), (-d, +d), **kwargs)  
            kwargs.update(transform=ax_bottom.transAxes)
            ax_bottom.plot((-d, +d), (1 - d, 1 + d), **kwargs)  
            ax_bottom.plot((1 - d, 1 + d), (1 - d, 1 + d), **kwargs)

            # 底部设置标签
            ax_bottom.set_xticks(x)
            ax_bottom.set_xticklabels(labels, rotation=20, ha="right")
            # ax_bottom.set_xlabel("Protocol")
            ax_top.legend(loc="upper left", framealpha=0.9) # 图例放在上图
            
            # 公共Y轴标签
            fig.text(0.02, 0.5, "Time (s)", va="center", rotation="vertical", fontsize=local_style["axes.labelsize"])

        # ==========================================
        # 场景 B: PoS (单轴，无标签)
        # ==========================================
        else:
            fig, ax = plt.subplots()
            draw_bars_on_ax(ax, show_legend=True) # PoS也显示图例
            
            ax.set_ylim(0, max_val * 1.15)
            ax.set_ylabel("Time (s)")
            ax.set_xticks(x)
            ax.set_xticklabels(labels, rotation=20, ha="right")
            
            ax.legend(loc="upper left")

        plt.tight_layout()
        if network == 'pow':
            fig.subplots_adjust(top=0.95, left=0.12) # 为Y轴标题留空
        
        save_path = os.path.join(out_dir, "stacked_time_bars.pdf")
        plt.savefig(save_path, format="pdf")
        plt.close()
        print(f"   [OK] Saved: {save_path}")

def plot_latency_stability(metric: str, network: str, out_dir: str, window: int = 50) -> None:
    """Generate rolling mean + variance stability plot with doubled typography."""
    local_style = {
        "font.family": "sans-serif",
        "font.sans-serif": ["DejaVu Sans", "Arial"],
        "axes.unicode_minus": False,
        "grid.linestyle": "--",
        "grid.alpha": 0.4,
        "figure.figsize": (12, 8),
        "font.size": 32,
        "axes.labelsize": 36,
        "axes.titlesize": 40,
        "xtick.labelsize": 28,
        "ytick.labelsize": 28,
        "legend.fontsize": 28,
    }

    with plt.rc_context(local_style):

        csv_file = f"{metric}_{network}.csv"
        if not os.path.exists(csv_file):
            print(f"-> Skip stability plot, missing file: {csv_file}")
            return

        df = pd.read_csv(csv_file)
        if "seqId" not in df.columns:
            print(f"-> Skip stability plot, seqId missing in {csv_file}")
            return

        rolling_data = {}
        max_vals = []

        for key, cfg in PROTOCOLS.items():
            if key not in df.columns:
                continue

            vals = clean_time_data(df[key])
            series = pd.Series(vals)
            rolling_mean = series.rolling(window=window).mean()
            rolling_std = series.rolling(window=window).std()

            if rolling_mean.dropna().empty:
                continue

            rolling_data[key] = (rolling_mean, rolling_std, cfg)
            max_vals.append(float(rolling_mean.max()))

        if not rolling_data:
            return

        max_val = max(max_vals)
        sorted_max = sorted(max_vals)
        second_max = sorted_max[-2] if len(sorted_max) > 1 else max_val
        need_break = (len(sorted_max) > 1) and (max_val > second_max * 3)

        tick_size = local_style["xtick.labelsize"]
        x_tick_size = tick_size
        x_label_size = local_style["axes.labelsize"]
        legend_size = local_style["legend.fontsize"]

        if need_break:
            fig, (ax_top, ax_bottom) = plt.subplots(
                2,
                1,
                sharex=True,
                figsize=(12, 8),
                gridspec_kw={"height_ratios": [1, 3], "hspace": 0.05},
            )
            axes_list = [ax_top, ax_bottom]
        else:
            fig, ax = plt.subplots(figsize=(12, 7))
            axes_list = [ax]

        for ax in axes_list:
            for key, (r_mean, r_std, cfg) in rolling_data.items():
                ax.plot(
                    df["seqId"],
                    r_mean,
                    label=cfg["label"],
                    color=cfg["color"],
                    linewidth=2.5,
                )
                ax.fill_between(
                    df["seqId"],
                    r_mean - r_std,
                    r_mean + r_std,
                    color=cfg["color"],
                    alpha=0.15,
                )
            ax.tick_params(axis="x", labelsize=x_tick_size)
            ax.tick_params(axis="y", labelsize=tick_size)
            ax.grid(True, linestyle="--", alpha=0.6)

        if need_break:
            ax_top.set_ylim(max_val * 0.85, max_val * 1.05)
            ax_bottom.set_ylim(0, second_max * 1.5)

            ax_top.spines["bottom"].set_visible(False)
            ax_bottom.spines["top"].set_visible(False)
            ax_top.xaxis.tick_top()
            ax_top.tick_params(labeltop=False)
            ax_bottom.xaxis.tick_bottom()

            d = 0.01
            kwargs = dict(transform=ax_top.transAxes, color="k", clip_on=False)
            ax_top.plot((-d, +d), (-d, +d), **kwargs)
            ax_top.plot((1 - d, 1 + d), (-d, +d), **kwargs)
            kwargs.update(transform=ax_bottom.transAxes)
            ax_bottom.plot((-d, +d), (1 - d, 1 + d), **kwargs)
            ax_bottom.plot((1 - d, 1 + d), (1 - d, 1 + d), **kwargs)

            ax_top.legend(loc="upper right", frameon=True, framealpha=0.9, fontsize=legend_size)
            ax_bottom.set_xlabel("Sequence ID", fontsize=x_label_size)
            fig.text(0.04, 0.5, "Average Latency (s)", va="center", rotation="vertical", fontsize=x_label_size)
        else:
            axes_list[0].set_xlabel("Sequence ID", fontsize=x_label_size)
            axes_list[0].set_ylabel("Average Latency (s)", fontsize=x_label_size)
            axes_list[0].legend(loc="upper left", fontsize=legend_size)

        title_map = {
            "consensusTime": "Consensus Time",
            "onChainTime": "On-Chain Time",
            "searchTime": "Search Time",
        }
        # plt.suptitle(
        #     f"{title_map.get(metric, metric)} Stability (Rolling Mean={window}) [{network.upper()}]",
        #     y=0.95,
        # )

        out_path = os.path.join(out_dir, f"{metric}_stability.pdf")
        plt.savefig(out_path, format="pdf")
        plt.close()
        print(f"   [OK] Stability plot saved: {out_path}")
# ================= 运行入口 =================

if __name__ == "__main__":
    networks = ["pos", "pow"]
    for net in networks:
        # 假设数据在这个目录下，您可以根据实际情况修改
        out_dir = f"figs_{net}_basic3" 
        plot_stacked_time_bars(net, out_dir)
        plot_latency_stability("consensusTime", net, out_dir, window=50)
        # plot_queue_suite(net, out_dir)
        # plot_throughput_suite(net, out_dir)
        # plot_certificate_suite(net, out_dir)
