#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RWA-FastOracle 绘图脚本 (优化版)
目标：1:1 复刻 PDF 中的视觉风格
修改点：颜色映射、去除Marker、吞吐量改为柱状图、数据重采样逻辑
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os

# ================= 配置区域 =================
# 设置字体，优先使用英文字体以匹配论文，备用中文字体
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

# 颜色映射 (硬编码以匹配PDF中的颜色)
# Committee: Blue, Daon: Orange, Decentruth: Green, Seenfeed: Red, Deepthought: Purple
COLOR_MAP = {
    'committee': '#1f77b4',     # 蓝色
    'daon': '#ff7f0e',          # 橙色
    'decentruth': '#2ca02c',    # 绿色
    'seenfeed': '#d62728',      # 红色
    'deepthought': '#9467bd',   # 紫色
    'default': 'gray'
}

# 输出目录
OUT_DIR_POS = "figs_pos"
OUT_DIR_POW = "figs_pow"

def get_color(col_name):
    """根据列名获取固定颜色"""
    k = col_name.lower().strip()
    return COLOR_MAP.get(k, COLOR_MAP['default'])

# ================= 绘图函数 =================

def plot_handled_num(df: pd.DataFrame, out_dir: str, network: str, use_log_time: bool = False):
    """
    累计处理数量图
    风格：平滑曲线，无Marker
    """
    plt.figure(figsize=(8, 6))
    
    # 确保 time 列存在
    if 'time' not in df.columns:
        return

    # 预处理时间轴
    t = df['time'].astype(float)
    # 避免 log(0)
    if use_log_time:
        x_vals = np.log(t + 1e-9)
        x_label = "Log Time"
    else:
        x_vals = t
        x_label = "Time (s)"

    for col in df.columns:
        if col == "time":
            continue
        
        # 绘制线条 (linewidth=2, 无marker)
        plt.plot(x_vals, df[col], 
                 linewidth=2.5, 
                 label=col, 
                 color=get_color(col),
                 alpha=0.9)

    plt.legend(fontsize=14, loc='best')
    plt.xlabel(x_label, fontsize=18)
    plt.ylabel("Handled Requests", fontsize=18)
    plt.tick_params(labelsize=14)
    plt.grid(True, linestyle='--', alpha=0.3)
    plt.tight_layout()
    
    os.makedirs(out_dir, exist_ok=True)
    save_path = os.path.join(out_dir, "handled_num.pdf")
    plt.savefig(save_path, format="pdf", bbox_inches='tight')
    plt.close()
    print(f"✓ 生成: {save_path}")


def plot_throughput_bar(df: pd.DataFrame, out_dir: str, filename: str, 
                        ylabel: str, use_log_time: bool = False, bios: float = 0, 
                        resample_interval: str = '5s', divider: int = 1):
    """
    通用柱状图绘制函数 (用于 Throughput 和 Certification)
    风格：PDF P18/P19 风格的细柱状图
    """
    # 数据预处理：重采样
    # 将累计值转换为增量值 (diff)，然后按时间窗口聚合 (resample sum)
    df_idx = df.set_index(pd.to_timedelta(df['time'], unit='s'))
    # 计算每个时间段的增量（假设原始数据是累计值，如果原始数据不是累计值，请去掉 .diff()）
    # 注意：通常 total_handled_num 是累计值
    df_resampled = df_idx.drop(columns=['time']).diff().resample(resample_interval).sum()
    
    # 恢复时间列 (秒)
    df_resampled['time_sec'] = df_resampled.index.total_seconds()
    
    # 过滤掉 bios 之前的数据
    df_plot = df_resampled[df_resampled['time_sec'] > bios].copy()
    
    plt.figure(figsize=(8, 6))
    
    # 计算 X 轴坐标
    if use_log_time:
        # Log Offset Time: log(t - bios)
        time_offset = df_plot['time_sec'] - bios
        # 过滤掉非正数
        mask = time_offset > 0
        df_plot = df_plot[mask]
        x_vals = np.log(time_offset[mask])
        xlabel = "Log Offset Time"
        # 调整柱子宽度：在对数轴上，为了不重叠，宽度需要很小
        width = 0.05 
    else:
        x_vals = df_plot['time_sec'] - bios
        xlabel = "Offset Time (s)"
        width = 2.0 # 线性轴上的宽度

    # 绘制柱状图
    # 技巧：为了防止柱子互相覆盖，我们使用非堆叠的 step 或者是透明度高的 bar
    # PDF P18 看起来像是重叠的 Bar，或者很细的 Line
    
    for col in df_plot.columns:
        if col == 'time_sec':
            continue
            
        y_vals = df_plot[col] / divider
        
        # 过滤掉 0 值，使图表更干净
        mask_y = y_vals > 0
        if not mask_y.any():
            continue

        plt.bar(x_vals[mask_y], y_vals[mask_y],
                width=width,
                label=col,
                color=get_color(col),
                alpha=0.6, # 透明度防遮挡
                align='center')

    plt.legend(fontsize=14, loc='upper right')
    plt.xlabel(xlabel, fontsize=18)
    plt.ylabel(ylabel, fontsize=18)
    plt.tick_params(labelsize=14)
    plt.grid(True, linestyle='--', alpha=0.3)
    plt.tight_layout()
    
    os.makedirs(out_dir, exist_ok=True)
    save_path = os.path.join(out_dir, filename)
    plt.savefig(save_path, format="pdf", bbox_inches='tight')
    plt.close()
    print(f"✓ 生成: {save_path}")


