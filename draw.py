import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
import typing

def plot_handled_num(df: pd.DataFrame):
    plt.figure(figsize=(12, 8))
    for col in df.columns:
        if col == "time":
            continue
        plt.plot(df["time"], df[col], linewidth=2, label=col)

    plt.legend(fontsize=18)
    plt.xlabel("Time", fontsize=20)
    plt.ylabel("Handled Num", fontsize=20)
    plt.xticks(fontsize=18)
    plt.yticks(fontsize=18)
    plt.tight_layout()
    plt.grid()
    plt.savefig("figure/handled_num.pdf", format="pdf")


def plot_throughpout(df: pd.DataFrame):
    df = df.copy()
    df["new_time"] = df["time"] // 20
    plt.figure(figsize=(12, 8))
    for col in df.columns:
        if col == "time" or col == "new_time":
            continue
        _grouped_res = df.groupby("new_time")[col].sum()
        _res = _grouped_res.diff()
        plt.plot(_res.index, _res, linewidth=2, label=col)

    plt.legend(fontsize=18)
    plt.xlabel("Time", fontsize=20)
    plt.ylabel("Throughput", fontsize=20)
    plt.xticks(fontsize=18)
    plt.yticks(fontsize=18)
    plt.tight_layout()
    plt.grid()
    plt.savefig("figure/throughput.pdf", format="pdf")

def plot_cerification_gen_speed(df: pd.DataFrame):
    df = df.copy()
    df["new_time"] = df["time"] // 20
    plt.figure(figsize=(12, 8))
    for col in df.columns:
        if col == "time" or col == "new_time":
            continue
        _grouped_res = df.groupby("new_time")[col].sum()
        _res = _grouped_res.diff()
        plt.plot(_res.index, _res // 15, linewidth=2, label=col)

    plt.legend(fontsize=18)
    plt.xlabel("Time", fontsize=20)
    plt.ylabel("Cerification Num", fontsize=20)
    plt.xticks(fontsize=18)
    plt.yticks(fontsize=18)
    plt.tight_layout()
    plt.grid()
    plt.savefig("figure/certif_num.pdf", format="pdf")

def plot_queue_length(df: pd.DataFrame):
    plt.figure(figsize=(12, 8))
    for col in df.columns:
        if col == "time":
            continue
        if col == "committee":
            df = df[df[col].abs() > 1e-2 ]
            plt.plot(df["time"], df[col], linewidth=2, label=col)

    plt.legend(fontsize=18)
    plt.xlabel("Time", fontsize=20)
    plt.ylabel("Queue Length", fontsize=20)
    plt.xticks(fontsize=18)
    plt.yticks(fontsize=18)
    plt.tight_layout()
    plt.grid()
    plt.savefig("figure/queue.pdf", format="pdf")

def plot_consensus(_metrics: typing.List):
    for metric in _metrics:
        plt.figure(figsize=(12, 8))
        df = pd.read_csv(f"{metric}.csv")
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
        plt.savefig(f"figure/{metric}.pdf", format="pdf")

if __name__ == "__main__":
    if not os.path.exists("figure"):
        os.makedirs("figure")
    
    df = {}
    for name in ["total_handled_num", "total_q_len"]:
        folder_name = name + ".csv"
        df[name] = pd.read_csv(folder_name)
    
    plot_handled_num(df["total_handled_num"])
    plot_throughpout(df["total_handled_num"])
    plot_cerification_gen_speed(df["total_handled_num"])

    plot_queue_length(df["total_q_len"])
    plot_consensus(["consensusTime", "searchTime", "onChainTime"])