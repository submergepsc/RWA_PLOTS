#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RWA-FastOracle 高级性能分析图表生成脚本
(基于 Queue Length, Throughput, Cert Speed 的深度可视化)
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
import seaborn as sns

# ================= 全局配置区域 =================

# 统一的协议名称、颜色和图例标签 (保持与 plot_comparison.py 完全一致)
PROTOCOLS = {
    'committee': {'label': 'Ours', 'color': '#1f77b4'},
    'daon': {'label': 'Daon', 'color': '#ff7f0e'},
    'decentruth': {'label': 'Decentruth', 'color': '#2ca02c'},
    'seenfeed': {'label': 'Seenfeed', 'color': '#d62728'},
    'deepthought': {'label': 'Deepthought', 'color': '#9467bd'}
}

# 输出目录
OUT_DIR_POW = "figs_pow_advanced"

# ================= 数据处理辅助函数 =================

def calculate_throughput(df_handled):
    """
    从累计处理数 (Cumulative Handled) 计算瞬时吞吐量 (TPS)
    TPS_t = (Handled_t - Handled_{t-1}) / (Time_t - Time_{t-1})
    """
    # 假设第一列是 time
    time_col = df_handled['time']
    df_tps = pd.DataFrame({'time': time_col})
    
    # 计算时间差 (dt)
    dt = time_col.diff().fillna(1.0) # 防止除以0，第一帧设为1
    dt = dt.replace(0, 1e-9) # 防止时间戳重复导致除以0
    
    for col in PROTOCOLS.keys():
        if col in df_handled.columns:
            # 计算处理数差 (dH)
            dH = df_handled[col].diff().fillna(0)
            # 计算 TPS
            df_tps[col] = dH / dt
            
            # 数据清洗：去除异常大的尖峰（可能是初始化导致的）或负值
            df_tps[col] = df_tps[col].clip(lower=0)
            
    return df_tps

def get_log_time(time_series, bios=550):
    """
    生成对数时间轴，复现 PDF 中的逻辑: log(t - bios)
    """
    # 过滤掉小于 bios 的时间点，防止 log 报错
    valid_mask = time_series > bios
    # 计算 log time
    log_t = np.log(time_series[valid_mask] - bios)
    return log_t, valid_mask

# ================= 绘图函数区域 =================

def plot_queue_log_dynamics(network: str, out_dir: str):
    """
    1. 队列消减动力学图 (Queue Draining Dynamics - Log Time)
    实质性分析: 使用对数时间轴展示 RWA-FastOracle 的"断崖式"高效处理能力。
    """
    # 局部样式配置 (保持一致)
    plt.rcParams.update({
        'font.family': 'sans-serif', 'font.sans-serif': ['Arial', 'DejaVu Sans', 'SimHei'],
        'axes.unicode_minus': False, 'font.size': 18,
        'axes.labelsize': 20, 'axes.titlesize': 22,
        'xtick.labelsize': 28, 'ytick.labelsize': 28,
        'legend.fontsize': 24, # 图例字体
        'figure.figsize': (12, 8),
        'grid.linestyle': '--', 'grid.alpha': 0.6
    })
    
    print(f"-> 正在生成 Queue Log-Dynamics ({network.upper()})...")
    df = pd.read_csv(f"total_q_len_{network}.csv")
    
    plt.figure()
    
    bios_val = 550 # 偏移量，根据 PDF 设定
    
    for key, config in PROTOCOLS.items():
        if key in df.columns:
            # 获取 Log Time
            log_t, mask = get_log_time(df['time'], bios=bios_val)
            y_vals = df.loc[mask, key]
            
            # 样式逻辑: 突出显示 Ours (Committee)
            if key == 'committee':
                lw, ls, alpha, zorder = 4.0, '-', 1.0, 10
            else:
                lw, ls, alpha, zorder = 2.5, '-', 0.8, 1
            
            plt.plot(log_t, y_vals, 
                     label=config['label'], color=config['color'],
                     linewidth=lw, linestyle=ls, alpha=alpha, zorder=zorder)

    plt.title(f"Queue Draining Dynamics (Log Time)")
    plt.xlabel(f"Log Time (t > {bios_val})")
    plt.ylabel("Queue Length")
    plt.legend(loc='upper right')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "queue_log_dynamics.pdf"), format="pdf")
    plt.close()

