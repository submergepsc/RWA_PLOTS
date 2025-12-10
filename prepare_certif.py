import pandas as pd

for method in ["pow", "pos"]:
    res = pd.DataFrame()
    for scheme in ["committee", "daon", "decentruth", "deepthought", "seenfeed"]:
        file_name = "certif_" + method + "/" + scheme + ".csv"
        df = pd.read_csv(file_name)
        res[scheme] = df["since_time"]
    res.to_csv("certif_gen_" + method + ".csv", index=False)