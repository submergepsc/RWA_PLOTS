# RWAExpResults 绘图与数据结构说明

本项目是 FastOracle/RWA 论文实验图的整理目录。当前有效工作流主要包括：

1. 根目录 CSV 作为绘图输入。
2. `plot_1_stacked_bars.py` 到 `plot_5_scalability.py` 生成论文图。
3. `figures/` 保存生成的 PDF。
4. `main.tex` 通过 `figure -> figures` 软链接引用这些 PDF。

本文只说明当前仍在使用的文件和数据链路。目录中还有一些历史脚本、调试图片、旧版输出、压缩包和临时目录，本文不把它们作为主流程的一部分。

## 快速运行

项目 Python 环境在：

```bash
.venv/bin/python
```

推荐使用：

```bash
MPLCONFIGDIR=/tmp/matplotlib-cache .venv/bin/python plot_1_stacked_bars.py
MPLCONFIGDIR=/tmp/matplotlib-cache .venv/bin/python run_all_plots.py
```

说明：

- `plot_1_stacked_bars.py` 生成论文中的 latency breakdown 图。
- `run_all_plots.py` 当前只串联运行 `plot_2_queue.py`、`plot_3_throught.py`、`plot_4_certifycate.py`、`plot_5_scalability.py`。
- `MPLCONFIGDIR=/tmp/matplotlib-cache` 用来避免 Matplotlib 写入默认缓存目录失败。

语法检查：

```bash
.venv/bin/python -m py_compile \
  plot_1_stacked_bars.py \
  plot_2_queue.py \
  plot_3_throught.py \
  plot_4_certifycate.py \
  plot_5_scalability.py \
  run_all_plots.py
```

## 当前核心文件结构

```text
RWAExpResults/
├── main.tex
├── main.pdf
├── figure -> figures
├── figures/
│   ├── 01_breakdown/
│   │   ├── stacked_breakdown_pos.pdf
│   │   └── stacked_breakdown_pow.pdf
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
├── plot_1_stacked_bars.py
├── plot_2_queue.py
├── plot_3_throught.py
├── plot_4_certifycate.py
├── plot_5_scalability.py
├── run_all_plots.py
├── searchTime_pos.csv
├── searchTime_pow.csv
├── consensusTime_pos.csv
├── consensusTime_pow.csv
├── onChainTime_pos.csv
├── onChainTime_pow.csv
├── total_q_len_pos.csv
├── total_q_len_pow.csv
├── total_handled_num_pos.csv
├── total_handled_num_pow.csv
├── certif_gen_pos.csv
├── certif_gen_pow.csv
├── gen_certif.py
├── prepare_certif.py
├── prepare.py
└── certif_pos/
```

## 数据列名与图中显示名

根目录 CSV 里使用内部方案列名：

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

注意：`certif_gen_pos.csv` 和 `certif_gen_pow.csv` 当前没有 `deepthought` 列，所以证书图只画 4 个方案。

## 数据总流程

当前绘图主要使用已经聚合好的根目录 CSV：

```text
实验原始结果
  -> 聚合/整理脚本生成根目录 CSV
  -> plot_1 ~ plot_5 读取根目录 CSV
  -> figures/01_breakdown ~ figures/05_scalability 输出 PDF
  -> main.tex 通过 figure/... 引用 PDF
```

其中 `figure` 是指向 `figures` 的软链接：

```text
figure -> figures
```

因此脚本输出到 `figures/...` 后，`main.tex` 中的 `figure/...` 路径可以正常找到图片。

## 根目录 CSV 的用途

### 阶段耗时 CSV

```text
searchTime_pos.csv
searchTime_pow.csv
consensusTime_pos.csv
consensusTime_pow.csv
onChainTime_pos.csv
onChainTime_pow.csv
```

列结构：

```text
committee, seqId, daon, decentruth, seenfeed, deepthought
```

用途：

- 被 `plot_1_stacked_bars.py` 读取。
- 用来计算每个方案的平均 Search、Consensus、On-chain 时间。
- 生成 `figures/01_breakdown/*.pdf`。

其中时间值可能带单位，例如 `ms`、`s`、`ns`。`plot_1_stacked_bars.py` 里的 `clean_time_data()` 会把它们统一换算成秒。

### 队列长度 CSV

```text
total_q_len_pos.csv
total_q_len_pow.csv
```

列结构：

```text
time, committee, daon, decentruth, seenfeed, deepthought
```

用途：

- 被 `plot_2_queue.py` 读取。
- `time` 会转换成分钟：`time_min = time / 60.0`。
- 各方案列表示对应时间点的队列长度。
- 生成 `figures/02_queue/queue_dynamics_pos.pdf` 和 `queue_dynamics_pow.pdf`。