def plot_throughput_stability(network: str, out_dir: str, window=20):
    """
    2. 吞吐量稳定性分析图 (Throughput Stability with Rolling Mean)
    实质性分析: 展示瞬时吞吐量的波动性与平均趋势，证明系统的稳健性。
    """
    # 局部样式配置
    plt.rcParams.update({
        'font.family': 'sans-serif', 'font.sans-serif': ['Arial', 'DejaVu Sans', 'SimHei'],
        'axes.unicode_minus': False, 'font.size': 18,
        'axes.labelsize': 20, 'axes.titlesize': 22,
        'xtick.labelsize': 28, 'ytick.labelsize': 28,
        'legend.fontsize': 24,
        'figure.figsize': (12, 8),
        'grid.linestyle': '--', 'grid.alpha': 0.6
    })
    
    print(f"-> 正在生成 Throughput Stability ({network.upper()})...")
    df_handled = pd.read_csv(f"total_handled_num_{network}.csv")
    df_tps = calculate_throughput(df_handled)
    
    plt.figure()
    
    bios_val = 550
    # 获取 Log Time (用于 X 轴，使得前期的高吞吐不被压缩)
    log_t, mask = get_log_time(df_tps['time'], bios=bios_val)
    
    for key, config in PROTOCOLS.items():
        if key in df_tps.columns:
            raw_tps = df_tps.loc[mask, key]
            
            # 计算滑动平均
            rolling_mean = raw_tps.rolling(window=window, min_periods=1).mean()
            
            # 仅绘制 'committee' 和两个对比项以避免图表过于混乱，或者绘制全部
            # 这里绘制全部，但利用透明度
            
            if key == 'committee':
                zorder = 10
                # 绘制阴影误差带 (可选: 使用 std)
                # rolling_std = raw_tps.rolling(window=window).std().fillna(0)
                # plt.fill_between(log_t, rolling_mean - rolling_std, rolling_mean + rolling_std, color=config['color'], alpha=0.2)
            else:
                zorder = 1
            
            # 绘制平滑曲线
            plt.plot(log_t, rolling_mean, 
                     label=config['label'], color=config['color'],
                     linewidth=3.0, alpha=0.9, zorder=zorder)
            
            # 可选: 在背景中绘制原始数据的淡色轨迹，展示真实波动
            # plt.plot(log_t, raw_tps, color=config['color'], linewidth=1, alpha=0.15, zorder=zorder-1)

    plt.title(f"Throughput Stability (Log Time)")
    plt.xlabel(f"Log Time (t > {bios_val})")
    plt.ylabel("Throughput (TPS)")
    plt.legend(loc='upper right')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "throughput_stability.pdf"), format="pdf")
    plt.close()

def plot_throughput_violin(network: str, out_dir: str):
    """
    3. 吞吐量/证书生成速度 统计分布图 (Violin Plot)
    实质性分析: 统计 TPS 的分布。如果 Ours 的图形呈"倒三角"或"上宽下窄"，说明大部分时间维持高性能。
    这也是"证书生成速度"的一种侧面反映 (CertSpeed ~= TPS / BatchSize)。
    """
    plt.rcParams.update({
        'font.family': 'sans-serif', 'font.sans-serif': ['Arial', 'DejaVu Sans', 'SimHei'],
        'axes.unicode_minus': False, 'font.size': 18,
        'axes.labelsize': 20, 'axes.titlesize': 22,
        'xtick.labelsize': 24, # Protocol names
        'ytick.labelsize': 24,
        'figure.figsize': (12, 8),
        'grid.linestyle': '--', 'grid.alpha': 0.6
    })
    
    print(f"-> 正在生成 Throughput/Cert Speed Distribution ({network.upper()})...")
    df_handled = pd.read_csv(f"total_handled_num_{network}.csv")
    df_tps = calculate_throughput(df_handled)
    
    # 重塑数据用于 Seaborn
    plot_data = []
    bios_val = 550 if network=='pow' else 0

    valid_indices = df_tps['time'] > bios_val # 只统计开始运行后的阶段
    
    for col in PROTOCOLS.keys():    
        if col in df_tps.columns:
            # 获取有效阶段的 TPS
            vals = df_tps.loc[valid_indices, col]
            # 过滤掉 0 值 (队列排空后的数据) 以免拉低平均值，只看"工作状态"的性能
            vals = vals[vals > 0.1] 
            
            if len(vals) > 0:
                # 下采样以提高绘图速度
                if len(vals) > 3000: vals = vals.sample(3000)
                temp_df = pd.DataFrame({'TPS': vals, 'Protocol': PROTOCOLS[col]['label']})
                plot_data.append(temp_df)
    
    if not plot_data: return
    long_df = pd.concat(plot_data)

    plt.figure()
    
    # 绘制小提琴图
    sns.violinplot(x='Protocol', y='TPS', data=long_df, 
                   inner="quartile", # 显示四分位数线
                   hue='Protocol', legend=False,
                   palette=[p['color'] for p in PROTOCOLS.values() if p['label'] in long_df['Protocol'].unique()],
                   alpha=0.4, linewidth=1.5)
    
    plt.title(f"Throughput Performance Distribution")
    plt.ylabel("Transactions Per Second (TPS)")
    plt.xlabel("")
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "throughput_violin_dist.pdf"), format="pdf")
    plt.close()

