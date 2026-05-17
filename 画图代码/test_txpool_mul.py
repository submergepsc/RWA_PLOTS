import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import json
import os
import argparse
import matplotlib.ticker as ticker

# -----------------------------
# 读取配置文件
# -----------------------------
def load_config(config_path):
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"配置文件不存在: {config_path}")
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)

# -----------------------------
# 计算交易池大小
# -----------------------------
def count_txpool(data, interval=1, max_time=24000):
    required_cols = ['ccTLS', 'ccTSD', 'ccTIS']
    for col in required_cols:
        if col not in data.columns:
            raise ValueError(f"CSV 缺少必要列 '{col}'，当前列为: {data.columns.tolist()}")

    data_listen = (data['ccTLS'] - data['ccTIS'].min()) / 1000
    data_send = (data['ccTSD'] - data['ccTIS'].min()) / 1000

    counts_txpool = []
    txpool_size = 0
    start_time = 0
    end_time = start_time + interval

    while end_time <= max_time:
        count_listen = len(data_listen[(data_listen >= start_time) & (data_listen < end_time)])
        count_send = len(data_send[(data_send >= start_time) & (data_send < end_time)])
        txpool_size += count_listen - count_send
        counts_txpool.append(txpool_size)
        start_time += interval
        end_time += interval

    return counts_txpool

# -----------------------------
# 绘图函数
# -----------------------------
def plot_txpool(config_path, interval=1, max_time=24000):
    config = load_config(config_path)
    datasets = config.get("datasets", [])
    if not datasets:
        print("[Warning] 配置文件中没有 datasets，退出。")
        return

    results = []
    for ds in datasets:
        path = ds.get("path")
        label = ds.get("label", os.path.basename(path) if path else "Unknown")
        color = ds.get("color", None)

        if not path or not os.path.exists(path):
            print(f"[Warning] CSV 文件不存在或未指定路径，跳过: {path}")
            continue

        try:
            df = pd.read_csv(path)
            txpool = count_txpool(df, interval=interval, max_time=max_time)
            results.append({
                'label': label,
                'txpool': txpool,
                'color': color
            })
        except Exception as e:
            print(f"[Error] 处理 {path} 失败: {e}")
            continue

    if not results:
        print("[Error] 没有有效数据，无法绘图。")
        return

    # -----------------------------
    # 绘图
    # -----------------------------
    plt.figure(figsize=(10, 6))
    colors = [r['color'] if r['color'] else c for r, c in zip(results, plt.cm.tab10(np.linspace(0, 1, len(results))))]

    for res, color in zip(results, colors):
        time_range = np.arange(0, len(res['txpool']) * interval, interval)
        plt.plot(time_range, res['txpool'], label=res['label'], color=color, linewidth=2)

    # 图表美化
    plt.xlabel('System Running Time (s)', fontsize=16)
    plt.ylabel('Committee Txpool Size', fontsize=16)
    plt.title('Comparison of Committee Txpool Size', fontsize=18)
    plt.grid(True, alpha=0.3)
    plt.legend(fontsize=12)
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)

    ax = plt.gca()
    ax.xaxis.set_major_formatter(ticker.ScalarFormatter(useMathText=True))
    ax.xaxis.offsetText.set_visible(False)

    plt.tight_layout()

    # -----------------------------
    # 保存 PDF
    # -----------------------------
    pic_dir = "pic"
    os.makedirs(pic_dir, exist_ok=True)

    existing_files = [
        f for f in os.listdir(pic_dir)
        if f.startswith("test_txpool_mul") and f.endswith(".pdf")
    ]
    next_idx = len(existing_files) + 1
    save_path = os.path.join(pic_dir, f"test_txpool_mul{next_idx}.pdf")
    plt.savefig(save_path, format="pdf")
    print(f"[Info] 图像已保存到 {save_path}")

    # 显示图像
    plt.show()

# -----------------------------
# 主入口
# -----------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="健壮 Txpool 绘图")
    parser.add_argument("--config", type=str, required=True, help="JSON 配置路径")
    parser.add_argument("--interval", type=float, default=1, help="时间间隔（秒）")
    parser.add_argument("--max_time", type=float, default=24000, help="最大系统运行时间")
    args = parser.parse_args()

    plot_txpool(args.config, interval=args.interval, max_time=args.max_time)
