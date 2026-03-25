import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
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
# 处理单个 dataset，计算累计延迟和TPS
# -----------------------------
def process_csv(path, label, k):
    if not os.path.exists(path):
        print(f"[Warning] 文件不存在: {path}")
        return {"Latency (s)": [], "TPS": [], "Method": []}

    df = pd.read_csv(path)
    required_cols = ["Confirmed latency of this tx (ms)", "ccTIS"]
    if not all(col in df.columns for col in required_cols):
        print(f"[Error] 文件 {path} 缺少所需列，跳过")
        return {"Latency (s)": [], "TPS": [], "Method": []}

    if len(df) < k:
        print(f"[Warning] 文件 {path} 交易数量不足 (只 {len(df)} 行)，跳过")
        return {"Latency (s)": [], "TPS": [], "Method": []}

    df = df.sort_values(by="ccTIS")
    data = df["Confirmed latency of this tx (ms)"].iloc[:k]
    
    latency = data.sum() / 1000  # 秒
    tps = k / data.max() * 1000  # TPS

    return {
        "Latency (s)": [latency],
        "TPS": [tps],
        "Method": [label]
    }

# -----------------------------
# 主绘图函数
# -----------------------------
def plot_from_config(config_path):
    config = load_config(config_path)
    datasets = config.get("datasets", [])
    k = config.get("k", 239998)  # 默认使用之前的 k 值
    palette = {ds["label"]: ds.get("color", None) for ds in datasets}

    all_data = {"Latency (s)": [], "TPS": [], "Method": []}
    for ds in datasets:
        path = ds.get("path")
        label = ds.get("label", os.path.basename(path) if path else "Unknown")
        if not path:
            print(f"[Warning] dataset 缺少 path，跳过: {ds}")
            continue
        data = process_csv(path, label, k)
        for key in all_data:
            all_data[key].extend(data[key])

    df = pd.DataFrame(all_data)
    if df.empty:
        print("[Error] 没有有效数据，无法绘图。")
        return

    # -----------------------------
    # 绘图
    # -----------------------------
    plt.figure(figsize=(10, 6))
    sns.lineplot(
        data=df,
        x="Latency (s)",
        y="TPS",
        hue="Method",
        style="Method",
        markers=True,
        dashes=False,
        linewidth=2.5,
        markersize=12,
        palette=palette
    )

    plt.xlabel("CTX Latency (sec.)", fontsize=18)
    plt.ylabel("CTX Throughput (TPS)", fontsize=18)
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)

    plt.grid(True, linestyle="--", alpha=0.6)
    plt.legend(fontsize=14)
    plt.tight_layout()

    # -----------------------------
    # 保存到 PDF
    # -----------------------------
    pic_dir = "pic"
    os.makedirs(pic_dir, exist_ok=True)
    existing_files = [f for f in os.listdir(pic_dir) if f.startswith("latency_CTX") and f.endswith(".pdf")]
    next_idx = len(existing_files) + 1
    save_path = os.path.join(pic_dir, f"latency_CTX{next_idx}.pdf")
    plt.savefig(save_path, format="pdf")
    print(f"[Info] 图像已保存到 {save_path}")
    plt.show()

# -----------------------------
# 主入口
# -----------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CTX Latency vs Throughput 绘图")
    parser.add_argument("--config", type=str, required=True, help="JSON 配置文件路径")
    args = parser.parse_args()
    plot_from_config(args.config)