### 累计处理数量 CSV

```text
total_handled_num_pos.csv
total_handled_num_pow.csv
```

列结构：

```text
time, committee, daon, decentruth, seenfeed, deepthought
```

用途一：

- 被 `plot_3_throught.py` 读取。
- 脚本用相邻时间点的累计处理数量差分计算吞吐量：

```text
TPS = handled_num.diff() / time.diff()
```

- 生成 `figures/03_throughput/throughput_stability_pos.pdf` 和 `throughput_stability_pow.pdf`。

用途二：

- 被 `plot_5_scalability.py` 读取。
- 脚本把累计处理数量作为 x 轴，把行索引近似作为累计处理延迟。
- 生成 `figures/05_scalability/pos_quantity_vs_time.pdf` 和 `pow_quantity_vs_time.pdf`。

### 证书生成 CSV

```text
certif_gen_pos.csv
certif_gen_pow.csv
```

列结构：

```text
committee, daon, decentruth, seenfeed
```

用途：

- 被 `plot_4_certifycate.py` 读取。
- 每列是一种方案的证书累计生成时间序列。
- 脚本对每列排序后绘制累计证书数量曲线。
- 生成 `figures/04_certificate/certificate_cdf_pos.pdf` 和 `certificate_cdf_pow.pdf`。

## 绘图脚本说明

### `plot_1_stacked_bars.py`

输入：

```text
searchTime_pos.csv
consensusTime_pos.csv
onChainTime_pos.csv
searchTime_pow.csv
consensusTime_pow.csv
onChainTime_pow.csv
```

输出：

```text
figures/01_breakdown/stacked_breakdown_pos.pdf
figures/01_breakdown/stacked_breakdown_pow.pdf
```

功能：

- 计算 Search、Consensus、On-chain 三个阶段的平均耗时。
- 每个方案画一条横向堆叠柱。
- PoW 图中因为数值跨度较大，脚本使用断轴布局。

### `plot_2_queue.py`

输入：

```text
total_q_len_pos.csv
total_q_len_pow.csv
```

输出：

```text
figures/02_queue/queue_dynamics_pos.pdf
figures/02_queue/queue_dynamics_pow.pdf
```

功能：

- 画队列长度随时间变化。
- x 轴为分钟，使用 log scale。
- 当前页面尺寸为 `8 x 6 in`，PDF 为 `576 x 432 pts`，用于和 plot3、plot4 三图并排。

### `plot_3_throught.py`

输入：

```text
total_handled_num_pos.csv
total_handled_num_pow.csv
```

输出：

```text
figures/03_throughput/throughput_stability_pos.pdf
figures/03_throughput/throughput_stability_pow.pdf
```

功能：

- 从累计处理数量差分得到吞吐量。
- PoS 输出时间序列吞吐曲线，并标注请求全部处理完成点。
- PoW 输出按方案分行的横向箱线图。
- PoW 中不同方案的 TPS 数量级差异较大，所以通过 `POW_AXIS_CONFIG` 为每行设置独立 x 轴范围和刻度。
- 当前页面尺寸为 `8 x 6 in`，PDF 为 `576 x 432 pts`。

### `plot_4_certifycate.py`

输入：

```text
certif_gen_pos.csv
certif_gen_pow.csv
```

输出：

```text
figures/04_certificate/certificate_cdf_pos.pdf
figures/04_certificate/certificate_cdf_pow.pdf
```

功能：

- 画证书数量随时间累计增长的曲线。
- x 轴是秒，使用科学记数法。
- 标注 `Peak certificates reached.`，箭头从文本框真实边界连到 FastOracle 峰值点。
- 当前页面尺寸为 `8 x 6 in`，PDF 为 `576 x 432 pts`。

### `plot_5_scalability.py`

输入：

```text
total_handled_num_pos.csv
total_handled_num_pow.csv
```

输出：

```text
figures/05_scalability/pos_quantity_vs_time.pdf
figures/05_scalability/pow_quantity_vs_time.pdf
```

功能：

- 画处理请求数量与累计处理延迟关系。
- x 轴是处理请求数量。
- y 轴是累计处理延迟。
- 当前脚本会先扫描 pos/pow 的全局最大处理数量，确保两张图的 x 轴范围一致。

## 批量运行脚本

### `run_all_plots.py`

当前按顺序运行：

```text
plot_2_queue.py
plot_3_throught.py
plot_4_certifycate.py
plot_5_scalability.py
```

