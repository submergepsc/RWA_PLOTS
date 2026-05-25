#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RWA-FastOracle 性能对比图表生成脚本 (高级重构版)
生成多样化、具有深度分析能力的图表，以全面展示模型优势。
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
import sys
import seaborn as sns

# ================= 全局配置区域 =================

# 1. 样式与颜色配置
plt.style.use('seaborn-v0_8-whitegrid') # 使用一个清爽、现代的科研绘图样式

# 统一的协议名称、颜色和图例标签
PROTOCOLS = {
    'committee': {'label': 'Ours', 'color': '#DF3156'},
    'daon': {'label': 'Daon', 'color': '#56B4E9'},
    'decentruth': {'label': 'Decentruth', 'color': '#009E73'},
    'seenfeed': {'label': 'Seenfeed', 'color': '#E69F00'},
    'deepthought': {'label': 'Deepthought', 'color': '#4A0080'}
}

# 2. 文件与目录配置
OUT_DIR_POS = "figs_pos"
OUT_DIR_POW = "figs_pow"

# ================= 辅助函数 =================

def clean_time_data(series):
    """将包含单位的时间字符串Series转换为纯秒数的float Series"""
    # 提取数值和单位
    extracted = series.astype(str).str.extract(r'^(\d+\.?\d*)\s*(ms|s|ns)?$', flags=0)
    values = pd.to_numeric(extracted[0], errors='coerce').fillna(0)
    units = extracted[1]
    
    # 根据单位进行转换
    factors = np.ones(len(values))
    factors[units == 'ms'] = 0.001
    factors[units == 'ns'] = 1e-9
    
    return values * factors

# ================= 绘图函数区域 =================  

def plot_latency_scatter(metric: str, network: str, out_dir: str):
    """1. 高密度散点图 (Scatter Plot) - 用于延迟指标"""
    plt.rcParams.update({
        'font.family': 'sans-serif',
        'font.sans-serif': ['Arial', 'DejaVu Sans', 'SimHei'],
        'axes.unicode_minus': False,
        'font.size': 18,
        'axes.labelsize': 20,
        'axes.titlesize': 22,
        'xtick.labelsize': 28,  # 控制X轴刻度标签（如 0, 2500, 5000）的大小
        'ytick.labelsize': 28,  # 控制Y轴刻度标签的大小
        'legend.fontsize': 16,  # <--- 控制图例（Legend）的字体大小
        'figure.figsize': (12, 7),
        'grid.linestyle': '--',
        'grid.alpha': 0.6
    })
    print(f"-> 正在生成 {metric} ({network.upper()}) 散点图...")
    df = pd.read_csv(f"{metric}_{network}.csv")

    plt.figure()
    for key, config in PROTOCOLS.items():
        if key in df.columns:
            y_vals = clean_time_data(df[key])
            plt.scatter(df["seqId"], y_vals, s=2, label=config['label'], color=config['color'], alpha=0.7)

    title_map = {'consensusTime': 'Consensus Time', 'onChainTime': 'On-Chain Time', 'searchTime': 'Search Time'}
    plt.title(f"{title_map.get(metric, metric)} Comparison ({network.upper()})")
    plt.xlabel("Sequence ID")
    plt.ylabel("Time (s)")
    legend = plt.legend(markerscale=8)
    for handle in legend.legend_handles:
        handle.set_sizes([60.0])
    plt.tight_layout()  
    plt.savefig(os.path.join(out_dir, f"{metric}_scatter.pdf"), format="pdf", transparent=True)
    plt.close() 

