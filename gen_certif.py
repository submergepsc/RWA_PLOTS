import shutil
from pathlib import Path

import pandas as pd


def simple_parse(time_str):
    if not time_str.endswith("s"):
        raise SystemError("format error")
    time_str = time_str[:-1]
    if "m" not in time_str:
        return float(time_str)
    else:
        parts = time_str.split("m")
        if len(parts) != 2:
            raise ValueError(f"Invalid format: {time_str}")
        minutes = float(parts[0])
        seconds = float(parts[1])
        return minutes * 60 + seconds


for method in ["pow", "pos"]:
    results_folder_name = "certif_" + method

    folder_path = Path(results_folder_name)

    if folder_path.exists():
        shutil.rmtree(folder_path)

    folder_path.mkdir()
    for scheme in ["committee", "daon", "decentruth", "deepthought", "seenfeed"]:
        print(f"start {method}-{scheme}")
        folder_name = "results_" + scheme + ("_pow" if method == "pow" else "")
        df = pd.read_csv(folder_name + "/consensus.csv")
        for col in ["consensusTime", "searchTime"]:
            df[col] = df[col].apply(simple_parse)
        df["total_time"] = df["consensusTime"] + df["searchTime"]

        df = df[["total_time", "comId", "seqId"]]
        assert isinstance(df, pd.DataFrame)

        committeeSize = df["comId"].nunique()

        df_list = []

        for comId in df["comId"].unique():
            com_df = df[df["comId"] == comId]
            assert isinstance(com_df, pd.DataFrame)
            com_df = com_df.sort_values(by="seqId").reset_index(drop=True)
            com_df["newSeqId"] = com_df.index + 1
            com_df["newRoundId"] = (com_df["newSeqId"] // 15).astype(int)

            group_df = com_df.groupby("newRoundId")[["total_time"]].max().reset_index()
            group_df["since_time"] = group_df["total_time"].cumsum()
            group_df["certId"] = group_df["newRoundId"] * committeeSize + comId

            df_list.append(group_df)

        result = pd.concat(df_list)

        result = result.sort_values(by="certId").reset_index(drop=True)

        # result["time_counter"] = (result["since_time"] // 5).astype(int) * 5 + 1

        # final_res = result.groupby("time_counter").size().reset_index(name="count")  # type: ignore

        result.to_csv(results_folder_name + "/" + scheme + ".csv", index=False)
