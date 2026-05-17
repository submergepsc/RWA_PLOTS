import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import json
import argparse
from matplotlib.patches import Patch

# -----------------------------
# 读取配置文件
# -----------------------------
def load_config(config_path):
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"配置文件不存在: {config_path}")
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)

# -----------------------------
# 计算单个方案的三个阶段平均延迟
# -----------------------------
def get_latency_mean(file_path):
    try:
        df = pd.read_csv(file_path)
        stage1 = (df["ccTLS"] - df["ccTIS"]) / 1000
        stage2 = (df["ccTID"] - df["ccTLS"]) / 1000
        stage3 = (df["ccTMC"] - df["ccTID"]) / 1000
        return stage1.mean(), stage2.mean(), stage3.mean()
    except FileNotFoundError:
        print(f"[Warning] 文件不存在: {file_path}")
        return np.nan, np.nan, np.nan
    except KeyError as e:
        print(f"[Warning] 文件缺少列: {file_path}, {e}")
        return np.nan, np.nan, np.nan

# -----------------------------
# 绘制堆叠柱状图
# -----------------------------
def plot_avg_latency_from_config(config_path):
    config = load_config(config_path)
    datasets = config.get("datasets", [])
    
    if not datasets:
        print("[Error] 没有有效的 dataset 配置")
        return
    is_single_dataset = len(datasets) == 1
    
    # 配置颜色和 hatch
    colors = [ds.get("color", "#CCCCCC") for ds in datasets]
    hatches = ["//", "xx", "\\\\"]  # 三个阶段的 hatch
    edgecolors = ["#000000"] * 3  # 描边颜色
    
    stage_labels = ["Src. Chain Stage", "Cross-Chain Stage", "Dst. Chain Stage"]

    stage1_means, stage2_means, stage3_means = [], [], []

    for ds in datasets:
        file_path = ds.get("path")
        s1, s2, s3 = get_latency_mean(file_path)
        stage1_means.append(s1)
        stage2_means.append(s2)
        stage3_means.append(s3)

    # 单个数据集时用窄高度+窄柱形，多个数据集保持原配置
    if is_single_dataset:
        fig, ax = plt.subplots(figsize=(10, 3))  # 进一步减小高度
        bar_height = 0.1  # 柱子高度
        # 设置y轴范围，使柱子占据适当比例
        y_min, y_max = -0.2, 0.2
    else:
        fig, ax = plt.subplots(figsize=(10, 6))
        bar_height = 0.5  # 多个数据集保持原高度
        y_min, y_max = -0.5, len(datasets) - 0.5

    y_pos = np.arange(len(datasets))

    stage_means = [stage1_means, stage2_means, stage3_means]
    left = np.zeros(len(datasets))
    
    for i, (stage_mean, hatch) in enumerate(zip(stage_means, hatches)):
        for j, color in enumerate(colors):
            ax.barh(
                y=j,
                width=stage_mean[j],
                height=bar_height,
                left=left[j],
                color=color,
                hatch=hatch,
                edgecolor=edgecolors[0],
                linewidth=1.5
            )
        left += stage_mean

    # 设置y轴范围
    ax.set_ylim(y_min, y_max)
    
    # 设置标签和刻度
    ax.set_yticks(y_pos)
    ax.set_yticklabels([ds.get("label", f"Method {i+1}") for i, ds in enumerate(datasets)], fontsize=14)
    ax.set_xlabel("Average Latency (s)", fontsize=16)
    ax.tick_params(axis='x', labelsize=14)
    
    # 自定义图例
    legend_handles = [
        Patch(facecolor="white", label=stage_labels[i], hatch=hatches[i], edgecolor=edgecolors[0], linewidth=1.5)
        for i in range(3)
    ]
    ax.legend(handles=legend_handles, loc="lower right", fontsize=14)

    ax.grid(True, linestyle="--", alpha=0.6)
    plt.tight_layout()

    # -----------------------------
    # 保存到 PDF
    # -----------------------------
    pic_dir = "pic"
    os.makedirs(pic_dir, exist_ok=True)
    existing_files = [f for f in os.listdir(pic_dir) if f.startswith("avg_latency") and f.endswith(".pdf")]
    next_idx = len(existing_files) + 1
    save_path = os.path.join(pic_dir, f"avg_latency{next_idx}.pdf")
    plt.savefig(save_path, format="pdf")
    print(f"[Info] 图像已保存到 {save_path}")
    plt.show()

# -----------------------------
# 主入口
# -----------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="方案平均延迟堆叠柱状图绘制")
    parser.add_argument("--config", type=str, required=True, help="JSON 配置文件路径")
    args = parser.parse_args()
    plot_avg_latency_from_config(args.config)