def plot_summary_bars(network: str, out_dir: str):
    """2. 总结性条形图 (Bar Chart) - 用于总耗时和平均吞吐量"""
    plt.rcParams.update({
        'font.family': 'sans-serif',
        'font.sans-serif': ['Arial', 'DejaVu Sans', 'SimHei'],
        'axes.unicode_minus': False,
        'font.size': 18,
        'axes.labelsize': 20,
        'axes.titlesize': 22,
        'xtick.labelsize': 16,  # 控制X轴刻度标签（如 0, 2500, 5000）的大小
        'ytick.labelsize': 24,  # 控制Y轴刻度标签的大小
        'legend.fontsize': 14,  # <--- 控制图例（Legend）的字体大小
        'figure.figsize': (12, 7),
        'grid.linestyle': '--',
        'grid.alpha': 0.6
    })
    print(f"-> 正在生成 Overall Performance Summary ({network.upper()}) 条形图...")
    df = pd.read_csv(f"total_handled_num_{network}.csv")

    total_time, avg_throughput = {}, {}
    for key in PROTOCOLS.keys():
        if key in df.columns and not df[key].empty:
            max_handled = df[key].max()
            if max_handled > 0:
                finish_time = df.loc[df[key][df[key] >= max_handled].index[0], 'time']
                total_time[key] = finish_time
                avg_throughput[key] = max_handled / finish_time if finish_time > 0 else 0

    if not total_time: return

    labels = [PROTOCOLS[key]['label'] for key in total_time.keys()]
    times = list(total_time.values())
    colors = [PROTOCOLS[key]['color'] for key in total_time.keys()]

    if network == 'pow':
        # 使用断轴 (Broken Axis)
        fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(12, 8))
        fig.subplots_adjust(hspace=0.1)  # 调整子图间距

        # 在两个子图上绘制相同的柱状图
        for ax in [ax1, ax2]:
            bars = ax.bar(labels, times, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5, hatch='//')
            # 添加数值标签
            for bar in bars:
                yval = bar.get_height()
                # 只在对应的轴上显示标签
                if (ax == ax1 and yval > 100000) or (ax == ax2 and yval < 100000):
                    ax.text(bar.get_x() + bar.get_width()/2.0, yval, f'{yval:.1f}s', va='bottom', ha='center', fontsize=20)

        # 设置断轴范围 (根据数据 Deepthought ~1.3M, Others ~20k)
        ax1.set_ylim(1300000, 1350000)  # 上部显示 Deepthought
        ax2.set_ylim(0, 25000)          # 下部显示其他

        # 隐藏边框
        ax1.spines['bottom'].set_visible(False)
        ax2.spines['top'].set_visible(False)
        ax1.xaxis.tick_top()
        ax1.tick_params(labeltop=False)  # 隐藏上图的 X 轴标签
        ax2.xaxis.tick_bottom()

        # 添加断裂线 (d)
        d = .015 
        kwargs = dict(transform=ax1.transAxes, color='k', clip_on=False)
        ax1.plot((-d, +d), (-d, +d), **kwargs)        # top-left diagonal
        ax1.plot((1 - d, 1 + d), (-d, +d), **kwargs)  # top-right diagonal

        kwargs.update(transform=ax2.transAxes)  # switch to the bottom axes
        ax2.plot((-d, +d), (1 - d, 1 + d), **kwargs)  # bottom-left diagonal
        ax2.plot((1 - d, 1 + d), (1 - d, 1 + d), **kwargs)  # bottom-right diagonal
        
        ax1.set_title(f'Overall Performance Summary ({network.upper()})')
        # Y轴标签居中比较麻烦，这里简单处理
        fig.text(0.04, 0.5, 'Total Time to Complete (s)', va='center', rotation='vertical', fontsize=20)
        plt.xticks(rotation=30, ha="right")

    else:
        # 正常绘制 (POS)
        fig, ax = plt.subplots()
        bars = ax.bar(labels, times, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5, hatch='//')
        
        ax.set_ylabel('Total Time to Complete (s)')
        ax.set_title(f'Overall Performance Summary ({network.upper()})')
        plt.xticks(rotation=30, ha="right")
        
        for bar in bars:
            yval = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2.0, yval, f'{yval:.1f}s', va='bottom', ha='center', fontsize=20)

    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "summary_bars.pdf"), format="pdf")
    plt.close()