def plot_queue_length(df: pd.DataFrame, out_dir: str, network: str, use_log_time: bool = False):
    """
    队列长度图
    风格：PDF P20 风格，平滑曲线，类似钟形曲线/三角形
    """
    plt.figure(figsize=(8, 6))
    
    t = df['time'].astype(float)
    
    # PDF P20 的 X 轴是 0, 2, 4, 6... 这明显是 log(time) 后的线性坐标
    if use_log_time:
        # 使用 log(t + 1) 防止 log(0)
        x_vals = np.log(t + 1)
        xlabel = "Log Time"
    else:
        x_vals = t
        xlabel = "Time (s)"

    for col in df.columns:
        if col == "time":
            continue
            
        # 绘制线条
        plt.plot(x_vals, df[col], 
                 linewidth=2.0,  # 稍微细一点，展现细节
                 label=col, 
                 color=get_color(col),
                 alpha=0.8) # 无 Marker

    plt.legend(fontsize=14, loc='best')
    plt.xlabel(xlabel, fontsize=18)
    plt.ylabel("Queue Length", fontsize=18)
    plt.tick_params(labelsize=14)
    plt.grid(True, linestyle='--', alpha=0.3)
    plt.tight_layout()
    
    os.makedirs(out_dir, exist_ok=True)
    save_path = os.path.join(out_dir, "queue.pdf")
    plt.savefig(save_path, format="pdf", bbox_inches='tight')
    plt.close()
    print(f"✓ 生成: {save_path}")


def plot_consensus_metric(metric: str, out_dir: str, suffix: str):
    """
    时间类指标图 (Consensus, Search, OnChain)
    风格：PDF P9/P10 风格，高密度噪音图，无 Marker
    """
    filename = f"{metric}_{suffix}.csv"
    if not os.path.exists(filename):
        print(f"⚠️ 跳过: 找不到文件 {filename}")
        return

    df = pd.read_csv(filename)
    
    plt.figure(figsize=(8, 6))
    
    # 采样：如果数据点太多，PDF中通常看起来是密密麻麻的
    # 为了绘图速度和文件大小，如果超过5000点，可以降采样，但为了精确保留所有点
    
    x_col = "seqId"
    
    for col in df.columns:
        if col == x_col:
            continue
            
        # 数据清洗：提取数字
        raw_vals = df[col].astype(str)
        # 提取数值部分 (正则：数字 + 可选小数点)
        values = raw_vals.str.extract(r'^(\d+\.?\d*)').astype(float)[0]
        # 提取单位
        units = raw_vals.str.extract(r'(ms|s|ns)$')[0]
        
        # 统一转为秒
        # 如果没有单位，默认是秒? 视具体数据而定，这里假设如果不匹配则是原始值
        # 向量化操作提高速度
        factors = np.ones(len(units))
        factors[units == 'ms'] = 0.001
        factors[units == 'ns'] = 1e-9
        
        y_vals = values * factors
        
        # 绘制：极细的线，无Marker，模拟噪点图效果
        plt.plot(df[x_col], y_vals, 
                 linewidth=0.8,  # 极细
                 label=col, 
                 color=get_color(col),
                 alpha=0.7)

    plt.legend(fontsize=14, loc='upper right')
    plt.xlabel("Sequence Id", fontsize=18)
    plt.ylabel("Time (s)", fontsize=18)
    plt.tick_params(labelsize=14)
    plt.grid(True, linestyle='--', alpha=0.3)
    plt.tight_layout()
    
    os.makedirs(out_dir, exist_ok=True)
    save_path = os.path.join(out_dir, f"{metric}.pdf")
    plt.savefig(save_path, format="pdf", bbox_inches='tight')
    plt.close()
    print(f"✓ 生成: {save_path}")


