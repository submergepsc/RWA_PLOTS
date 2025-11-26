#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RWA-FastOracle 性能对比图表生成脚本
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os

# ================= 配置区域 =================
# 设置字体，以确保图表清晰显示
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

# 颜色映射 (硬编码以匹配PDF中的颜色)
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
    """根据列名（协议名）获取固定颜色"""
    # 将列名转换为小写并去除首尾空格，以匹配 COLOR_MAP 的键
    key = col_name.lower().strip()
    return COLOR_MAP.get(key, COLOR_MAP['default'])

# ================= 绘图函数 1: 累计处理请求数 =================

def plot_handled_num(df: pd.DataFrame, out_dir: str, use_log_time: bool = False):
    """
    绘制累计处理请求数量图。
    风格：平滑曲线，无数据点标记。

    :param df: 包含时间和各协议累计数量的DataFrame。
    :param out_dir: 图片输出目录。
    :param use_log_time: X轴是否使用对数刻度。
    """
    plt.figure(figsize=(8, 6))
    
    if 'time' not in df.columns:
        print("错误：数据中缺少 'time' 列。")
        return

    # 根据是否使用对数刻度，准备X轴数据和标签
    t = df['time'].astype(float)
    if use_log_time:
        # 使用 log(t + 1) 来避免 log(0) 的问题
        x_vals = np.log(t + 1)
        x_label = "Log Time"
    else:
        x_vals = t
        x_label = "Time (s)"

    # 遍历DataFrame的每一列（每个协议）进行绘图
    for col in df.columns:
        if col == "time":
            continue
        
        plt.plot(x_vals, df[col], 
                 linewidth=2.5, 
                 label=col.strip(), # 去除列名可能存在的空格
                 color=get_color(col),
                 alpha=0.9)

    plt.legend(fontsize=14, loc='best')
    plt.xlabel(x_label, fontsize=18)
    plt.ylabel("Handled Requests", fontsize=18)
    plt.tick_params(labelsize=14)
    plt.grid(True, linestyle='--', alpha=0.3)
    plt.tight_layout()
    
    # 创建输出目录并保存图片
    os.makedirs(out_dir, exist_ok=True)
    save_path = os.path.join(out_dir, "handled_num.pdf")
    plt.savefig(save_path, format="pdf", bbox_inches='tight')
    plt.close()
    print(f"✓ 已生成图表: {save_path}")


# ================= 主程序入口 =================

def main():
    """
    主函数，负责读取数据并调用绘图函数。
    """
    print(">>> 开始生成'累计处理请求数'图表...")
    
    # --- 生成 PoS 图表 ---
    try:
        df_handled_pos = pd.read_csv("total_handled_num_pos.csv")
        plot_handled_num(df_handled_pos, OUT_DIR_POS, use_log_time=True)
    except FileNotFoundError:
        print("❌ 未找到 'total_handled_num_pos.csv'，跳过 PoS 累计处理图。")

    # --- 生成 PoW 图表 ---
    try:
        df_handled_pow = pd.read_csv("total_handled_num_pow.csv")
        plot_handled_num(df_handled_pow, OUT_DIR_POW, use_log_time=True)
    except FileNotFoundError:
        print("❌ 未找到 'total_handled_num_pow.csv'，跳过 PoW 累计处理图。")

    print("\n>>> '累计处理请求数'图表生成完毕。")


if __name__ == "__main__":
    main()
