#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plot 05: Scalability (Quantity vs Time)
Target: Generate Line Charts for PoW and PoS.
Logic: X-axis = Processed Quantity, Y-axis = Time(s).
Output: 
  - figures/05_scalability/pow_quantity_vs_time.pdf
  - figures/05_scalability/pos_quantity_vs_time.pdf
"""

import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from typing import Dict

# ================= 全局配置 =================

DATA_DIR = "." 
FIGURES_ROOT = "figures"
SUB_DIR_NAME = "05_scalability" 

# 定义文件映射
SCENARIOS = {
    "pow": "total_handled_num_pow.csv",
    "pos": "total_handled_num_pos.csv"
}

# 协议配置 (配色方案)
PROTOCOLS: Dict[str, Dict[str, str]] = {
    "committee":  {"label": "Ours",       "color": "#1f77b4"}, 
    "daon":       {"label": "Daon",       "color": "#ff7f0e"},
    "decentruth": {"label": "Decentruth", "color": "#2ca02c"},
    "seenfeed":   {"label": "Seenfeed",   "color": "#d62728"},
    "deepthought":{"label": "Deepthought","color": "#9467bd"},
}

# 字体与样式
AXIS_LABEL_SIZE = 44
TICK_LABEL_SIZE = 40
LEGEND_FONT_SIZE = 38
DEFAULT_FIGSIZE = (12, 9)
SAVEFIG_KWARGS = {"bbox_inches": "tight", "pad_inches": 0.1}

# ================= 数据生成 (测试用) =================

def generate_dummy_data_if_needed():
    """生成模拟数据以防文件缺失"""
    time_idx = np.arange(0, 61, 1) # 0-60s
    
    # 模拟数据：X轴是数量，Y轴是Time(Index)
    # 意味着 Committee 处理得最快，所以在同样的时间(Index)内，它的数量(Value)应该最大
    # 绘图时 X=Value, Y=Index，所以 Committee 的曲线斜率最缓（或者是曲线位于最下方，取决于怎么看）
    # 在 X=Quantity, Y=Time 图中，同样数量(X)，Committee耗时(Y)最少 -> 曲线最低
    
    if not os.path.exists(SCENARIOS["pow"]):
        print(f"[Info] Generating dummy PoW data...")
        pd.DataFrame({
            "committee":   time_idx * 500, 
            "daon":        time_idx * 300,
            "decentruth":  time_idx * 200,
            "seenfeed":    time_idx * 150,
            "deepthought": time_idx * 80,
        }, index=time_idx).to_csv(SCENARIOS["pow"])

    if not os.path.exists(SCENARIOS["pos"]):
        print(f"[Info] Generating dummy PoS data...")
        pd.DataFrame({
            "committee":   time_idx * 800, 
            "daon":        time_idx * 500,
            "decentruth":  time_idx * 350,
            "seenfeed":    time_idx * 250,
            "deepthought": time_idx * 150,
        }, index=time_idx).to_csv(SCENARIOS["pos"])

# ================= 绘图核心逻辑 =================

def plot_quantity_vs_time(df: pd.DataFrame, scenario: str, out_dir: str):
    print(f"   -> Plotting Line Chart for [{scenario}]...")
    
    # 1. 样式设置
    plt.figure(figsize=DEFAULT_FIGSIZE)
    plt.rcParams.update({
        'font.family': 'sans-serif',
        'font.size': 14,
        'axes.linewidth': 2.0,
        'axes.labelsize': AXIS_LABEL_SIZE,
        'xtick.labelsize': TICK_LABEL_SIZE,
        'ytick.labelsize': TICK_LABEL_SIZE,
        'legend.fontsize': LEGEND_FONT_SIZE
    })

    # 2. 准备数据: Index 是 Time (Y轴), Columns 是 Quantity (X轴)
    time_index = df.index.to_numpy()

    for method, config in PROTOCOLS.items():
        if method in df.columns:
            quantity_series = df[method].to_numpy()
            
            # 清洗 NaN
            mask = ~np.isnan(quantity_series)
            x_data = quantity_series[mask] # Quantity
            y_data = time_index[mask]      # Time
            
            if len(x_data) == 0: continue
            
            # 突出显示 Ours
            is_ours = (method == 'committee')
            lw = 6.0 if is_ours else 4.0
            zorder = 10 if is_ours else 2
            alpha = 1.0 if is_ours else 0.85
            
            # 绘图 X=Quantity, Y=Time
            plt.plot(x_data, y_data, 
                     label=config['label'], 
                     color=config['color'],
                     linewidth=lw, 
                     alpha=alpha,
                     zorder=zorder)

    # 3. 标签与美化
    plt.xlabel("Processed Quantity")     # 横轴：数量
    plt.ylabel("Processing Time (s)")    # 纵轴：时间
    
    plt.grid(True, linestyle='--', linewidth=1.5, alpha=0.6)
    plt.ylim(bottom=0)
    plt.xlim(left=0)

    # 图例位置：因为曲线是往右上方走的，右下角通常比较空
    plt.legend(loc='lower right', frameon=True, framealpha=0.9)
    
    # 保存
    save_filename = f"{scenario}_quantity_vs_time.pdf"
    save_path = os.path.join(out_dir, save_filename)
    
    plt.savefig(save_path, format="pdf", **SAVEFIG_KWARGS)
    plt.close()

# ================= 主程序 =================

if __name__ == "__main__":
    target_dir = os.path.join(FIGURES_ROOT, SUB_DIR_NAME)
    os.makedirs(target_dir, exist_ok=True)
    
    # 1. 准备数据
    generate_dummy_data_if_needed()
    
    # 2. 循环处理 PoW 和 PoS
    for scenario_name, csv_file in SCENARIOS.items():
        print(f"\nProcessing Scenario: {scenario_name.upper()} ...")
        file_path = os.path.join(DATA_DIR, csv_file)
        
        if os.path.exists(file_path):
            try:
                # 读取 CSV (Index=Time)
                df = pd.read_csv(file_path, index_col=0)
                # 绘图
                plot_quantity_vs_time(df, scenario_name, target_dir)
            except Exception as e:
                print(f"[Error] {e}")
        else:
            print(f"[Warning] File not found: {file_path}")

    print(f"\n[Done] Figures saved in: {target_dir}")