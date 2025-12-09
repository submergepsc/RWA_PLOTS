import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
import typing
import re

# ==========================================
# 1. 全局样式设置 (Publication Quality)
# ==========================================
# 这些设置确保图片文字够大、线条够清晰，直接符合 PDF 文档中的风格
plt.rcParams.update({
    'font.family': 'sans-serif',      # 使用无衬线字体 (接近 Arial/Helvetica)
    'font.size': 18,                  # 全局字体大小 18
    'axes.labelsize': 20,             # 坐标轴标签大小 20
    'axes.titlesize': 22,             # 标题大小 22
    'xtick.labelsize': 18,            # X轴刻度大小
    'ytick.labelsize': 18,            # Y轴刻度大小
    'legend.fontsize': 16,            # 图例大小
    'lines.linewidth': 2.5,           # 线条加粗
    'figure.figsize': (10, 7),        # 图片比例 (接近 4:3 或 3:2)
    'figure.autolayout': True,        # 自动调整布局，防止标签被切掉
    'grid.alpha': 0.3,                # 网格透明度
    'grid.linestyle': '--',           # 网格虚线
    'savefig.dpi': 300                # 保存高分辨率
})

# ==========================================
# 2. 增强的绘图函数
# ==========================================

def plot_handled_num(df: pd.DataFrame, out_dir: str = "figure", use_log_time: bool = False):
    plt.figure()
    
    # 自动获取更美观的颜色循环
    colors = plt.cm.tab10.colors 
    
    for idx, col in enumerate(df.columns):
        if col == "time": continue    
        
        # 数据准备
        y_vals = df[col]
        if use_log_time:
            # 避免对 0 取对数
            valid_mask = df["time"] > 0
            x_vals = np.log(np.asarray(df.loc[valid_mask, "time"]).astype(float))
            y_vals = y_vals[valid_mask]
        else:
            x_vals = df["time"]
            
        plt.plot(x_vals, y_vals, label=col, color=colors[idx % 10])

    plt.legend(loc='upper left', frameon=True, fancybox=True, framealpha=0.9)
    plt.xlabel("Log Time" if use_log_time else "Time")
    plt.ylabel("Handled Num")
    plt.title("Total Handled Requests")
    plt.grid(True)
    
    os.makedirs(out_dir, exist_ok=True)
    plt.savefig(os.path.join(out_dir, "handled_num.pdf"), format="pdf")
    plt.close()

def plot_throughpout(df: pd.DataFrame, out_dir: str = "figure", use_log_time: bool = False, bios: float = 550):
    df = df.copy()
    # 仅保留 time > bios 的部分
    df = df[df["time"] > bios]
    
    plt.figure()
    colors = plt.cm.tab10.colors
    
    for idx, col in enumerate(df.columns):
        if col == "time": continue
        
        # 计算吞吐量 (差分)
        _grouped_res = df.groupby("time")[col].sum()
        _res = _grouped_res.diff().fillna(0)
        
        # X轴处理
        if use_log_time:
            # log(t - bios)
            time_diff = _res.index - bios
            # 过滤掉 <= 0 的值以防报错
            valid_mask = time_diff > 0
            x_vals = np.log(time_diff[valid_mask].astype(float))
            y_vals = _res[valid_mask]
        else:
            x_vals = _res.index
            y_vals = _res
            
        # 优化：吞吐量通常是波动的，使用稍细的线并加上透明度，
        # 或者使用 fill_between 让波峰更明显 (参考论文常见做法)
        plt.plot(x_vals, y_vals, label=col, linewidth=1.5, alpha=0.8, color=colors[idx % 10])
        
        # 可选：如果想要更像“柱状”或“尖峰”，可以取消注释下面这行
        # plt.fill_between(x_vals, y_vals, alpha=0.1, color=colors[idx % 10])

    plt.legend(loc='upper right')
    plt.xlabel(f"{'Log Time' if use_log_time else 'Time'} ($t > {bios}$)")
    plt.ylabel("Throughput (reqs)")
    plt.title("System Throughput Analysis")
    plt.grid(True)
    
    os.makedirs(out_dir, exist_ok=True)
    plt.savefig(os.path.join(out_dir, "throughput.pdf"), format="pdf")
    plt.close()

