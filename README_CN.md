# 服务化检测项目（Servitization Detection Project）

本项目用于在年报等文本中识别 13 类服务化相关的服务类别，并基于关键词字典构建 **complementing/substituting** 服务指标，以及一个简化的供应链/运营风险评分，方便后续做计量研究（如服务化与业绩、风险、bullwhip effect 等的关系）。

## 一、项目结构

- `data/raw/`：
  - 输入文件目录。
  - 存放原始 PDF/TXT 等文件，文件名格式约定为：`COMPANY_YEAR.ext`，例如 `AAPL_2019.pdf`、`TSLA_2020.txt`。

- `data/outputs/`：
  - 输出结果目录。
  - 主要包含 `servitization_results.csv` 和可选的 JSON 结果。

- `src/servitization/`：
  - 核心业务逻辑模块：
    - `config_keywords.py`：13 类服务的关键词表和 complementing/substituting 分类。
    - `detector.py`：文本预处理、关键词匹配、服务类别识别、风险评分等。
    - `io_markitdown.py`：统一调用 `markitdown` 将 PDF/DOCX/PPTX 等转换成纯文本。
    - `pipeline.py`：批处理流程（从文件夹读入 -> 识别服务 -> 导出 CSV/JSON）。
    - `__init__.py`：对外暴露主要函数。

- `scripts/run_detection.py`：
  - 便捷脚本，一行命令跑完整流程。

## 二、环境与依赖

在项目根目录（本仓库根目录）下建议创建虚拟环境：

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

`requirements.txt` 中主要包含：

- `markitdown[all]`：
  - 用于将 PDF / DOCX / PPTX 等多种文档格式转换为 markdown/text。
- `pandas`：
  - 用于表格结果处理和导出 CSV。

可选：如需启用 lemma 回退（使用 spaCy 做词形还原），则：

1. 安装 spaCy 及模型：

   ```bash
   pip install spacy
   python -m spacy download en_core_web_sm
   ```

2. 在 `src/servitization/detector.py` 中把：

   ```python
   USE_SPACY = False
   ```

   改成：

   ```python
   USE_SPACY = True
   ```

## 三、输入数据约定

- 将年报等文本文件放入 `data/raw/` 目录下；
- 文件命名约定：`COMPANY_YEAR.ext`，例如：
  - `AAPL_2019.pdf`
  - `AAPL_2020.txt`
  - `TSLA_2019.pdf`

其中：

- `COMPANY`：公司 ID（字符串即可）；
- `YEAR`：四位数字年份（如 2019）。

`pipeline.py` 会根据文件名自动解析 `company` 和 `year`，并将同一公司不同年份的文本打包处理。

## 四、运行方式

### 方式 A：模块形式（推荐）

在项目根目录执行：

```bash
source .venv/bin/activate  # 如果创建了虚拟环境
export PYTHONPATH=src

python -m servitization.pipeline \
  --input-dir data/raw \
  --output-csv data/outputs/servitization_results.csv \
  --output-json data/outputs/servitization_results.json
```

说明：

- `--input-dir`：输入文件夹路径（默认为 `data/raw`）。
- `--output-csv`：输出 CSV 结果路径。
- `--output-json`：可选，输出包含详细 evidence 的 JSON 文件路径。

### 方式 B：脚本形式

同样在项目根目录：

```bash
source .venv/bin/activate  # 如果创建了虚拟环境
export PYTHONPATH=src      # 建议设置，确保可以导入 `servitization`

python scripts/run_detection.py
```

`scripts/run_detection.py` 默认：

- 输入：`data/raw`；
- CSV 输出：`data/outputs/servitization_results.csv`；
- JSON 输出：`data/outputs/servitization_results.json`。

## 五、输出结果说明（列含义与研究使用）

主输出文件是 `data/outputs/servitization_results.csv`，每一行对应一个公司-年份（firm-year）观察值，即 `(company, year)`。关键列如下：

### 1. `company` 与 `year`

- **`company`**：
  - 从文件名前缀解析出的公司 ID，例如 `AAPL_2019.pdf` -> `AAPL`。
  - 在面板数据中可作为公司维度的主键 `i`，用于与财务数据、股票数据等合并。

- **`year`**：
  - 从文件名解析的年份，例如 `2019`。
  - 在面板数据中作为时间维度的主键 `t`。

> 研究视角：`(company, year)` 就是标准 panel data 里的 `(i, t)`，可直接与 Compustat/CSMAR/CRSP 等数据对齐。

### 2. `service_num`：服务化广度（breadth）

- 定义：
  - 13 个服务类别中，被识别为存在（flag=1）的类别个数，即 `sum(flags.values())`。
- 含义：
  - 某公司在该年提供了多少 **不同类别** 的服务。
- 研究用途：
  - 可作为一个简单的 **servitization breadth/intensity** 指标：
    - 数值越大，说明该公司从“纯产品”走向“产品+服务”的程度越深，服务组合越丰富。

### 3. `comp_count`：complementing 型服务数量