def plot_latency_cdf(metric: str, network: str, out_dir: str):
    """3. 累积分布函数图 (CDF) - 用于延迟指标"""
    plt.rcParams.update({
        'font.family': 'sans-serif',
        'font.sans-serif': ['Arial', 'DejaVu Sans', 'SimHei'],
        'axes.unicode_minus': False,
        'font.size': 18,
        'axes.labelsize': 20,
        'axes.titlesize': 22,
        'xtick.labelsize':28,  # 控制X轴刻度标签（如 0, 2500, 5000）的大小
        'ytick.labelsize': 28,  # 控制Y轴刻度标签的大小
        'legend.fontsize': 32,  # <--- 控制图例（Legend）的字体大小
        'figure.figsize': (12, 7),
        'grid.linestyle': '--',
        'grid.alpha': 0.6
    })
    print(f"-> 正在生成 {metric} ({network.upper()}) CDF图...")
    df = pd.read_csv(f"{metric}_{network}.csv")

    if network == 'pow':
        # 使用断轴 (Broken Axis) - 左右分割
        fig, (ax1, ax2) = plt.subplots(1, 2, sharey=True, figsize=(12, 7), gridspec_kw={'width_ratios': [4, 1]})
        fig.subplots_adjust(wspace=0.05)
        axes = [ax1, ax2]
    else:
        fig, ax = plt.subplots()
        axes = [ax]

    for key, config in PROTOCOLS.items():
        if key in df.columns:
            # 数据清洗和计算 CDF (保持不变)
            data = clean_time_data(df[key]).sort_values()
            if len(data) == 0: continue # 防止空数据报错
            cdf = np.arange(1, len(data) + 1) / len(data)

            # ================== 【新增的判断语句】 ==================
            # 如果是 RWA (committee)，设置高 zorder 让它浮在最上面，并用虚线
            if key == 'committee':
                current_zorder = 10      # 10 > 1，强制画在最上层
                current_linestyle = '--' # 虚线，防止颜色相近时分辨不清
                current_linewidth = 3.5  # 加粗一点
                current_alpha = 1.0      # 不透明
            else:
                current_zorder = 1       # 其他协议层级低，会被 RWA 盖住
                current_linestyle = '-'  # 实线
                current_linewidth = 2.5  
                current_alpha = 0.8      # 稍微透明一点，增加层次感
            # ========================================================

            # 绘图时传入这些动态参数
            for ax in axes:
                ax.plot(data, cdf, 
                         label=config['label'], 
                         color=config['color'], 
                         linewidth=current_linewidth,
                         linestyle=current_linestyle,
                         alpha=current_alpha,
                         zorder=current_zorder)  # <--- 关键参数

                     
    title_map = {'consensusTime': 'Consensus Time', 'onChainTime': 'On-Chain Time', 'searchTime': 'Search Time'}

    if network == 'pow':
        # 设置断轴范围
        ax1.set_xlim(0, 15)    # 左图显示大部分 (0-15s)
        ax2.set_xlim(600, 700) # 右图显示 Deepthought (600-700s)

        # 隐藏边框
        ax1.spines['right'].set_visible(False)
        ax2.spines['left'].set_visible(False)
        ax2.yaxis.tick_right()
        ax2.tick_params(labelright=False) # 隐藏右图的 Y 轴标签
        
        # 断裂线
        d = .015 
        kwargs = dict(transform=ax1.transAxes, color='k', clip_on=False)
        ax1.plot((1 - d, 1 + d), (-d, +d), **kwargs)
        ax1.plot((1 - d, 1 + d), (1 - d, 1 + d), **kwargs)

        kwargs.update(transform=ax2.transAxes)
        ax2.plot((-d, +d), (-d, +d), **kwargs)
        ax2.plot((-d, +d), (1 - d, 1 + d), **kwargs)
        
        # 标题和标签
        fig.suptitle(f"{title_map.get(metric, metric)} CDF ({network.upper()})", fontsize=22, y=0.95)
        fig.text(0.5, 0.04, "Time (s)", ha='center', fontsize=20)
        ax1.set_ylabel("Cumulative Probability")
        
        # 图例
        ax1.legend(loc='lower right')
        
    else:
        plt.title(f"{title_map.get(metric, metric)} CDF ({network.upper()})")
        plt.xlabel("Time (s)")
        plt.ylabel("Cumulative Probability")
        plt.xlim(left=-0.01)
        plt.ylim([0, 1])
        plt.legend(loc='lower right')

    plt.tight_layout()
    if network == 'pow':
        plt.subplots_adjust(top=0.9)
        
    plt.savefig(os.path.join(out_dir, f"{metric}_cdf.pdf"), format="pdf")
    plt.close()
    plt.title(f"{title_map.get(metric, metric)} CDF ({network.upper()})")
    plt.xlabel("Time (s)")
    plt.ylabel("Cumulative Probability")
    plt.xlim(left=-0.01) # 略微调整以显示接近0的数据
    plt.ylim([0, 1])
    plt.legend(loc='lower right')
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, f"{metric}_cdf.pdf"), format="pdf")
    plt.close()