def plot_completion_race_bar(network: str, out_dir: str):
    """
    4. 任务完成时间竞赛图 (Completion Time Horizontal Bar)
    实质性分析: 直观对比各协议处理完所有请求所需的总时间。
    """
    plt.rcParams.update({
        'font.family': 'sans-serif', 'font.sans-serif': ['Arial', 'DejaVu Sans'],
        'axes.unicode_minus': False, 'font.size': 18,
        'axes.labelsize': 20, 'axes.titlesize': 22,
        'xtick.labelsize': 24, 
        'ytick.labelsize': 24,
        'figure.figsize': (12, 7),
        'grid.linestyle': '--', 'grid.alpha': 0.6
    })
    
    print(f"-> 正在生成 Completion Time Race ({network.upper()})...")
    df_q = pd.read_csv(f"total_q_len_{network}.csv")
    
    completion_times = {}
    
    for key in PROTOCOLS.keys():
        if key in df_q.columns:
            # 找到队列长度首次归零的时间，或者最小值的时间
            # 假设队列最后会变为0
            zero_indices = df_q.index[df_q[key] <= 100].tolist() # 容差100
            if zero_indices:
                first_zero_idx = zero_indices[0]
                time_val = df_q.loc[first_zero_idx, 'time']
                completion_times[key] = time_val
            else:
                # 如果没归零，取最大时间
                completion_times[key] = df_q['time'].max()
    
    if not completion_times: return

    # 排序：时间短的在上面
    sorted_items = sorted(completion_times.items(), key=lambda x: x[1], reverse=True)
    labels = [PROTOCOLS[k]['label'] for k, v in sorted_items]
    times = [v for k, v in sorted_items]
    colors = [PROTOCOLS[k]['color'] for k, v in sorted_items]
    
    plt.figure()
    
    # 绘制水平条形图
    bars = plt.barh(labels, times, color=colors, alpha=0.8, edgecolor='black')
    
    plt.xlabel("Total Time to Drain Queue (s)")
    plt.title("Task Completion Speed Comparison")
    
    # 在条形图末尾添加数值
    for bar in bars:
        width = bar.get_width()
        plt.text(width * 1.02, bar.get_y() + bar.get_height()/2, 
                 f'{width:.1f} s', 
                 va='center', ha='left', fontsize=18, fontweight='bold')
    
    # 如果差距太大，使用 Log 轴
    if max(times) / (min(times) + 1e-5) > 50:
        plt.xscale('log')
        plt.xlabel("Total Time to Drain Queue (s) [Log Scale]")
    
    plt.xlim(right=max(times)*1.2) # 留出空间给标签
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "completion_time_race.pdf"), format="pdf")
    plt.close()

# ================= 主程序入口 =================

def main(): 
    networks = ['pow', 'pos']
    
    for network in networks:
        # 根据网络类型动态生成输出目录名
        out_dir = f"figs_{network}_advanced"
        os.makedirs(out_dir, exist_ok=True)
        
        print(f"\n{'='*20} 开始生成 {network.upper()} 高级性能分析图表 {'='*20}")
        
        # 1. 队列 Log-Time 动力学
        plot_queue_log_dynamics(network, out_dir)
        
        # 2. 吞吐量稳定性 (Rolling)
        plot_throughput_stability(network, out_dir)
        
        # 3. 吞吐量/证书生成分布 (Violin)
        plot_throughput_violin(network, out_dir)
        
        # 4. 完成时间竞赛 (Bar)
        plot_completion_race_bar(network, out_dir)
        
        print(f"高级图表生成完毕! 保存在: {out_dir}")

if __name__ == "__main__":
    main()
