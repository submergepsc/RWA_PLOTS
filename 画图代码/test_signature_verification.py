import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
import argparse
import numpy as np

# -----------------------------
# 读取配置文件
# -----------------------------
def load_config(config_path):
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"配置文件不存在: {config_path}")
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)

# -----------------------------
# 处理单个 CSV，计算累计 CTX 数量
# -----------------------------
def process_csv(path, label, max_time=10000, interval=1):
    if not os.path.exists(path):
        print(f"[Warning] 文件不存在: {path}")
        return {"Time (s)": [], "CTX Count": [], "Method": []}

    df = pd.read_csv(path)
    if not all(col in df.columns for col in ["ccTPG", "ccTIS"]):
        print(f"[Error] 文件 {path} 缺少所需列，跳过")
        return {"Time (s)": [], "CTX Count": [], "Method": []}

    # 计算每笔交易的相对时间
    relative_time = (df['ccTPG'] - df['ccTIS'].min()) / 1000

    # 按时间间隔统计 CTX 数量
    times = np.arange(0, max_time, interval)
    counts = [((relative_time >= t) & (relative_time < t + interval)).sum() for t in times]

    # 避免对数刻度报错，将 0 替换为 1
    counts = [c if c > 0 else 1 for c in counts]

    return {
        "Time (s)": times.tolist(),
        "CTX Count": counts,
        "Method": [label] * len(times)
    }

# -----------------------------
# 主绘图函数
# -----------------------------
def plot_from_config(config_path):
    config = load_config(config_path)
    datasets = config.get("datasets", [])
    interval = config.get("interval", 1)

    if not datasets:
        print("[Error] 配置文件中没有 datasets")
        return

    # 处理所有数据集
    all_data = {"Time (s)": [], "CTX Count": [], "Method": []}
    palette = {}
    for ds in datasets:
        path = ds.get("path")
        label = ds.get("label", os.path.basename(path) if path else "Unknown")
        color = ds.get("color", None)
        palette[label] = color
        max_time = ds.get("max_time", 10000)  # 可以通过配置文件设置
        data = process_csv(path, label, max_time=max_time, interval=interval)
        for key in all_data:
            all_data[key].extend(data[key])

    df = pd.DataFrame(all_data)
    if df.empty:
        print("[Error] 没有有效数据，无法绘图。")
        return

    # -----------------------------
    # 绘制一张总图
    # -----------------------------
    plt.figure(figsize=(10, 6))
    sns.lineplot(
        data=df,
        x="Time (s)",
        y="CTX Count",
        hue="Method",
        style="Method",
        markers=True,
        dashes=False,
        linewidth=2.5,
        markersize=10,
        palette=palette
    )

    plt.xlabel("System Running Time (sec.)", fontsize=18)
    plt.ylabel("Number of CTXs Certificates", fontsize=18)
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)
    plt.yscale("log")  # 对数刻度
    plt.grid(True, alpha=0.3, which="both")  # 对数刻度下显示网格
    plt.legend(fontsize=14, loc='upper left')
    plt.tight_layout()

    # -----------------------------
    # 保存 PDF
    # -----------------------------
    pic_dir = "pic"
    os.makedirs(pic_dir, exist_ok=True)
    existing_files = [f for f in os.listdir(pic_dir) if f.startswith("CTX_Count") and f.endswith(".pdf")]
    next_idx = len(existing_files) + 1
    save_path = os.path.join(pic_dir, f"test_signature_verification_{next_idx}.pdf")
    plt.savefig(save_path, format="pdf")
    print(f"[Info] 图像已保存到 {save_path}")

    plt.show()

# -----------------------------
# 主入口
# -----------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CTX Count vs System Running Time 绘图")
    parser.add_argument("--config", type=str, required=True, help="JSON 配置文件路径")
    args = parser.parse_args()
    plot_from_config(args.config)
