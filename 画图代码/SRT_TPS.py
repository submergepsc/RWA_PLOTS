import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from collections import Counter
import json
import argparse
import os

# -----------------------------
# 读取配置文件
# -----------------------------
def load_config(config_path):
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"配置文件不存在: {config_path}")
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)

# -----------------------------
# 处理单个 CSV 数据
# -----------------------------
def process_csv(path, label, idx_start=4, idx_end=4):
    if not os.path.exists(path):
        print(f"[Warning] File not found: {path}")
        return {"System Running Time": [], "TPS": [], "Method": []}

    df = pd.read_csv(path)
    if 'ccTMC' not in df.columns or 'ccTIS' not in df.columns:
        print(f"[Error] {path} 缺少 'ccTMC' 或 'ccTIS' 列，跳过")
        return {"System Running Time": [], "TPS": [], "Method": []}

    time2tps = {"System Running Time": [], "TPS": [], "Method": []}

    try:
        data_mint = (df['ccTMC'] - df['ccTIS'].min()) / 1000
        time_counter = Counter(data_mint)
        times = sorted(time_counter.keys())
        txs_num = [time_counter[t] for t in times]
        txs_sum = 0

        for i, t in enumerate(times):
            if t <= 0:  # 避免除零
                continue
            txs_sum += txs_num[i]
            time2tps['System Running Time'].append(t)
            time2tps['TPS'].append(txs_sum / t)

        # 添加起点
        time2tps['System Running Time'].append(0)
        time2tps['TPS'].append(0)
    except Exception as e:
        print(f"[Error] 处理 {path} 出错: {e}")
        return {"System Running Time": [], "TPS": [], "Method": []}

    # 添加 Method 标签
    time2tps['Method'] = [label] * len(time2tps['System Running Time'])
    return time2tps

# -----------------------------
# 主绘图函数
# -----------------------------
def plot_from_config(config_path, max_time=None):
    config = load_config(config_path)
    datasets = config.get("datasets", [])
    if not datasets:
        print("[Warning] 配置文件中没有 datasets，退出。")
        return

    idx_start = config.get("idx_start", 4)
    idx_end = config.get("idx_end", 4)

    # 合并所有 dataset 数据
    all_data = {"System Running Time": [], "TPS": [], "Method": []}
    for ds in datasets:
        path = ds.get("path")
        label = ds.get("label", os.path.basename(path) if path else "Unknown")

        if not path:
            print(f"[Warning] dataset 缺少 path，跳过: {ds}")
            continue

        tps_data = process_csv(path, label, idx_start, idx_end)
        all_data['System Running Time'].extend(tps_data['System Running Time'])
        all_data['TPS'].extend(tps_data['TPS'])
        all_data['Method'].extend(tps_data['Method'])

    if not all_data['System Running Time']:
        print("[Error] 没有有效数据，无法绘图。")
        return

    df = pd.DataFrame(all_data)

    if max_time:
        df = df[df['System Running Time'] <= max_time]

    palette = {d.get("label", os.path.basename(d.get("path", "Unknown"))): d.get("color", None)
               for d in datasets}

    fig, ax = plt.subplots(figsize=(8,6))
    sns.lineplot(
        data=df,
        x='System Running Time',
        y='TPS',
        hue='Method',
        style='Method',
        errorbar=None,  # 避免 sd 在样本过少时报错
        ax=ax,
        linewidth=2.5,
        palette=palette
    )

    ax.set_xlabel('System Running Time (sec.)', fontsize=20)
    ax.set_ylabel('Throughput (TPS)', fontsize=20)
    ax.tick_params(axis='both', labelsize=16)
    ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    ax.grid(True, linestyle='--', alpha=0.5)
    plt.legend(fontsize=12, loc='upper right')
    plt.tight_layout()

    # -----------------------------
    # 保存到 PDF
    # -----------------------------
    pic_dir = "pic"
    os.makedirs(pic_dir, exist_ok=True)

    existing_files = [
        f for f in os.listdir(pic_dir)
        if f.startswith("SRT_TPS") and f.endswith(".pdf")
    ]
    next_idx = len(existing_files) + 1
    save_path = os.path.join(pic_dir, f"SRT_TPS{next_idx}.pdf")

    plt.savefig(save_path, format="pdf")
    print(f"[Info] 图像已保存到 {save_path}")

    # 显示图像
    plt.show()

# -----------------------------
# 主入口
# -----------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="健壮 TPS 绘图")
    parser.add_argument("--config", type=str, required=True, help="JSON 配置路径")
    parser.add_argument("--max_time", type=float, default=None, help="显示最大系统时间")
    args = parser.parse_args()

    plot_from_config(args.config, max_time=args.max_time)