def plot_box_violin_comparison(metric: str, network: str, out_dir: str):
    """
    4. 小提琴图 + 箱线图 (Violin + Box Plot)
    作用：展示数据分布的形态以及统计学分布。
    """
    plt.rcParams.update({
        'font.family': 'sans-serif',
        'font.sans-serif': ['Arial', 'DejaVu Sans', 'SimHei'],
        'axes.unicode_minus': False,
        'font.size': 18,
        'axes.labelsize': 20,
        'axes.titlesize': 22,
        'xtick.labelsize': 14,  # 控制X轴刻度标签（如 0, 2500, 5000）的大小
        'ytick.labelsize': 24,  # 控制Y轴刻度标签的大小
        'legend.fontsize': 14,  # <--- 控制图例（Legend）的字体大小
        'figure.figsize': (12, 8),
        'grid.linestyle': '--',
        'grid.alpha': 0.6
    })
    print(f"-> 正在生成 {metric} ({network.upper()}) 小提琴分布图...")
    csv_file = f"{metric}_{network}.csv"
    df = pd.read_csv(csv_file)
    
    plot_data = []
    for col in PROTOCOLS.keys():
        if col in df.columns:
            vals = clean_time_data(df[col])
            if len(vals) > 2000: vals = vals.sample(2000) # Downsample for performance
            temp_df = pd.DataFrame({'Latency': vals, 'Protocol': PROTOCOLS[col]['label']})
            plot_data.append(temp_df)
    
    if not plot_data: return
    long_df = pd.concat(plot_data)

    plt.figure(figsize=(12, 8))
    
    sns.violinplot(x='Protocol', y='Latency', data=long_df, inner=None, palette=[p['color'] for p in PROTOCOLS.values() if p['label'] in long_df['Protocol'].unique()], alpha=0.3)
    sns.boxplot(x='Protocol', y='Latency', data=long_df, width=0.2, boxprops={'facecolor':'None', 'edgecolor':'black'}, showfliers=False)
    
    plt.title(f"{metric} Distribution Analysis (Violin & Box) ({network.upper()})")
    plt.ylabel("Latency (s)")
    plt.xlabel("") # Protocol names are clear enough
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    plt.xticks(rotation=15, ha="right")
    
    plt.savefig(os.path.join(out_dir, f"{metric}_violin_box.pdf"), format="pdf")
    plt.close()

def plot_kde_density(metric: str, network: str, out_dir: str):
    """
    5. 核密度估计图 (KDE Plot)
    作用：平滑的直方图，清晰展示大部分请求落在哪个时间区间。
    """
    plt.rcParams.update({
        'font.family': 'sans-serif',
        'font.sans-serif': ['Arial', 'DejaVu Sans', 'SimHei'],
        'axes.unicode_minus': False,
        'font.size': 18,
        'axes.labelsize': 20,
        'axes.titlesize': 22,
        'xtick.labelsize': 28,  # 控制X轴刻度标签（如 0, 2500, 5000）的大小
        'ytick.labelsize': 28,  # 控制Y轴刻度标签的大小
        'legend.fontsize': 32,  # <--- 控制图例（Legend）的字体大小
        'figure.figsize': (12, 7),
        'grid.linestyle': '--',
        'grid.alpha': 0.6
    })
    print(f"-> 正在生成 {metric} ({network.upper()}) 核密度图 (KDE)...")
    csv_file = f"{metric}_{network}.csv"
    df = pd.read_csv(csv_file)
    
    plt.figure(figsize=(12,8))
    
    for col, config in PROTOCOLS.items():
        if col in df.columns:
            vals = clean_time_data(df[col])
            sns.kdeplot(vals, label=config['label'], color=config['color'], fill=True, alpha=0.1, linewidth=2.5)

    title_map = {'consensusTime': 'Consensus Time', 'onChainTime': 'On-Chain Time', 'searchTime': 'Search Time'}
    plt.title(f"{title_map.get(metric, metric)} Probability Density ({network.upper()})")
    plt.xlabel("Time (s)")
    plt.ylabel("Density")
    plt.legend()
    plt.xlim(left=0)
    
    plt.savefig(os.path.join(out_dir, f"{metric}_kde.pdf"), format="pdf")
    plt.close()

