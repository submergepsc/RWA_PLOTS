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

# ================= 全局配置区域 =================

# 1. 样式与颜色配置
plt.style.use('seaborn-v0_8-whitegrid') # 使用一个清爽、现代的科研绘图样式
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'DejaVu Sans', 'SimHei'],
    'axes.unicode_minus': False,
    'font.size': 18,
    'axes.labelsize': 20,
    'axes.titlesize': 22,
    'xtick.labelsize': 16,
    'ytick.labelsize': 16,
    'legend.fontsize': 14,
    'figure.figsize': (12, 7),
    'grid.linestyle': '--',
    'grid.alpha': 0.6
})

# 统一的协议名称、颜色和图例标签
PROTOCOLS = {
    'committee': {'label': 'RWA-FastOracle (Ours)', 'color': '#1f77b4'},
    'daon': {'label': 'Daon', 'color': '#ff7f0e'},
    'decentruth': {'label': 'Decentruth', 'color': '#2ca02c'},
    'seenfeed': {'label': 'Seenfeed', 'color': '#d62728'},
    'deepthought': {'label': 'Deepthought', 'color': '#9467bd'}
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
    
    fig, ax = plt.subplots()
    bars = ax.bar(labels, times, color=[PROTOCOLS[key]['color'] for key in total_time.keys()], alpha=0.8)
    ax.set_ylabel('Total Time to Complete (s)')
    ax.set_title(f'Overall Performance Summary ({network.upper()})')
    plt.xticks(rotation=15, ha="right")
    
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2.0, yval, f'{yval:.1f}s', va='bottom', ha='center', fontsize=14)

    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "summary_bars.pdf"), format="pdf")
    plt.close()

def plot_latency_cdf(metric: str, network: str, out_dir: str):
    """3. 累积分布函数图 (CDF) - 用于延迟指标"""
    print(f"-> 正在生成 {metric} ({network.upper()}) CDF图...")
    df = pd.read_csv(f"{metric}_{network}.csv")

    plt.figure()
    for key, config in PROTOCOLS.items():
        if key in df.columns:
            data = clean_time_data(df[key]).sort_values()
            cdf = np.arange(1, len(data) + 1) / len(data)
            plt.plot(data, cdf, label=config['label'], color=config['color'], linewidth=2.5)

    title_map = {'consensusTime': 'Consensus Time', 'onChainTime': 'On-Chain Time', 'searchTime': 'Search Time'}
    plt.title(f"{title_map.get(metric, metric)} CDF ({network.upper()})")
    plt.xlabel("Time (s)")
    plt.ylabel("Cumulative Probability")
    plt.xlim(left=0)
    plt.ylim([0, 1])
    plt.legend(loc='lower right')
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, f"{metric}_cdf.pdf"), format="pdf")
    plt.close()

# ================= 主程序入口 =================

def main():
    """主函数，为PoS和PoW环境生成一整套多样化的图表。"""
    networks_to_run = ['pos', 'pow']
    
    for network in networks_to_run:
        out_dir = OUT_DIR_POS if network == 'pos' else OUT_DIR_POW
        os.makedirs(out_dir, exist_ok=True)
        
        print(f"\n{'='*20} 开始生成 {network.upper()} 环境下的图表 {'='*20}")
        
        # 1. 延迟散点图
        plot_latency_scatter('consensusTime', network, out_dir)
        
        # # 2. 总结性条形图 (总耗时)
        # plot_summary_bars(network, out_dir)
        
        # # 3. 延迟CDF图
        # plot_latency_cdf('consensusTime', network, out_dir)

    print(f"\n{'='*20} 所有图表生成完毕! {'='*20}")

if __name__ == "__main__":
    main()