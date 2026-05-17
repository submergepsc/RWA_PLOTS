import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
import json
import argparse

# -----------------------------
# 读取配置文件
# -----------------------------
def load_config(config_path):
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"配置文件不存在: {config_path}")
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)

# -----------------------------
# 处理单个 dataset，计算累计延迟
# -----------------------------
def process_csv(path, label, x_ticks):
    if not os.path.exists(path):
        print(f"[Warning] 文件不存在: {path}")
        return {"Number of Cross-Chain Tx": [], "Latency (s)": [], "Method": []}

    df = pd.read_csv(path)
    if "Confirmed latency of this tx (ms)" not in df.columns or "ccTIS" not in df.columns:
        print(f"[Error] 文件 {path} 缺少所需列，跳过")
        return {"Number of Cross-Chain Tx": [], "Latency (s)": [], "Method": []}

    # 按时间排序
    df = df.sort_values(by="ccTIS")

    result = {"Number of Cross-Chain Tx": [], "Latency (s)": [], "Method": []}
    for tx in x_ticks:
        if tx <= len(df):
            selected = df.head(tx)
            total_latency = selected["Confirmed latency of this tx (ms)"].sum() / 1000
            result["Number of Cross-Chain Tx"].append(tx)
            result["Latency (s)"].append(total_latency)
            result["Method"].append(label)
    return result

# -----------------------------
# 主绘图函数
# -----------------------------
def plot_from_config(config_path):
    config = load_config(config_path)
    datasets = config.get("datasets", [])
    x_ticks = config.get("x_ticks", [10000, 100000, 200000, 300000])
    palette = {ds["label"]: ds.get("color", None) for ds in datasets}

    all_data = {"Number of Cross-Chain Tx": [], "Latency (s)": [], "Method": []}
    for ds in datasets:
        path = ds.get("path")
        label = ds.get("label", os.path.basename(path) if path else "Unknown")
        if not path:
            print(f"[Warning] dataset 缺少 path，跳过: {ds}")
            continue
        data = process_csv(path, label, x_ticks)
        for k in all_data:
            all_data[k].extend(data[k])

    df = pd.DataFrame(all_data)
    if df.empty:
        print("[Error] 没有有效数据，无法绘图。")
        return

    # 绘制折线图
    plt.figure(figsize=(10, 6))
    sns.lineplot(
        data=df,
        x="Number of Cross-Chain Tx",
        y="Latency (s)",
        hue="Method",
        style="Method",
        markers=True,
        dashes=False,
        linewidth=2.5,
        markersize=15,
        palette=palette
    )

    # 设置标签和刻度
    plt.xlabel("Number of Cross-Chain Tx", fontsize=18)
    plt.ylabel("Cumulative Latency (s)", fontsize=18)
    plt.xticks(x_ticks, labels=[f"{int(x/1000)}k" for x in x_ticks], fontsize=16)
    plt.yticks(fontsize=16)

    ax = plt.gca()
    ax.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
    ax.yaxis.get_offset_text().set_fontsize(16)

    plt.legend(fontsize=14)
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.tight_layout()
    
    # -----------------------------
    # 保存到 PDF
    # -----------------------------
    pic_dir = "pic"
    os.makedirs(pic_dir, exist_ok=True)

    # 找到已有文件数量，命名为 latency_CTXNum{n}.pdf
    existing_files = [
        f for f in os.listdir(pic_dir)
        if f.startswith("latency_CTXNum") and f.endswith(".pdf")
    ]
    next_idx = len(existing_files) + 1
    save_path = os.path.join(pic_dir, f"latency_CTXNum{next_idx}.pdf")

    plt.savefig(save_path, format="pdf")
    print(f"[Info] 图像已保存到 {save_path}")

    # 显示图像
    plt.show()

# -----------------------------
# 主入口
# -----------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="跨链交易数 vs 累计延迟 绘图")
    parser.add_argument("--config", type=str, required=True, help="JSON 配置文件路径")
    args = parser.parse_args()
    plot_from_config(args.config)
