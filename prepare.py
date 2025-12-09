import pandas as pd

METHOD_LIST = ["committee", "daon", "decentruth", "seenfeed", "deepthought"]

MAX_REQUEST_NUM = 20000

result_df = {"handled_num": {}, "q_len": {}}

for method in METHOD_LIST:
    folder_name = "results_" + method + "_pow/sec.csv"
    df = pd.read_csv(folder_name)
    df = df.sort_values(by="time").reset_index(drop=True)
    
    df = df.groupby("time")[["q_len", "handled_num"]].sum()

    df["q_len"] = df["q_len"].clip(lower=0, upper=MAX_REQUEST_NUM)
    df["handled_num"] = df["handled_num"].clip(lower=0, upper=MAX_REQUEST_NUM)

    for metric in ["q_len", "handled_num"]:
        result_df[metric][method] = df[metric]

for metric in ["q_len", "handled_num"]:
    res_dict = result_df[metric]

    res_df = pd.DataFrame(res_dict)

    if metric == "handled_num":
        res_df = res_df.fillna(MAX_REQUEST_NUM)
    else:
        res_df = res_df.fillna(0)

    res_df.to_csv(f"total_{metric}_pow.csv")


for metric in ["consensusTime", "searchTime", "onChainTime"]:
    res_df = {}
    for method in METHOD_LIST:
        folder_name = "results_" + method + "_pow/consensus.csv"
        df = pd.read_csv(folder_name)
        df = df.sort_values(by="seqId").reset_index(drop=True)
        res_df[method] = df[metric]
        res_df["seqId"] = df["seqId"]

    res_df = pd.DataFrame(res_df)
    res_df.to_csv(f"{metric}_pow.csv", index= False)