# ================= 主程序 =================

def main():
    print(">>> 开始生成 PDF 复刻版图表...")
    
    # 创建输出目录
    os.makedirs(OUT_DIR_POS, exist_ok=True)
    os.makedirs(OUT_DIR_POW, exist_ok=True)

    # ------------------ PoS 网络 ------------------
    print("\n--- 处理 PoS 数据 ---")
    try:
        # 读取数据
        df_handled = pd.read_csv("total_handled_num_pos.csv")
        df_queue = pd.read_csv("total_q_len_pos.csv")
        
        # 1. 累计处理数 (Log Time)
        plot_handled_num(df_handled, OUT_DIR_POS, "PoS", use_log_time=True)
        
        # 2. 吞吐量 (柱状图, Log Offset Time, 每5秒)
        # 这里的 bios=550 是参考 PDF P18 的标题 "t > 550"
        plot_throughput_bar(df_handled, OUT_DIR_POS, "throughput.pdf", 
                            "Throughput (req/5s)", use_log_time=True, bios=550, resample_interval='5s')
        
        # 3. 证书生成速度 (柱状图, Log Offset Time, 每5秒)
        # 注意：证书可能是一批请求生成一个，这里假设 divider=1 或者根据逻辑调整
        plot_throughput_bar(df_handled, OUT_DIR_POS, "certif_num.pdf", 
                            "Certification Speed", use_log_time=True, bios=550, resample_interval='5s')
                            
        # 4. 队列长度 (Log Time, 平滑曲线)
        plot_queue_length(df_queue, OUT_DIR_POS, "PoS", use_log_time=True)
        
        # 5. 时间指标 (散点/噪点图)
        for metric in ["consensusTime", "searchTime", "onChainTime"]:
            plot_consensus_metric(metric, OUT_DIR_POS, "pos")
            
    except FileNotFoundError as e:
        print(f"❌ 缺少 PoS 数据文件: {e}")

    # ------------------ PoW 网络 ------------------
    print("\n--- 处理 PoW 数据 ---")
    try:
        # 读取数据
        df_handled = pd.read_csv("total_handled_num_pow.csv")
        df_queue = pd.read_csv("total_q_len_pow.csv")
        
        # 1. 累计处理数
        plot_handled_num(df_handled, OUT_DIR_POW, "PoW", use_log_time=True)
        
        # 2. 吞吐量 (Log Offset, bios可能不同，这里暂定550，如果PoW开始时间不同请调整)
        plot_throughput_bar(df_handled, OUT_DIR_POW, "throughput.pdf", 
                            "Throughput (req/5s)", use_log_time=True, bios=550, resample_interval='5s')
                            
        # 3. 证书生成
        plot_throughput_bar(df_handled, OUT_DIR_POW, "certif_num.pdf", 
                            "Certification Speed", use_log_time=True, bios=550, resample_interval='5s')
                            
        # 4. 队列
        plot_queue_length(df_queue, OUT_DIR_POW, "PoW", use_log_time=True)
        
        # 5. 时间指标
        for metric in ["consensusTime", "searchTime", "onChainTime"]:
            plot_consensus_metric(metric, OUT_DIR_POW, "pow")

    except FileNotFoundError as e:
        print(f"❌ 缺少 PoW 数据文件: {e}")

    print("\n>>> 所有图表生成完毕！请查看 figs_pos 和 figs_pow 文件夹。")

if __name__ == "__main__":
    main()