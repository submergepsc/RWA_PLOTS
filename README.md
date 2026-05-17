# Plot All 绘图文件结构说明

本文档说明 `run_all_plots.py` 当前串联的 4 个绘图脚本及其相关输入、输出和上游数据文件。

## 运行入口

```text
run_all_plots.py
```

该脚本按顺序执行以下 4 个文件：

```text
plot_2_queue.py
plot_3_throught.py
plot_4_certifycate.py
plot_5_scalability.py
```

推荐运行命令：

```bash
MPLCONFIGDIR=/tmp/matplotlib-cache .venv/bin/python run_all_plots.py
```

`MPLCONFIGDIR=/tmp/matplotlib-cache` 用于避免 Matplotlib 写入用户配置目录失败或反复重建缓存。

## 总体数据流

```text
原始实验结果 CSV
  -> 聚合后的根目录 CSV
  -> plot_2 / plot_3 / plot_4 / plot_5
  -> figures/02_queue
     figures/03_throughput
     figures/04_certificate
     figures/05_scalability
```

当前 4 个绘图脚本都从项目根目录读取 CSV，并把 PDF 写入 `figures/` 下对应子目录。

## 方案列名与显示名

输入 CSV 中使用的列名：

```text
committee
daon
decentruth
seenfeed
deepthought
```

图中显示名：

```text
committee    -> FastOracle
daon         -> DAON
decentruth   -> DECEN.
seenfeed     -> Sen.
deepthought  -> Deep.
```

注意：`certif_gen_pos.csv` 和 `certif_gen_pow.csv` 当前没有 `deepthought` 列，因此 `plot_4_certifycate.py` 的证书图只画 4 条曲线。

## 文件结构

```text
RWAExpResults/
├── run_all_plots.py
├── plot_2_queue.py
├── plot_3_throught.py
├── plot_4_certifycate.py
├── plot_5_scalability.py
├── total_q_len_pos.csv
├── total_q_len_pow.csv
├── total_handled_num_pos.csv
├── total_handled_num_pow.csv
├── certif_gen_pos.csv
├── certif_gen_pow.csv
├── figures/
│   ├── 02_queue/
│   │   ├── queue_dynamics_pos.pdf
│   │   └── queue_dynamics_pow.pdf
│   ├── 03_throughput/
│   │   ├── throughput_stability_pos.pdf
│   │   └── throughput_stability_pow.pdf
│   ├── 04_certificate/
│   │   ├── certificate_cdf_pos.pdf
│   │   └── certificate_cdf_pow.pdf
│   └── 05_scalability/
│       ├── pos_quantity_vs_time.pdf
│       └── pow_quantity_vs_time.pdf
├── gen_certif.py
├── prepare_certif.py
├── prepare.py
├── certif_pos/
│   ├── committee.csv
│   ├── daon.csv
│   ├── decentruth.csv
│   ├── deepthought.csv
│   └── seenfeed.csv
└── 暂时存放不用/
    ├── results_committee/
    ├── results_committee_pow/
    ├── results_daon/
    ├── results_daon_pow/
    ├── results_decentruth/
    ├── results_decentruth_pow/
    ├── results_deepthought/
    ├── results_deepthought_pow/
    ├── results_seenfeed/
    └── results_seenfeed_pow/
```

## 四个绘图脚本

### 1. `plot_2_queue.py`

用途：绘制队列长度随时间变化的曲线图。

输入：

```text
total_q_len_pos.csv
total_q_len_pow.csv
```

输入列：

```text
time, committee, daon, decentruth, seenfeed, deepthought
```

输出：

```text
figures/02_queue/queue_dynamics_pos.pdf
figures/02_queue/queue_dynamics_pow.pdf
```

图形特征：

- x 轴为 `Time (min)`，使用对数坐标。
- y 轴为 `Queue Length`。
- 当前 PDF 页面尺寸统一为 `576 x 432 pts`，用于和 plot3、plot4 三图并排。

### 2. `plot_3_throught.py`

用途：绘制吞吐量稳定性图。

输入：

```text
total_handled_num_pos.csv
total_handled_num_pow.csv
```

输入列：

```text
time, committee, daon, decentruth, seenfeed, deepthought
```

输出：

```text
figures/03_throughput/throughput_stability_pos.pdf
figures/03_throughput/throughput_stability_pow.pdf
```

图形特征：

- PoS 图：时间序列吞吐曲线。
- PoW 图：按方案分行的横向箱线图。
- PoW 每个方案使用独立 x 轴范围，避免不同数量级互相挤压。
- 当前 PDF 页面尺寸统一为 `576 x 432 pts`。