注意：它当前不包含 `plot_1_stacked_bars.py`。如果要完整更新论文中所有 01 到 05 的实验图，需要先单独运行 `plot_1_stacked_bars.py`，再运行 `run_all_plots.py`。

## 上游生成脚本

### `gen_certif.py`

用途：

- 从各方案目录中的 `consensus.csv` 生成方案级证书时间数据。

读取路径模式：

```text
results_<scheme>/consensus.csv
results_<scheme>_pow/consensus.csv
```

输出路径模式：

```text
certif_pos/<scheme>.csv
certif_pow/<scheme>.csv
```

当前仓库中能看到 `certif_pos/`，但 `certif_pow/` 不一定总是存在。运行前要确认原始 `results_*` 目录是否在根目录，或者是否还在 `暂时存放不用/` 下。

### `prepare_certif.py`

用途：

- 合并 `certif_pos/` 和 `certif_pow/` 下的方案级 CSV。

读取：

```text
certif_pos/committee.csv
certif_pos/daon.csv
certif_pos/decentruth.csv
certif_pos/deepthought.csv
certif_pos/seenfeed.csv
certif_pow/committee.csv
certif_pow/daon.csv
certif_pow/decentruth.csv
certif_pow/deepthought.csv
certif_pow/seenfeed.csv
```

输出：

```text
certif_gen_pos.csv
certif_gen_pow.csv
```

当前 `certif_gen_*.csv` 实际只有 `committee`、`daon`、`decentruth`、`seenfeed` 这 4 列，因此 plot4 不画 `Deep.`。

### `prepare.py`

用途：

- 从 `results_*_pow/` 下的 `sec.csv` 和 `consensus.csv` 生成 PoW 聚合 CSV。

输出：

```text
total_q_len_pow.csv
total_handled_num_pow.csv
consensusTime_pow.csv
searchTime_pow.csv
onChainTime_pow.csv
```

注意：

- 这是上游聚合脚本，不是常规出图入口。
- 当前项目中的原始结果目录主要被放在 `暂时存放不用/` 下；如果要重新跑 `prepare.py`，需要先确认路径是否匹配脚本中的 `results_<method>_pow/...`。

## LaTeX 中的引用关系

`main.tex` 当前引用这些实验图：

```text
figure/01_breakdown/stacked_breakdown_pos.pdf
figure/01_breakdown/stacked_breakdown_pow.pdf
figure/05_scalability/pos_quantity_vs_time.pdf
figure/05_scalability/pow_quantity_vs_time.pdf
figure/03_throughput/throughput_stability_pos.pdf
figure/02_queue/queue_dynamics_pos.pdf
figure/04_certificate/certificate_cdf_pos.pdf
figure/03_throughput/throughput_stability_pow.pdf
figure/02_queue/queue_dynamics_pow.pdf
figure/04_certificate/certificate_cdf_pow.pdf
```

因为 `figure` 是指向 `figures` 的软链接，所以这些路径对应脚本生成的 `figures/...` 文件。

## 不作为当前主流程说明的文件

以下类型文件没有纳入本文主流程：

- `draw.py`、`draw_improved.py`、`plot_advanced.py`、`plot_comparison.py`、`plot_full_8_analysis.py` 等历史/替代绘图脚本。
- `tmp_fig/`、`tmp_debug/`、`debug_*.png`、`test_*.png` 等调试输出。
- `figs_*`、`figs_recreated/`、`figs_pos_basic3/`、`figs_pow_basic3/` 等旧版输出目录。
- 压缩包、PDF 文献、PPT 等非当前绘图流程文件。
- `暂时存放不用/` 下的原始或历史结果目录，除非需要重新生成根目录聚合 CSV。

这些文件可能仍有参考价值，但不是当前 `main.tex` 和 `figures/01~05` 论文图的主要生成链路。

## 常见维护点

- 改方案显示名：修改各 `plot_*.py` 顶部的 `PROTOCOLS`。
- 改 plot3 PoW 每行 x 轴范围：修改 `plot_3_throught.py` 中的 `POW_AXIS_CONFIG`。
- 改 plot4 标注：修改 `plot_4_certifycate.py` 中 `Peak certificates reached.` 附近的文本框、箭头和峰值圈逻辑。
- 保持三图并排尺寸一致：`plot_2_queue.py`、`plot_3_throught.py`、`plot_4_certifycate.py` 应保持 `DEFAULT_FIGSIZE = (8, 6)`，并避免对其中某一张使用 tight 裁切导致页面尺寸不同。
- 完整刷新论文图：运行 `plot_1_stacked_bars.py`，再运行 `run_all_plots.py`。
