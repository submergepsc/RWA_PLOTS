import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
import typing

def plot_handled_num(df: pd.DataFrame, out_dir: str = "figure", use_log_time: bool = False):
    plt.figure(figsize=(12, 8))
    for col in df.columns:
        if col == "time":
            continue
        if use_log_time:
            x_vals = np.log(np.asarray(df["time"]).astype(float))
        else:
            x_vals = df["time"]
        plt.plot(x_vals, df[col], linewidth=2, label=col)

    plt.legend(fontsize=18)
    plt.xlabel("Log Time" if use_log_time else "Time", fontsize=20)
    plt.ylabel("Handled Num", fontsize=20)
    plt.xticks(fontsize=18)
    plt.yticks(fontsize=18)
    plt.tight_layout()
    plt.grid()
    os.makedirs(out_dir, exist_ok=True)
    plt.savefig(os.path.join(out_dir, "handled_num.pdf"), format="pdf")


def plot_throughpout(df: pd.DataFrame, out_dir: str = "figure", use_log_time: bool = False, bios: float = 550):
    df = df.copy()
    df["new_time"] = df["time"]
    # 仅保留 time > bios
    df = df[df["new_time"] > bios]
    plt.figure(figsize=(12, 8))
    for col in df.columns:
        if col == "time" or col == "new_time":
            continue
        _grouped_res = df.groupby("new_time")[col].sum()
        _res = _grouped_res.diff()
        # 选择 x 值：默认用原索引，否则取 log（假定均为大于1的正数）
        if use_log_time:
            x_vals = np.log(np.asarray(_res.index - bios).astype(float))
        else:
            x_vals = _res.index
        plt.plot(x_vals, _res, linewidth=2, label=col)

    plt.legend(fontsize=18)
    plt.xlabel(f"{'Log Time' if use_log_time else 'Time'} (t>{bios} & t -= {bios})", fontsize=20)
    plt.ylabel("Throughput", fontsize=20)
    plt.xticks(fontsize=18)
    plt.yticks(fontsize=18)
    plt.tight_layout()
    plt.grid()
    os.makedirs(out_dir, exist_ok=True)
    plt.savefig(os.path.join(out_dir, "throughput.pdf"), format="pdf")

def plot_cerification_gen_speed(df: pd.DataFrame, out_dir: str = "figure", use_log_time: bool = False, bios: float = 550):
    df = df.copy()
    df["new_time"] = df["time"]
    # 仅保留 time > bios
    df = df[df["new_time"] > bios]
    plt.figure(figsize=(12, 8))
    for col in df.columns:
        if col == "time" or col == "new_time":
            continue
        _grouped_res = df.groupby("new_time")[col].sum()
        _res = _grouped_res.diff()
        # 选择 x 值：默认用原索引，否则取 log（假定均为大于1的正数）
        if use_log_time:
            x_vals = np.log(np.asarray(_res.index - bios).astype(float))
        else:
            x_vals = _res.index
        plt.plot(x_vals, _res // 15, linewidth=2, label=col)

    plt.legend(fontsize=18)
    plt.xlabel(f"{'Log Time' if use_log_time else 'Time'} (t>{bios} & t -= {bios})", fontsize=20)
    plt.ylabel("Cerification Num", fontsize= 20)
    plt.xticks(fontsize=18)
    plt.yticks(fontsize=18)
    plt.tight_layout()
    plt.grid()
    os.makedirs(out_dir, exist_ok=True)
    plt.savefig(os.path.join(out_dir, "certif_num.pdf"), format="pdf")

def plot_queue_length(df: pd.DataFrame, out_dir: str = "figure", use_log_time: bool = False):
    plt.figure(figsize=(12, 8))
    for col in df.columns:
        if col == "time":
            continue

        if use_log_time:
            x_vals = np.log(df["time"].astype(float))
        else:
            x_vals = df["time"]
        plt.plot(x_vals, df[col], linewidth=2, label=col)

    plt.legend(fontsize=18)
    plt.xlabel("Log Time" if use_log_time else "Time", fontsize=20)
    plt.ylabel("Queue Length", fontsize=20)
    plt.xticks(fontsize=18)
    plt.yticks(fontsize=18)
    plt.tight_layout()
    plt.grid()
    os.makedirs(out_dir, exist_ok=True)
    plt.savefig(os.path.join(out_dir, "queue.pdf"), format="pdf")

def plot_consensus(_metrics: typing.List, out_dir: str = "figure"):
    for metric in _metrics:
        plt.figure(figsize=(12, 8))
        df = pd.read_csv(f"{metric}_pow.csv")
        for col in df.columns:
            if col == "seqId":
                continue
            extracted = df[col].str.extract(r'^(\d+\.?\d*)\s*(ms|s)$', flags=0)

            values = extracted[0].astype(float)
            units = extracted[1]

            _res = np.where(units == 'ms', values / 1000.0, values)

            plt.plot(df["seqId"], _res, linewidth=2, label=col)
        plt.legend(fontsize=18)
        plt.xlabel("Sequence Id", fontsize=20)
        plt.ylabel("Time", fontsize=20)
        plt.xticks(fontsize=18)
        plt.yticks(fontsize=18)
        plt.title(metric, fontsize= 24)
        plt.tight_layout()
        plt.grid()
        os.makedirs(out_dir, exist_ok=True)
        plt.savefig(os.path.join(out_dir, f"{metric}.pdf"), format="pdf")

if __name__ == "__main__":
    fig_dir = "figure_pow"
    if not os.path.exists(fig_dir):
        os.makedirs(fig_dir)
    
    df = {}
    for name in ["total_handled_num", "total_q_len"]:
        folder_name = name + "_pow.csv"
        df[name] = pd.read_csv(folder_name)
    
    plot_handled_num(df["total_handled_num"], out_dir=fig_dir, use_log_time=True)
    plot_throughpout(df["total_handled_num"], out_dir=fig_dir, use_log_time=True)
    plot_cerification_gen_speed(df["total_handled_num"], out_dir=fig_dir, use_log_time=True)

    plot_queue_length(df["total_q_len"], out_dir=fig_dir, use_log_time=True)
    plot_consensus(["consensusTime", "searchTime", "onChainTime"], out_dir=fig_dir)