- 定义：
  - 在 `CATEGORY_TYPE` 中被标记为 `"complementing"` 的服务类别中，flag=1 的类别个数。
  - 典型包括：维修保养、备件供应、安装与调试、技术支持、培训与咨询、系统集成等。
- 含义：
  - 描述企业提供的“围绕产品的补充型服务”（support / complement services）的广度。
- 研究用途：
  - 可视为 **早期/温和型服务化** 的程度：
    - 企业仍然以销售产品为主，通过售后服务、维护、培训等提升产品价值与客户粘性。

### 4. `sub_count`：substituting 型服务数量

- 定义：
  - 在 `CATEGORY_TYPE` 中标记为 `"substituting"` 的类别中，flag=1 的类别个数。
  - 主要包括：
    - `leasing_and_rental`：租赁、按使用付费、订阅等；
    - `performance_based_contracts`：绩效合同、SLA、availability/uptime guarantee 等；
    - `recycling_and_process_management` 等（视具体设定）。
- 含义：
  - 描述企业采用 **部分替代传统一次性产品销售** 的服务模式的程度（leasing、pay-per-use、outcome-based contracts 等）。
- 研究用途：
  - 可视为 **更激进 / outcome-based 型服务化** 的程度：
    - 企业不再只是卖“产品+售后”，而是卖“可用性/性能/产出”；
    - 对收入结构、需求风险、运营风险影响更大，与供应链 bullwhip 效应、风险转移等主题高度相关。

### 5. `risk_score`：简化的风险暴露指标

- 当前实现：

  ```python
  risk_score = 2.0 * sub_count + 0.5 * comp_count
  ```

  - substituting 类服务每类赋权重 2.0；
  - complementing 类服务每类赋权重 0.5；
  - 该公式只是示例，可以根据研究需要调整权重或函数形式（线性/非线性）。

- 直观解释：
  - 假设：
    - substituting / outcome-based 服务对企业的运营和供应链风险影响更大；
    - complementing 服务的影响相对温和（既可能增加运营复杂度，也可能改善信息反馈）。

- 研究用途：
  - 可作为企业 **服务相关运营/供应链风险暴露** 的简单 proxy：
    - 可用于研究“服务化与风险/波动性/弹性”的关系；
    - 或作为控制变量，配合其他结构性指标使用。

### 6. `flags`：13 类服务组合的 0/1 向量

- 结构：

  ```python
  {
      "maintenance_and_repair": 1,
      "spare_parts_support": 1,
      "leasing_and_rental": 0,
      ...
  }
  ```

- 含义：
  - 对每一类服务（共 13 类）给出一个 0/1 标志，表示该 firm-year 是否被识别出此类服务。

- 研究用途：
  - 可以将 `flags` 展开成多个 dummy 变量，用于更细粒度的计量分析：
    - 构建不同“服务化策略类型”（maintenance-heavy / solution-heavy / performance-based-heavy 等）；
    - 单独考察某些类别（如 leasing / performance-based）的边际效应；
    - 组合构造更加复杂的指标（如 digital intensity、contractual risk intensity 等）。

### 7. `evidence`：文本层面的证据片段

- 结构：

  ```python
  {
      "maintenance_and_repair": ["... 文本片段 ...", ...],
      "leasing_and_rental": ["... 文本片段 ...", ...],
      ...
  }
  ```

  - 每个类别对应一个列表，保存触发该类别识别的上下文 snippet；
  - 如果启用 lemma 回退，还会出现类似 `"lemma_match::maintenance"` 的标记。

- 研究用途：
  - **人工校验与关键词调优**：
    - 抽样查看 evidence，判断误判/漏判情况，迭代优化 `config_keywords.py`。
  - **论文中的文本证据**：
    - 从中挑选代表性语句，作为论文中说明“什么叫服务化、performance-based contract”之类的 qualitative evidence。

## 六、与后续研究的衔接

该项目的设计目标，是让输出结果可以方便地融入你现有的 firm-year 面板数据中，用于：

- 复现或扩展服务化相关文献（例如服务化对盈利能力、创新、竞争策略的影响）；
- 结合供应链/bullwhip 效应文献，研究：
  - complementing vs substituting/service 的不同风险暴露；
  - outcome-based / leasing 合同如何重塑需求和库存波动；
- 构建更结构化的指标：
  - 服务化广度（`service_num`）；
  - 支持型 vs 替代型服务强度（`comp_count` vs `sub_count`）；
  - 合成风险指标（`risk_score`）；
  - 服务组合结构（展开 `flags` 后的多维 dummy）。

你可以在 Notebook 中通过 `pandas` 读入 CSV，例如：

```python
import pandas as pd

serv = pd.read_csv("data/outputs/servitization_results.csv")
serv.head()

# 示例：查看某公司某年的服务组合
row = serv[(serv["company"] == "AAPL") & (serv["year"] == 2019)].iloc[0]
print(row["service_num"], row["comp_count"], row["sub_count"], row["risk_score"])
print(row["flags"])
```

然后与外部财务/市场数据 merge 后进行回归分析或可视化。