def plot_stability_analysis(metric: str, network: str, out_dir: str, window=50):
    """
    6. 滑动窗口稳定性分析 (Rolling Mean & Std)
    作用：分析系统性能是否随时间推移而稳定。
    """
    plt.rcParams.update({
        'font.family': 'sans-serif',
        'font.sans-serif': ['Arial', 'DejaVu Sans', 'SimHei'],
        'axes.unicode_minus': False,    
        'font.size': 18,
        'axes.labelsize': 20,
        'axes.titlesize': 22,
        'xtick.labelsize': 28,  # 控制X轴刻度标签（如 0, 2500, 5000）的大小
        'ytick.labelsize': 28,  # 控制Y轴刻度标签的大小
        'legend.fontsize': 14,  # <--- 控制图例（Legend）的字体大小
        'figure.figsize': (12, 7),
        'grid.linestyle': '--',
        'grid.alpha': 0.6
    })
    print(f"-> 正在生成 {metric} ({network.upper()}) 稳定性分析图...")
    csv_file = f"{metric}_{network}.csv"
    df = pd.read_csv(csv_file)
    
    plt.figure(figsize=(12, 8)) 

    
    for col, config in PROTOCOLS.items():
        if col in df.columns:
            vals = clean_time_data(df[col])
            series = pd.Series(vals)
            rolling_mean = series.rolling(window=window).mean()
            rolling_std  = series.rolling(window=window).std()
            
            plt.plot(df['seqId'], rolling_mean, label=config['label'], color=config['color'], linewidth=2.5)
            plt.fill_between(df['seqId'], 
                            rolling_mean - rolling_std, 
                            rolling_mean + rolling_std, 
                            color=config['color'], alpha=0.15)
                            
    title_map = {'consensusTime': 'Consensus Time', 'onChainTime': 'On-Chain Time', 'searchTime': 'Search Time'}
    plt.title(f"{title_map.get(metric, metric)} Stability (Rolling Mean, w={window}) ({network.upper()})")
    plt.xlabel("Sequence ID")
    plt.ylabel("Average Latency (s)")
    plt.legend()
    
    plt.savefig(os.path.join(out_dir, f"{metric}_stability.pdf"), format="pdf")
    plt.close()

    
# ================= 主程序入口 =================

def main():
    """主函数，为PoS和PoW环境生成一整套多样化的图表。"""
    networks_to_run = ['pos', 'pow']
    # networks_to_run=['pos']
    
    for network in networks_to_run:
        out_dir = OUT_DIR_POS if network == 'pos' else OUT_DIR_POW
        os.makedirs(out_dir, exist_ok=True)
        
        print(f"\n{'='*20} 开始生成 {network.upper()} 环境下的图表 {'='*20}")
        
        # 1. 延迟散点图
        plot_latency_scatter('consensusTime', network, out_dir)
        
        # 2. 总结性条形图 (总耗时)
        plot_summary_bars(network, out_dir)
        
        # 3. 延迟CDF图
        plot_latency_cdf('consensusTime', network, out_dir)

        # 4. 小提琴/箱线分布图
        plot_box_violin_comparison('consensusTime', network, out_dir)

        # 5. 概率密度图 (KDE)
        plot_kde_density('consensusTime', network, out_dir)

        # 6. 稳定性分析图
        plot_stability_analysis('consensusTime', network, out_dir)

    print(f"\n{'='*20} 所有图表生成完毕! {'='*20}")

if __name__ == "__main__":
    main()