PoW 当前固定刻度：

```text
FastOracle: 13, 33, 53, 72
Deep.:      0.01, 0.04, 0.06, 0.09
Sen.:       13, 14, 15
DECEN.:     9.0, 9.6, 10, 11
DAON:       0.00, 13, 25, 38
```

### 3. `plot_4_certifycate.py`

用途：绘制证书生成数量随时间变化的 CDF/累计曲线。

输入：

```text
certif_gen_pos.csv
certif_gen_pow.csv
```

输入列：

```text
committee, daon, decentruth, seenfeed
```

输出：

```text
figures/04_certificate/certificate_cdf_pos.pdf
figures/04_certificate/certificate_cdf_pow.pdf
```

图形特征：

- x 轴为 `Time (s)`，使用科学记数法刻度。
- y 轴为 `Number of Certificates`。
- 当前带有 `Peak certificates reached.` 标注框和箭头。
- 当前 PDF 页面尺寸统一为 `576 x 432 pts`。

### 4. `plot_5_scalability.py`

用途：绘制处理请求数量与累计处理延迟的关系。

输入：

```text
total_handled_num_pos.csv
total_handled_num_pow.csv
```

输入列：

```text
time, committee, daon, decentruth, seenfeed, deepthought
```

输出：

```text
figures/05_scalability/pos_quantity_vs_time.pdf
figures/05_scalability/pow_quantity_vs_time.pdf
```

图形特征：

- x 轴为 `Processed Request Number`。
- y 轴为 `Cumulative Process Latency`。
- 使用 `total_handled_num_*.csv` 中的累计处理数量反推不同请求规模对应的处理延迟。

## 上游数据生成脚本

### `gen_certif.py`

从各方案的 `consensus.csv` 中生成证书中间数据：

```text
certif_pos/<scheme>.csv
certif_pow/<scheme>.csv
```

其中每个 scheme 文件包含 `since_time` 等证书累计时间数据。

### `prepare_certif.py`

把 `certif_pos/` 和 `certif_pow/` 下的方案级 CSV 合并为：

```text
certif_gen_pos.csv
certif_gen_pow.csv
```

这两个文件是 `plot_4_certifycate.py` 的直接输入。

### `prepare.py`

用于从 `results_*_pow/` 风格的结果目录聚合生成：

```text
total_q_len_pow.csv
total_handled_num_pow.csv
consensusTime_pow.csv
searchTime_pow.csv
onChainTime_pow.csv
```

注意：当前仓库中原始结果目录主要保存在 `暂时存放不用/` 下，而 `prepare.py` 读取的是根目录下的 `results_*_pow/`。直接运行前需要确认目录位置是否匹配。

## LaTeX 引用关系

`main.tex` 中三图并排部分引用：

```text
figure/03_throughput/throughput_stability_pos.pdf
figure/02_queue/queue_dynamics_pos.pdf
figure/04_certificate/certificate_cdf_pos.pdf

figure/03_throughput/throughput_stability_pow.pdf
figure/02_queue/queue_dynamics_pow.pdf
figure/04_certificate/certificate_cdf_pow.pdf
```

当前项目中 `figure` 是指向 `figures` 的软链接，因此脚本输出到 `figures/` 后，LaTeX 中的 `figure/...` 路径可以正常解析。

## 常见维护点

- 修改方案显示名：优先改各绘图脚本顶部的 `PROTOCOLS` 字典。
- 修改输出目录：改 `FIGURES_ROOT` 和 `PLOT_TYPE_NAME` / `SUB_DIR_NAME`。
- 修改 plot2/plot3/plot4 三图并排效果：保持三者 `DEFAULT_FIGSIZE = (8, 6)`，避免某一张被 `bbox_inches="tight"` 裁成不同尺寸。
- 修改 plot4 标注：关注 `Peak certificates reached.` 文本框、箭头边界计算、以及峰值空心圈大小。
- 修改 plot3 PoW 各方案横向范围：改 `POW_AXIS_CONFIG`。

## 快速检查命令

```bash
.venv/bin/python -m py_compile \
  plot_2_queue.py \
  plot_3_throught.py \
  plot_4_certifycate.py \
  plot_5_scalability.py
```

```bash
MPLCONFIGDIR=/tmp/matplotlib-cache .venv/bin/python run_all_plots.py
```

检查 PDF 页面尺寸：

```bash
pdfinfo figures/03_throughput/throughput_stability_pos.pdf
pdfinfo figures/02_queue/queue_dynamics_pos.pdf
pdfinfo figures/04_certificate/certificate_cdf_pos.pdf
```