def plot_queue_length(df: pd.DataFrame, out_dir: str = "figure", use_log_time: bool = False):
    plt.figure()
    colors = plt.cm.tab10.colors
    
    for idx, col in enumerate(df.columns):
        if col == "time": continue

        if use_log_time:
            # 同样处理 log(0)
            valid_mask = df["time"] > 0
            x_vals = np.log(df.loc[valid_mask, "time"].astype(float))
            y_vals = df.loc[valid_mask, col]
        else:
            x_vals = df["time"]
            y_vals = df[col]
            
        plt.plot(x_vals, y_vals, label=col, color=colors[idx % 10])

    plt.legend()
    plt.xlabel("Log Time" if use_log_time else "Time")
    plt.ylabel("Queue Length")
    plt.title("Queue Draining Performance")
    plt.grid(True)
    
    os.makedirs(out_dir, exist_ok=True)
    plt.savefig(os.path.join(out_dir, "queue.pdf"), format="pdf")
    plt.close()

def plot_consensus(_metrics: typing.List, out_dir: str = "figure"):
    colors = plt.cm.tab10.colors
    
    for metric in _metrics:
        file_path = f"{metric}_pow.csv"
        if not os.path.exists(file_path):
            print(f"Warning: {file_path} not found. Skipping.")
            continue
            
        df = pd.read_csv(file_path)
        plt.figure()
        
        for idx, col in enumerate(df.columns):
            if col == "seqId": continue
            
            # 增强的数据解析逻辑 (处理 '100 ms', '1.2 s' 等格式)
            # 1. 强制转换为字符串
            # 2. 提取数值部分
            # 3. 提取单位部分
            # 4. 转换
            
            str_series = df[col].astype(str)
            
            # 提取数值
            nums = str_series.str.extract(r'^(\d+\.?\d*)')[0].astype(float)
            
            # 提取单位 (如果有)
            units = str_series.str.extract(r'([a-z]+)$')[0]
            
            # 转换逻辑: 如果单位是 ms，除以 1000；否则保持原样 (假设是 s 或无单位)
            # 使用 numpy where 进行矢量化操作
            final_vals = np.where(units == 'ms', nums / 1000.0, nums)
            
            # 绘图：对于共识时间等高频数据，线宽稍微调细一点，避免太乱
            plt.plot(df["seqId"], final_vals, label=col, linewidth=1.5, alpha=0.9, color=colors[idx % 10])

        plt.legend(loc='best') # 让 matplotlib 自动选择最佳位置
        plt.xlabel("Sequence ID")
        plt.ylabel("Time (s)")
        plt.title(f"{metric} Latency")
        plt.grid(True)
        
        os.makedirs(out_dir, exist_ok=True)
        plt.savefig(os.path.join(out_dir, f"{metric}.pdf"), format="pdf")
        plt.close()

if __name__ == "__main__":
    fig_dir = "figure_pow_improved"
    
    # 读取数据 (假设您已经用 prepare.py 生成了 csv)
    # 注意：prepare.py 生成的 csv 通常第一列是 index 但没有 header 或者是 time
    # 这里假设 csv 格式标准。如果报错，可能需要检查 csv 的 header。
    
    try:
        # 读取 Queue 和 Handled 数据
        # 假设 csv 像这样: time,committee,daon...
        df_handled = pd.read_csv("total_handled_num_pow.csv") 
        df_q = pd.read_csv("total_q_len_pow.csv")
        
        plot_handled_num(df_handled, out_dir=fig_dir, use_log_time=True)
        plot_throughpout(df_handled, out_dir=fig_dir, use_log_time=True)
        plot_queue_length(df_q, out_dir=fig_dir, use_log_time=True)
        
        # 读取 Consensus 数据
        plot_consensus(["consensusTime", "searchTime", "onChainTime"], out_dir=fig_dir)
        
        print(f"Figures saved to {fig_dir}/")
        
    except FileNotFoundError as e:
        print(f"Error: Data file not found. Please run prepare.py first. Details: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")