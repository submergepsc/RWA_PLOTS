#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RWA-FastOracle 全景性能深度分析脚本 (8 图体系) - 字体修正版
"""

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import pandas as pd
import numpy as np
import os
import seaborn as sns

# ================= 全局配置区域 =================

PROTOCOLS = {
    'committee': {'label': 'Ours', 'color': '#1f77b4'},
    'daon': {'label': 'Daon', 'color': '#ff7f0e'},
    'decentruth': {'label': 'Decentruth', 'color': '#2ca02c'},
    'seenfeed': {'label': 'Seenfeed', 'color': '#d62728'},
    'deepthought': {'label': 'Deepthought', 'color': '#9467bd'}
}
<<<<<<< HEAD
# 队列衰减分析使用的最小队列阈值（降低以获取更多样本）
=======
>>>>>>> 9355776 (jfdk)
MIN_QUEUE_THRESHOLD = 50

# ================= 辅助函数区域 =================

def calculate_throughput(df_handled):
    """从累计处理数计算瞬时 TPS"""
    time_col = df_handled['time']
    df_tps = pd.DataFrame({'time': time_col})
    dt = time_col.diff().fillna(1.0).replace(0, 1e-9)
    
    for col in PROTOCOLS.keys():
        if col in df_handled.columns:
            dH = df_handled[col].diff().fillna(0)
            df_tps[col] = (dH / dt).clip(lower=0)
    return df_tps

def get_log_time(time_series, bios=550):
    """计算 log(t - bios)"""
    valid_mask = time_series > bios
    log_t = np.log(time_series[valid_mask] - bios)
    return log_t, valid_mask

# ================= Group 1: 队列长度 (Queue) =================

def plot_queue_log_dynamics(network: str, out_dir: str):
    """【图1】队列消减动力学图 (Log-Time)"""
<<<<<<< HEAD
    plt.rcParams.update({
        'font.family': 'sans-serif', 'font.sans-serif': ['Arial', 'DejaVu Sans'],
        'axes.unicode_minus': False, 'font.size': 18,
        'axes.labelsize': 20, 'axes.titlesize': 22,
        'xtick.labelsize': 24, 'ytick.labelsize': 24,
        'legend.fontsize': 20,
        'figure.figsize': (12, 8),
        'grid.linestyle': '--', 'grid.alpha': 0.6
    })
=======
    # 为当前绘图函数单独配置字号、字体与网格样式，避免影响其他图
    # --- 字体大小修正 ---
    plt.rcParams.update({
        'font.family': 'sans-serif', 'font.sans-serif': ['Arial', 'DejaVu Sans'],
        'axes.unicode_minus': False,
        'font.size': 14,
        'axes.labelsize': 32,         # 16 * 2
        'axes.titlesize': 18,
        'xtick.labelsize': 34,        # 14 * 2
        'ytick.labelsize': 34,
        'legend.fontsize': 32,       # 18 * 2
        'figure.figsize': (12, 9),
        'grid.linestyle': '--', 'grid.alpha': 0.6
    })
    
>>>>>>> 9355776 (jfdk)
    print(f"-> [1/8] Queue Log-Dynamics ({network})...")
    # 读取队列长度随时间变化的数据表，用于绘制排队长度曲线
    df = pd.read_csv(f"total_q_len_{network}.csv")
    plt.figure()
    
    bios_val = 550 if network == 'pow' else 0
<<<<<<< HEAD
=======
    # PoW 使用对数横轴，避免前期起伏太小；PoS 则保持线性时间轴
>>>>>>> 9355776 (jfdk)
    if network == 'pow':
        x_vals, mask = get_log_time(df['time'], bios=bios_val)
        x_label = f"Log Time (t > {bios_val})"
        title_suffix = " (Log Time)"
    else:
        mask = df['time'] >= bios_val
        x_vals = df.loc[mask, 'time'] - bios_val
        x_label = "Time (s)"
        title_suffix = ""
    
    for key, config in PROTOCOLS.items():
        if key in df.columns:
<<<<<<< HEAD
=======
            # 仅对符合掩码的时刻绘制队列长度，并突出我方协议的视觉权重
>>>>>>> 9355776 (jfdk)
            y_vals = df.loc[mask, key]
            zorder = 10 if key == 'committee' else 1
            lw = 4.0 if key == 'committee' else 2.5
            alpha = 1.0 if key == 'committee' else 0.8
<<<<<<< HEAD
            
            plt.plot(x_vals, y_vals, label=config['label'], color=config['color'],
                     linewidth=lw, alpha=alpha, zorder=zorder)

    plt.title(f"Queue Draining Dynamics{title_suffix}")
=======
            plt.plot(x_vals, y_vals, label=config['label'], color=config['color'],
                     linewidth=lw, alpha=alpha, zorder=zorder)

    # plt.title(f"Queue Draining Dynamics{title_suffix}")
>>>>>>> 9355776 (jfdk)
    plt.xlabel(x_label)
    plt.ylabel("Queue Length")
    plt.legend(loc='upper right')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "queue_log_dynamics.pdf"), format="pdf")
    plt.close()

def plot_queue_heatmap(network: str, out_dir: str):
<<<<<<< HEAD
    """【图2】队列积压热力图 (Strip Plot)"""
    # set_plot_style()
    # print(f"-> [2/8] Queue Backlog Strip Plot ({network})...")
    # df = pd.read_csv(f"total_q_len_{network}.csv")
    # plt.figure(figsize=(14, 6))
    # 
    # protocols = list(PROTOCOLS.keys())
    # y_positions = range(len(protocols))
    # 
    # for idx, key in enumerate(protocols):
    #     if key in df.columns:
    #         # 找出积压状态 (Queue > 0) 的时间段
    #         active_mask = df[key] > 10 # 容差
    #         active_times = df.loc[active_mask, 'time']
    #         
    #         if len(active_times) > 0:
    #             # 绘制条带，颜色深度可以代表积压量，这里简化为单一颜色条带表示"积压中"
    #             # 或者使用 scatter 绘制密集的点
    #             plt.scatter(active_times, [idx]*len(active_times), 
    #                         color=PROTOCOLS[key]['color'], marker='|', s=100, alpha=0.5)

    # plt.yticks(y_positions, [PROTOCOLS[p]['label'] for p in protocols])
    # plt.xlabel("Time (s)")
    # plt.title("Queue Backlog Duration (Active Period)")
    # plt.grid(axis='x', linestyle='--')
    # 
    # # 对 PoW 使用 Log Scale 如果时间太长
    # if network == 'pow':
    #     plt.xscale('log')
    #     plt.xlabel("Time (s) [Log Scale]")
    #     
    # plt.tight_layout()
    # plt.savefig(os.path.join(out_dir, "queue_backlog_strip.pdf"), format="pdf")
    # plt.close()
    pass

def plot_queue_decay_kde(network: str, out_dir: str):
    """
    【图3】队列衰减速率分布图 (Decay Rate KDE) with Broken X-Axis
    Splits the x-axis if 'Ours' is significantly faster than baselines.
    """
    plt.rcParams.update({
        'font.family': 'sans-serif', 'font.sans-serif': ['Arial', 'DejaVu Sans'],
        'axes.unicode_minus': False, 'font.size': 18,
        'axes.labelsize': 20, 'axes.titlesize': 22,
        'xtick.labelsize': 24, 'ytick.labelsize': 24,
        'legend.fontsize': 20,
        'figure.figsize': (12, 8),
        'grid.linestyle': '--', 'grid.alpha': 0.6
    })
    print(f"-> [3/8] Queue Decay Rate KDE ({network.upper()})...")
    
    try:
        df = pd.read_csv(f"total_q_len_{network}.csv")
    except FileNotFoundError:
        print(f"   [Error] File not found: total_q_len_{network}.csv")
        return

    # 1. Prepare Data
    decay_datasets = []
=======
    pass

def plot_queue_decay_kde(network: str, out_dir: str):
    """【图3】队列衰减速率分布图"""
    # 局部调整图形风格，使密度曲线在输出 PDF 上保持一致的字号
    # --- 字体大小修正 ---
    plt.rcParams.update({
        'font.family': 'sans-serif', 'font.sans-serif': ['Arial', 'DejaVu Sans'],
        'axes.unicode_minus': False,
        'font.size': 14,
        'axes.labelsize': 32,
        'axes.titlesize': 18,
        'xtick.labelsize': 28,
        'ytick.labelsize': 28,
        'legend.fontsize': 28,
        'figure.figsize': (12, 9),
        'grid.linestyle': '--', 'grid.alpha': 0.6
    })
    print(f"-> [3/8] Queue Decay Rate KDE ({network.upper()})...")
>>>>>>> 9355776 (jfdk)
    
    try:
        # 读取队列长度随时间的原始数据，用于估计衰减速率
        df = pd.read_csv(f"total_q_len_{network}.csv")
    except FileNotFoundError:
        print(f"   [Error] File not found: total_q_len_{network}.csv")
        return

    decay_datasets = []
    for key, config in PROTOCOLS.items():
        if key in df.columns:
<<<<<<< HEAD
            # Filter for active draining phase (> 100 items in queue)
=======
            # 仅保留队列长度较大时的片段，避免噪声影响衰减速率估计
>>>>>>> 9355776 (jfdk)
            mask = df[key] > 100
            if mask.sum() < 10: continue
            q_series = df.loc[mask, key]
            t_series = df.loc[mask, 'time']
<<<<<<< HEAD
            
            # Calculate Rate: -dQ / dt
            # Note: We use abs() to ensure positive rates for draining
            decay_rate = -q_series.diff() / t_series.diff()
            decay_rate = decay_rate.replace([np.inf, -np.inf], np.nan).dropna()
            
            # Filter noise: only keep significant draining rates > 1 req/s
            decay_rate = decay_rate[decay_rate > 1.0]
            
            if decay_rate.empty: continue
            decay_datasets.append((key, decay_rate, config))

    if not decay_datasets:
        print("   [Warn] No valid decay samples found.")
        return

    # 2. Check for Outlier (Broken Axis Condition, only for non-PoW)
=======
            # 衰减速率定义为队列长度下降量与时间间隔之比，并过滤异常值
            decay_rate = -q_series.diff() / t_series.diff()
            decay_rate = decay_rate.replace([np.inf, -np.inf], np.nan).dropna()
            decay_rate = decay_rate[decay_rate > 1.0]
            if decay_rate.empty: continue
            decay_datasets.append((key, decay_rate, config))

    if not decay_datasets: return

    # 统计各协议衰减速率的最大值，用于判断是否需要断轴展示
>>>>>>> 9355776 (jfdk)
    max_rates = [d.max() for _, d, _ in decay_datasets]
    global_max = max(max_rates)
    sorted_max = sorted(max_rates)
    second_max = sorted_max[-2] if len(sorted_max) > 1 else global_max
    need_break = (len(sorted_max) > 1) and (global_max > second_max * 3)

<<<<<<< HEAD
    # 3. Setup Plots
    if network == 'pow':
        fig, ax = plt.subplots(figsize=(12, 7))
=======
    if network == 'pow':
        fig, ax = plt.subplots(figsize=(12, 10))
>>>>>>> 9355776 (jfdk)
        axes = [ax]
        ax.set_xlim(0, 600)
        ax.set_ylim(0, 0.05)
        need_break = False
    elif need_break:
        fig, (ax_left, ax_right) = plt.subplots(
<<<<<<< HEAD
            1, 2, sharey=True, figsize=(12, 7),
=======
            1, 2, sharey=True, figsize=(12, 10),
>>>>>>> 9355776 (jfdk)
            gridspec_kw={'width_ratios': [3, 1], 'wspace': 0.05}
        )
        axes = [ax_left, ax_right]
        ax_left.set_xlim(0, second_max * 1.5)
        ax_right.set_xlim(global_max * 0.8, global_max * 1.1)
        ax_left.spines['right'].set_visible(False)
        ax_right.spines['left'].set_visible(False)
        ax_right.yaxis.tick_right()
        ax_right.tick_params(labelright=False, left=False)

        d = 0.015
        kwargs = dict(transform=ax_left.transAxes, color='k', clip_on=False)
        ax_left.plot((1 - d, 1 + d), (-d, +d), **kwargs)
        ax_left.plot((1 - d, 1 + d), (1 - d, 1 + d), **kwargs)
        kwargs.update(transform=ax_right.transAxes)
        ax_right.plot((-d, +d), (-d, +d), **kwargs)
        ax_right.plot((-d, +d), (1 - d, 1 + d), **kwargs)
    else:
<<<<<<< HEAD
        fig, ax = plt.subplots(figsize=(12, 7))
        axes = [ax]
        ax.set_xlim(left=0)

    # 4. Plot KDE
    for ax_curr in axes:
        for key, rates, config in decay_datasets:
            try:
                sns.kdeplot(
                    data=rates, 
                    color=config['color'], 
                    fill=True, 
                    alpha=0.1, 
                    linewidth=2.5, 
                    ax=ax_curr,
                    label=config['label'],
                    warn_singular=False
                )
            except: pass

    # 5. Labels & Legend
        if network == 'pow':
            handles, labels = axes[0].get_legend_handles_labels()
            by_label = dict(zip(labels, handles))
            axes[0].legend(by_label.values(), by_label.keys(), loc='upper right')
            axes[0].set_xlabel("Decay Rate (Requests / s)")
        elif need_break:
            handles, labels = axes[0].get_legend_handles_labels()
            by_label = dict(zip(labels, handles))
            axes[0].legend(by_label.values(), by_label.keys(), loc='upper right')
            axes[0].set_xlabel("Decay Rate (Requests / s)")
            axes[1].set_xlabel("")
        else:
            axes[0].legend(loc='upper right')
            axes[0].set_xlabel("Decay Rate (Requests / s)")
=======
        fig, ax = plt.subplots(figsize=(12, 10))
        axes = [ax]
        ax.set_xlim(left=0)

    for ax_curr in axes:
        for key, rates, config in decay_datasets:
            try:
                # 使用 KDE 平滑衰减速率分布，帮助比较各协议的尾部行为
                sns.kdeplot(
                    data=rates, color=config['color'], fill=True, alpha=0.1, 
                    linewidth=2.5, ax=ax_curr, label=config['label'], warn_singular=False
                )
            except: pass

    if network == 'pow':
        handles, labels = axes[0].get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        axes[0].legend(by_label.values(), by_label.keys(), loc='upper right')
        axes[0].set_xlabel("Decay Rate (Requests / s)")
    elif need_break:
        handles, labels = axes[0].get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        axes[0].legend(by_label.values(), by_label.keys(), loc='upper right')
        axes[0].set_xlabel("Decay Rate (Requests / s)")
        axes[1].set_xlabel("")
    else:
        axes[0].legend(loc='upper right')
        axes[0].set_xlabel("Decay Rate (Requests / s)")
>>>>>>> 9355776 (jfdk)

    axes[0].set_ylabel("Density")
    for ax in axes:
        ax.grid(True, axis='y', linestyle='--', alpha=0.5)

<<<<<<< HEAD
    plt.suptitle(f"Queue Decay Rate Distribution ({network.upper()})", y=0.96)
    
=======
    # plt.suptitle(f"Queue Decay Rate Distribution ({network.upper()})", y=0.96)
>>>>>>> 9355776 (jfdk)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "queue_decay_kde.pdf")
    plt.savefig(out_path, format="pdf")
    plt.close()
    print(f"   [OK] Saved: {out_path}")

<<<<<<< HEAD
# ================= Group 2: 吞吐量 (Throughput) =================
 
def plot_throughput_stability(network: str, out_dir: str):
    """
    【图4】吞吐量稳定性分析
    优化点：
    1. PoW 模式：使用【Y轴断轴】（Broken Axis），解决 Ours 峰值过高压缩其他曲线的问题。
    2. PoS 模式：保持原样，普通线性展示。
    """
    # 基础样式设置
    plt.rcParams.update({
        'font.family': 'sans-serif', 'font.sans-serif': ['Arial', 'DejaVu Sans'],
        'axes.unicode_minus': False, 'font.size': 18,
        'axes.labelsize': 20, 'axes.titlesize': 22,
        'xtick.labelsize': 24, 'ytick.labelsize': 24,
        'legend.fontsize': 20,
=======
# ================= Group 2: 吞吐量 (Throughput) ================= 

def plot_throughput_stability(network: str, out_dir: str):
    """【图4】吞吐量稳定性分析 (双重断轴版)"""
    # 为吞吐量曲线配置局部样式，以保持不同网络输出的一致性
    # --- 字体大小修正 ---
    plt.rcParams.update({
        'font.family': 'sans-serif', 'font.sans-serif': ['Arial', 'DejaVu Sans'],
        'axes.unicode_minus': False,
        'font.size': 14,
        'axes.labelsize': 32,
        'axes.titlesize': 18,
        'xtick.labelsize': 28,
        'ytick.labelsize': 28,
        'legend.fontsize': 28,
>>>>>>> 9355776 (jfdk)
        'figure.figsize': (12, 8),
        'grid.linestyle': '--', 'grid.alpha': 0.6
    })
    
    print(f"-> [4/8] Throughput Stability ({network})...")
    # 读取累计处理请求数，并转换为瞬时 TPS 序列
    df = pd.read_csv(f"total_handled_num_{network}.csv")
<<<<<<< HEAD
    df_tps = calculate_throughput(df) # 假设外部有此函数

    # --- 数据准备 ---
    bios_val = 550 if network == 'pow' else 0
    mask = df_tps['time'] > bios_val
    x_vals = df_tps.loc[mask, 'time'] - bios_val
    x_label = "Time (s)"

    # ==========================
    # 分支 1：PoW 使用断轴优化
    # ==========================
    if network == 'pow':
        # 创建两个共享X轴的子图，上下排列
        # height_ratios=[1, 3] 让下半部分（细节区）占更多高度
        fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(12, 8),
                                       gridspec_kw={'height_ratios': [1, 3]})
        fig.subplots_adjust(hspace=0.1)  # 调整两个图之间的间距

        for key, config in PROTOCOLS.items():
            if key in df_tps.columns:
                raw_tps = df_tps.loc[mask, key]
                rolling_mean = raw_tps.rolling(window=20, min_periods=1).mean()
                
                zorder = 10 if key == 'committee' else 1
                alpha = 0.9 if key == 'committee' else 0.7
                lw = 3.0
                
                # 在上下两个图上各画一遍
                ax1.plot(x_vals, rolling_mean, label=config['label'], color=config['color'],
                         linewidth=lw, alpha=alpha, zorder=zorder)
                ax2.plot(x_vals, rolling_mean, label=config['label'], color=config['color'],
                         linewidth=lw, alpha=alpha, zorder=zorder)

        # --- 针对 PoW 的关键范围设置 ---
        # 根据 image_ffecf4.jpg 观察：Ours 峰值约 350，稳定后<50
        ax1.set_ylim(250, 400)  # 上半图：只看 250 TPS 以上的高峰
        ax2.set_ylim(-2, 60)    # 下半图：只看 0-60 TPS 的细节
        
        # 隐藏边框，制造“断开”的视觉效果
        ax1.spines['bottom'].set_visible(False)
        ax2.spines['top'].set_visible(False)
        ax1.tick_params(labeltop=False, bottom=False)  # 上图不显示x刻度
        ax2.xaxis.tick_bottom()

        # 绘制断裂线（斜线标志）
        d = .015 
        kwargs = dict(transform=ax1.transAxes, color='k', clip_on=False)
        ax1.plot((-d, +d), (-d, +d), **kwargs)        # 上图左下
        ax1.plot((1 - d, 1 + d), (-d, +d), **kwargs)  # 上图右下
        kwargs.update(transform=ax2.transAxes)
        ax2.plot((-d, +d), (1 - d, 1 + d), **kwargs)  # 下图左上
        ax2.plot((1 - d, 1 + d), (1 - d, 1 + d), **kwargs)  # 下图右上

        # 设置标签
        ax1.set_title(f"Throughput Stability")
        ax1.legend(loc='upper right')
        ax2.set_ylabel("Throughput (TPS)")
        ax2.yaxis.set_label_coords(-0.08, 0.5, transform=ax2.transAxes) # Y轴标签居中
        ax2.set_xlabel(x_label)
        
        # PoW 也可以开启网格
        ax1.grid(True)
        ax2.grid(True)

    # ==========================
    # 分支 2：PoS 使用普通绘图（保持原样）
    # ==========================
    else:
        plt.figure()
        for key, config in PROTOCOLS.items():
            if key in df_tps.columns:
                raw_tps = df_tps.loc[mask, key]
                rolling_mean = raw_tps.rolling(window=20, min_periods=1).mean()
                zorder = 10 if key == 'committee' else 1
                plt.plot(x_vals, rolling_mean, label=config['label'], color=config['color'],
                         linewidth=3.0, alpha=0.9 if key=='committee' else 0.7, zorder=zorder)
        
        plt.title(f"Throughput Stability")
        plt.xlabel(x_label)
        plt.ylabel("Throughput (TPS)")
        plt.legend(loc='upper right')
        plt.grid(True)

    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "throughput_stability.pdf"), format="pdf")
    print("Done.")
=======
    df_tps = calculate_throughput(df) 

    bios_val = 550 if network == 'pow' else 0
    # 滤除预热阶段数据并对时间轴做平移，使不同网络对齐
    mask = df_tps['time'] > bios_val
    x_vals = df_tps.loc[mask, 'time'] - bios_val
    x_label = "Time (s)"

    # PoW
    if network == 'pow':
        fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(12, 8),
                                       gridspec_kw={'height_ratios': [1, 6]})
        fig.subplots_adjust(hspace=0.05) 

        for key, config in PROTOCOLS.items():
            if key in df_tps.columns:
                # 使用滑动平均削弱瞬时波动，让长期趋势更易比较
                raw_tps = df_tps.loc[mask, key]
                rolling_mean = raw_tps.rolling(window=20, min_periods=1).mean()
                zorder = 10 if key == 'committee' else 1
                alpha = 0.9 if key == 'committee' else 0.7
                lw = 3.0
                ax1.plot(x_vals, rolling_mean, label=config['label'], color=config['color'],
                         linewidth=lw, alpha=alpha, zorder=zorder)
                ax2.plot(x_vals, rolling_mean, label=config['label'], color=config['color'],
                         linewidth=lw, alpha=alpha, zorder=zorder)

        ax1.set_ylim(250, 400)  
        ax2.set_ylim(-2, 60)    
        ax2.set_xlim(left=0, right=22000)

        ax1.spines['bottom'].set_visible(False)
        ax2.spines['top'].set_visible(False)
        ax1.tick_params(labeltop=False, bottom=False)
        ax2.xaxis.tick_bottom()

        d = .015 
        kwargs = dict(transform=ax1.transAxes, color='k', clip_on=False)
        ax1.plot((-d, +d), (-d, +d), **kwargs)        
        ax1.plot((1 - d, 1 + d), (-d, +d), **kwargs)  
        kwargs.update(transform=ax2.transAxes)
        ax2.plot((-d, +d), (1 - d, 1 + d), **kwargs)  
        ax2.plot((1 - d, 1 + d), (1 - d, 1 + d), **kwargs)

        # ax1.set_title(f"Throughput Stability")
        # --- 修正：之前建议把 PoW 的图例移到下方 ax2，这里保留原逻辑，但改一下位置防止遮挡 ---
        # 如果上方空间太窄，还是建议放在下方；这里我用 loc='upper right' 放在下方子图
        ax2.legend(loc='upper right') 
        
        ax2.set_ylabel("Throughput (TPS)")
        ax2.yaxis.set_label_coords(-0.08, 0.5, transform=ax2.transAxes)
        ax2.set_xlabel(x_label)
        ax1.grid(True)
        ax2.grid(True)
        plt.tight_layout()
        plt.subplots_adjust(hspace=0.05)

    # PoS
    else:
        fig, (ax1, ax2) = plt.subplots(1, 2, sharey=True, figsize=(12, 8),
                                       gridspec_kw={'width_ratios': [4, 1]})
        fig.subplots_adjust(wspace=0.05)

        for key, config in PROTOCOLS.items():
            if key in df_tps.columns:
                raw_tps = df_tps.loc[mask, key]
                rolling_mean = raw_tps.rolling(window=20, min_periods=1).mean()
                zorder = 10 if key == 'committee' else 1
                alpha = 0.9 if key == 'committee' else 0.7
                lw = 3.0
                # 左右拆分时间轴，使后期偶发波动可以放大观察
                ax1.plot(x_vals, rolling_mean, label=config['label'], color=config['color'],
                         linewidth=lw, alpha=alpha, zorder=zorder)
                ax2.plot(x_vals, rolling_mean, label=config['label'], color=config['color'],
                         linewidth=lw, alpha=alpha, zorder=zorder)
        
        ax1.set_xlim(0, 22000)
        if len(x_vals) > 0:
            total_time = x_vals.max()
            if total_time > 27000:
                ax2.set_xlim(total_time - 5000, total_time+500)

        ax1.spines['right'].set_visible(False)
        ax2.spines['left'].set_visible(False)
        ax1.tick_params(labelright=False, right=False)
        ax2.tick_params(labelleft=False, left=False)   
        ax2.yaxis.tick_right() 
        ax2.tick_params(right=False) 

        d = .015 
        kwargs = dict(transform=ax1.transAxes, color='k', clip_on=False)
        ax1.plot((1 - d, 1 + d), (-d, +d), **kwargs) 
        ax1.plot((1 - d, 1 + d), (1 - d, 1 + d), **kwargs) 

        kwargs.update(transform=ax2.transAxes)
        ax2.plot((-d, +d), (-d, +d), **kwargs) 
        ax2.plot((-d, +d), (1 - d, 1 + d), **kwargs) 

        # fig.suptitle(f"Throughput Stability", y=0.95, fontsize=18) # 标题稍微调小
        ax1.set_ylabel("Throughput (TPS)")
        ax1.set_xlabel(x_label)
        ax2.set_xlabel(x_label)
        ax2.legend(loc='upper right')
        
        ax1.grid(True)
        ax2.grid(True)
        plt.tight_layout()
        plt.subplots_adjust(wspace=0.05, top=0.9)

    save_path = os.path.join(out_dir, "throughput_stability.pdf")
    plt.savefig(save_path, format="pdf")
    print(f"Saved to {save_path}")
>>>>>>> 9355776 (jfdk)
    plt.close()



def plot_throughput_violin(network: str, out_dir: str):
    """【图5】吞吐量统计分布图 (Violin)"""
<<<<<<< HEAD
    plt.rcParams.update({
        'font.family': 'sans-serif', 'font.sans-serif': ['Arial', 'DejaVu Sans'],
        'axes.unicode_minus': False, 'font.size': 18,
        'axes.labelsize': 20, 'axes.titlesize': 22,
        'xtick.labelsize': 24, 'ytick.labelsize': 24,
        'legend.fontsize': 20,
=======
    # 调整图形风格，便于直接输出到论文级别的图表
    # --- 字体大小修正 ---
    plt.rcParams.update({
        'font.family': 'sans-serif', 'font.sans-serif': ['Arial', 'DejaVu Sans'],
        'axes.unicode_minus': False,
        'font.size': 14,
        'axes.labelsize': 32,
        'axes.titlesize': 18,
        'xtick.labelsize': 28,
        'ytick.labelsize': 28,
        'legend.fontsize': 28,
>>>>>>> 9355776 (jfdk)
        'figure.figsize': (12, 8),
        'grid.linestyle': '--', 'grid.alpha': 0.6
    })
    print(f"-> [5/8] Throughput Violin ({network})...")
    # 读取总处理数并换算成 TPS 分布，便于比较各协议稳定性
    df = pd.read_csv(f"total_handled_num_{network}.csv")
    df_tps = calculate_throughput(df)
    
    plot_data = []
    bios_val = 550 if network == 'pow' else 0
    # 过滤掉预热阶段，并排除极低 TPS 的噪声样本
    valid_indices = df_tps['time'] > bios_val
    
    for col in PROTOCOLS.keys():
        if col in df_tps.columns:
            vals = df_tps.loc[valid_indices, col]
            vals = vals[vals > 0.1]
            
            if len(vals) > 0:
                # 抽样限制最大数据量，避免绘图时内存占用过大
                if len(vals) > 3000: vals = vals.sample(3000)
                temp_df = pd.DataFrame({'TPS': vals, 'Protocol': PROTOCOLS[col]['label']})
                plot_data.append(temp_df)
    
    if not plot_data: return
    long_df = pd.concat(plot_data)

    plt.figure()
    # 小提琴图展示分布形状，并通过配色对应协议身份
    sns.violinplot(x='Protocol', y='TPS', data=long_df, inner="quartile",
                   palette=[p['color'] for p in PROTOCOLS.values() if p['label'] in long_df['Protocol'].unique()],
                   alpha=0.4, linewidth=1.5)
    
    # plt.title("Throughput Performance Distribution")
    plt.ylabel("TPS")
    plt.xlabel("")
    plt.grid(axis='y', linestyle='--')
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "throughput_violin.pdf"), format="pdf")
    plt.close()

def plot_cumulative_workload(network: str, out_dir: str):
<<<<<<< HEAD
    """【图6】累积工作量堆叠图 (Cumulative Area)"""
    # set_plot_style()
    # print(f"-> [6/8] Cumulative Workload Area ({network})...")
    # df = pd.read_csv(f"total_handled_num_{network}.csv")
    # plt.figure()
    # 
    # # 归一化处理: 计算百分比 (0-100%)
    # # 假设 max handled 是总请求数
    # max_req = 20000 
    # 
    # bios_val = 550 if network == 'pow' else 0
    # valid_mask = df['time'] > bios_val
    # times = df.loc[valid_mask, 'time']
    # 
    # # 对 PoW 使用 Log Time
    # if network == 'pow':
    #     plot_x = np.log(times - bios_val)
    #     xlabel = f"Log Time (t > {bios_val})"
    # else:
    #     plot_x = times
    #     xlabel = "Time (s)"

    # for key, config in PROTOCOLS.items():
    #     if key in df.columns:
    #         # 转换为百分比
    #         y_vals = (df.loc[valid_mask, key] / max_req) * 100
    #         
    #         # 绘制填充面积图
    #         plt.fill_between(plot_x, y_vals, alpha=0.1, color=config['color'])
    #         plt.plot(plot_x, y_vals, label=config['label'], color=config['color'], linewidth=2.5)

    # plt.title("Cumulative Workload Progress")
    # plt.xlabel(xlabel)
    # plt.ylabel("Completion Percentage (%)")
    # plt.ylim(0, 105)
    # plt.legend(loc='lower right')
    # plt.grid(True)
    # plt.tight_layout()
    # plt.savefig(os.path.join(out_dir, "cumulative_workload.pdf"), format="pdf")
    # plt.close()
=======
>>>>>>> 9355776 (jfdk)
    pass

# ================= Group 3: 证书生成 (Certificate) =================

def plot_cert_burst_scatter(network: str, out_dir: str):
    """【图7】证书生成脉冲散点图 (Burst Scatter)"""
<<<<<<< HEAD
    plt.rcParams.update({
        'font.family': 'sans-serif', 'font.sans-serif': ['Arial', 'DejaVu Sans'],
        'axes.unicode_minus': False, 'font.size': 18,
        'axes.labelsize': 20, 'axes.titlesize': 22,
        'xtick.labelsize': 24, 'ytick.labelsize': 24,
        'legend.fontsize': 20,
=======
    # 针对证书生成事件配置绘图风格，便于凸显密度和阈值差异
    # --- 字体大小修正 ---
    plt.rcParams.update({
        'font.family': 'sans-serif', 'font.sans-serif': ['Arial', 'DejaVu Sans'],
        'axes.unicode_minus': False,
        'font.size': 14,
        'axes.labelsize': 32,
        'axes.titlesize': 18,
        'xtick.labelsize': 28,
        'ytick.labelsize': 28,
        'legend.fontsize': 28,
>>>>>>> 9355776 (jfdk)
        'figure.figsize': (12, 8),
        'grid.linestyle': '--', 'grid.alpha': 0.6
    })
    print(f"-> [7/8] Certificate Burst Scatter ({network})...")
    
    # 为不同网络单独设置证书生成阈值，保证散点具有可见密度
    BATCH_SIZE =2 if network=='pow' else 5
    df = pd.read_csv(f"total_handled_num_{network}.csv")
    
    plt.figure(figsize=(14, 6))
    protocols = list(PROTOCOLS.keys())
    
    for idx, key in enumerate(protocols):
        if key in df.columns:
            # 利用累计处理数的增量估计证书数量，筛选出爆发时刻
            new_reqs = df[key].diff().fillna(0)
            new_certs = (new_reqs // BATCH_SIZE).astype(int)
            burst_mask = new_certs > 0
            burst_times = df.loc[burst_mask, 'time']
            burst_sizes = new_certs[burst_mask]
            
            if len(burst_times) > 0:
                # 使用散点大小编码一次爆发中生成的证书数，纵轴区别协议
                plt.scatter(burst_times, [idx]*len(burst_times), 
                            s=burst_sizes*5, 
                            color=PROTOCOLS[key]['color'], 
                            alpha=0.6, label=PROTOCOLS[key]['label'])

    plt.yticks(range(len(protocols)), [PROTOCOLS[p]['label'] for p in protocols])
    plt.xlabel("Time (s)")
    # plt.title("Certificate Generation Bursts (Micro-View)")
    
    if network == 'pow':
        plt.xscale('log')
        plt.xlabel("Time (s) [Log Scale]")
        
    plt.grid(True, axis='x', which='both', linestyle='--')
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "cert_burst_scatter.pdf"), format="pdf")
    plt.close()

def plot_cert_inter_arrival_cdf(network: str, out_dir: str):
    """【图8】证书生成间隔 CDF (Inter-Arrival Time)"""
<<<<<<< HEAD
    plt.rcParams.update({
        'font.family': 'sans-serif', 'font.sans-serif': ['Arial', 'DejaVu Sans'],
        'axes.unicode_minus': False, 'font.size': 18,
        'axes.labelsize': 20, 'axes.titlesize': 22,
        'xtick.labelsize': 24, 'ytick.labelsize': 24,
        'legend.fontsize': 20,
=======
    # 调整图形参数，使累积分布在成图时保持高可读性
    # --- 字体大小修正 ---
    plt.rcParams.update({
        'font.family': 'sans-serif', 'font.sans-serif': ['Arial', 'DejaVu Sans'],
        'axes.unicode_minus': False,
        'font.size': 14,
        'axes.labelsize': 32,
        'axes.titlesize': 18,
        'xtick.labelsize': 28,
        'ytick.labelsize': 28,
        'legend.fontsize': 28,
>>>>>>> 9355776 (jfdk)
        'figure.figsize': (12, 8),
        'grid.linestyle': '--', 'grid.alpha': 0.6
    })
    print(f"-> [8/8] Certificate Inter-Arrival CDF ({network})...")
    
    BATCH_SIZE = 15
    df = pd.read_csv(f"total_handled_num_{network}.csv")
    plt.figure()
    
    for key, config in PROTOCOLS.items():
        if key in df.columns:
            # 通过请求增量估计证书批次，并获取每次批次的发生时间
            new_reqs = df[key].diff().fillna(0)
            burst_mask = new_reqs >= BATCH_SIZE
            burst_times = df.loc[burst_mask, 'time']
            
            if len(burst_times) > 1:
                # 计算相邻爆发的时间间隔，并绘制成累积分布以比较稳定性
                intervals = burst_times.diff().dropna()
                data = np.sort(intervals)
                cdf = np.arange(1, len(data) + 1) / len(data)
                plt.plot(data, cdf, label=config['label'], color=config['color'], linewidth=2.5)

    # plt.title("Certificate Inter-Arrival Time CDF")
    plt.xlabel("Inter-Arrival Time (s)")
    plt.ylabel("Cumulative Probability")
    plt.xscale('log')
    plt.legend(loc='lower right')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "cert_inter_arrival_cdf.pdf"), format="pdf")
    plt.close()

# ================= 主程序入口 =================

def main():
    networks = ['pow', 'pos']
    
    for network in networks:
        base_dir = f"figs_{network}_basic3"
        queue_dir = os.path.join(base_dir, "queue")
        throughput_dir = os.path.join(base_dir, "throughput")
        certificate_dir = os.path.join(base_dir, "certificate")
        for path in (queue_dir, throughput_dir, certificate_dir):
            os.makedirs(path, exist_ok=True)
        
        print(f"\n{'='*20} Processing {network.upper()} (8-Chart System) {'='*20}")
        
        # Group 1: Queue
        plot_queue_log_dynamics(network, queue_dir)
        plot_queue_heatmap(network, queue_dir)
        plot_queue_decay_kde(network, queue_dir)
        
        # Group 2: Throughput
        plot_throughput_stability(network, throughput_dir)
        plot_throughput_violin(network, throughput_dir)
        plot_cumulative_workload(network, throughput_dir)
        
        # Group 3: Certificate
        plot_cert_burst_scatter(network, certificate_dir)
        plot_cert_inter_arrival_cdf(network, certificate_dir)
        
        print(f"Queue charts -> {queue_dir}")
        print(f"Throughput charts -> {throughput_dir}")
        print(f"Certificate charts -> {certificate_dir}")

if __name__ == "__main__":
    main()
