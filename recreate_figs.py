#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
根据现有 figs 目录风格重新生成图表的脚本。
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os

# ================= 全局配置区域 =================

# 1. 样式与颜色配置 (参考 plot_performance_comparison.py)
plt.style.use('seaborn-v0_8-whitegrid')
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
OUT_DIR = "figs_recreated"
NETWORK = "pos" # 我们将根据 figs 目录中的 POS 图表进行复现

# ================= 辅助函数 =================

def clean_time_data(series):
    """将包含单位的时间字符串Series转换为纯秒数的float Series"""
    extracted = series.astype(str).str.extract(r'^(\d+\.?\d*)\s*(ms|s|ns)?$', flags=0)
    values = pd.to_numeric(extracted[0], errors='coerce').fillna(0)
    units = extracted[1]
    
    factors = np.ones(len(values))
    factors[units == 'ms'] = 0.001
    factors[units == 'ns'] = 1e-9
    
    return values * factors

# ================= 绘图函数区域 =================

def plot_latency_cdf(metric: str, network: str, out_dir: str):
    """
    绘制累积分布函数图 (CDF)，风格模仿 figs/consensusTime_cdf.pdf
    """
    print(f"-> 正在生成 {metric} ({network.upper()}) CDF图...")
    csv_file = f"{metric}_{network}.csv"
    if not os.path.exists(csv_file):
        print(f"  [错误] 数据文件 {csv_file} 不存在，跳过此图表。")
        return
        
    df = pd.read_csv(csv_file)

    plt.figure()
    for key, config in PROTOCOLS.items():
        if key in df.columns:   
            data = clean_time_data(df[key]).sort_values()
            if data.empty or (data == 0).all():
                print(f"  [警告] 协议 '{config['label']}' 的数据为空或全为0，将跳过绘制。")
                continue
            cdf = np.arange(1, len(data) + 1) / len(data)
            plt.plot(data, cdf, label=config['label'], color=config['color'], linewidth=2.5)

    title_map = {'consensusTime': 'Consensus Time', 'onChainTime': 'On-Chain Time', 'searchTime': 'Search Time'}
    plt.title(f"{title_map.get(metric, metric)} CDF ({network.upper()})")
    plt.xlabel("Time (s)")
    plt.ylabel("Cumulative Probability")
    plt.xlim(left=0)
    plt.ylim([0, 1.01]) # Y轴上限略微调高，避免顶到边框
    plt.legend(loc='lower right')
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, f"{metric}_cdf.pdf"), format="pdf")
    plt.close()

def plot_summary_bars(network: str, out_dir: str):
    """
    绘制总结性条形图，这在之前的脚本中也存在，很可能也是figs目录的一部分。
    """
    print(f"-> 正在生成 Overall Performance Summary ({network.upper()}) 条形图...")
    csv_file = f"total_handled_num_{network}.csv"
    if not os.path.exists(csv_file):
        print(f"  [错误] 数据文件 {csv_file} 不存在，跳过此图表。")
        return

    df = pd.read_csv(csv_file)

    total_time = {}
    for key in PROTOCOLS.keys():
        if key in df.columns and not df[key].empty:
            max_handled = df[key].max()
            if max_handled > 0:
                # 找到第一次达到最大处理数的时间
                finish_time_series = df.loc[df[key] >= max_handled, 'time']
                if not finish_time_series.empty:
                    finish_time = finish_time_series.iloc[0]
                    total_time[key] = finish_time

    if not total_time: 
        print("  [警告] 未能计算任何协议的总时间，跳过条形图。")
        return

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

# ================= 主程序入口 =================

def main():
    """主函数，重新生成figs风格的图表。"""
    os.makedirs(OUT_DIR, exist_ok=True)
    
    print(f"\n{'='*20} 开始重新生成 {NETWORK.upper()} 环境下的图表 {'='*20}")
    
    # 1. 重新生成 CDF 图
    plot_latency_cdf('consensusTime', NETWORK, OUT_DIR)
    
    # 2. 重新生成总结性条形图
    plot_summary_bars(NETWORK, OUT_DIR)

    print(f"\n{'='*20} 所有图表生成完毕! 已保存至 '{OUT_DIR}' 目录。 {'='*20}")

if __name__ == "__main__":
    main()
