# 中文服务化词库人工扩展操作说明

本说明是给协作同事用的，目标是：

- 利用现有检测结果中的 `evidence` 片段，
- 半人工方式扩展、修正 `src/servitization_cn/config_keywords_cn.py` 里的中文关键词表，
- 提高中文服务化检测的召回率和准确率。

## 一、前提条件

- 已经在项目根目录创建好虚拟环境，并安装了依赖：

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

- 已经跑过中文管线，生成了 `servitization_results_cn.json`：

```bash
source .venv/bin/activate
export PYTHONPATH=src
.venv/bin/python -m servitization_cn.pipeline_cn \
  --input-dir data/raw/CN \
  --output-csv data/outputs/servitization_results_cn.csv \
  --output-json data/outputs/servitization_results_cn.json
```

## 二、导出 evidence 片段

1. 在项目根目录运行导出脚本：

```bash
source .venv/bin/activate
export PYTHONPATH=src
python scripts/export_cn_evidence.py
```

2. 脚本会生成两个输出：

- 汇总 CSV：`data/outputs/cn_evidence_flat.csv`
  - 列：`company, year, category, idx, snippet`
  - 每一行是某公司某年份、某服务类别下的一条文本片段。

- 按类别拆分的 TXT：`data/outputs/cn_evidence/` 目录下：
  - 每个文件对应一个类别，例如：
    - `maintenance_and_repair.txt`
    - `leasing_and_rental.txt`
    - `digital_and_streaming_services.txt`
  - 每行格式：`[股票代码-年份] 文本片段`

> 建议：优先用 TXT 文件做人工阅读，因为按类别分好，更容易集中精力判断该类别的典型/误判表达。

## 三、人工审阅和标注建议

在审阅时，建议按“每个类别一轮”的方式进行。

### 1. 对每个类别，重点做三件事

- **A. 找“明确应该算服务”的表达**
  - 例如：
    - `维护维养、检修服务、隐身维护产品、托管运营服务、云平台订阅服务` 等；
  - 把这些“好例子”里出现的核心短语记下来，准备加入对应类别的 `KEYWORDS_CN` 中。

- **B. 找“明显是误判”的表达**
  - 常见误判模式：
    - 法律/治理用语：`维护股东合法权益、维护公司形象、维护信息披露公平`；
    - 和“服务”无关的日常词：`维护社会稳定、维护国家安全` 等。
  - 对这类片段，可以：
    - 记录“误判的触发词 + 错误语境”（例如触发词是 `维护`，但上下文是 `股东权益`）。

- **C. 标记“需要更强上下文约束”的词**
  - 有些词单独出现太宽泛，例如：`维护、服务、咨询`；
  - 建议后续只在“和设备/系统/平台等一起出现”时才算真正的服务。

### 2. 建议的标注方式（简单可执行）

可在 Excel / Sheets 或纯文本里做一个简单表格，例如：

- `good_phrases.csv`：

  - 列：`category, phrase, example_snippet`
  - 示例：

    | category                         | phrase         | example_snippet                 |
    |----------------------------------|----------------|---------------------------------|
    | maintenance_and_repair           | 维护维养       | "确保隐身武器装备隐身性能..." |
    | leasing_and_rental               | 融资租赁       | "通过融资租赁方式..."         |
    | digital_and_streaming_services   | 订阅服务       | "云平台采用订阅服务模式..."   |

- `bad_patterns.csv`：

  - 列：`category, trigger, context_hint`
  - 示例：

    | category               | trigger | context_hint      |
    |------------------------|---------|-------------------|
    | maintenance_and_repair | 维护    | 股东/权益/形象等 |

后续开发同事会根据这两份表来更新关键词和简单规则。

## 四、如何根据标注更新词库

所有中文关键词目前集中在：

- `src/servitization_cn/config_keywords_cn.py`：`KEYWORDS_CN`

### 1. 扩充关键词（增加召回）

- 将 `good_phrases.csv` 里确认过的短语，按类别加入对应列表中，例如：

  ```python
  KEYWORDS_CN = {
      "maintenance_and_repair": [
          "维修",
          "维护",
          "检修",
          "保养",
          "维修服务",
          "维护服务",
          "隐身维护",   # 新增
          "运维服务",   # 新增
      ],
      ...
  }
  ```

- 建议优先加入：
  - 行业特定表达（如军工、通信、医药、互联网）；
  - 比较稳定的名词或动宾短语（`隐身维护产品、云平台订阅服务` 等）。

### 2. 记录并处理误判（提高精度）

目前中文 detector 的否定/上下文逻辑在：

- `src/servitization_cn/detector_cn.py`：`NEGATION_PATTERNS` 和 `_is_negated` 函数。

短期内可以通过 **简单规则** 降低误判，比如：

- 在 `NEGATION_PATTERNS` 旁边增加一个 `BAD_CONTEXT` 字典，记录“若与这些词共现，就忽略本次命中”，例如：

  ```python
  BAD_CONTEXT = {
      "maintenance_and_repair": ["股东", "权益", "公司形象"],
  }
  ```

- 在 `_is_negated` 或匹配逻辑里检查：
  - 如果 snippet 中既出现触发词（如 `维护`），又出现坏上下文词（如 `股东`），则跳过。

> 具体规则可由开发同事根据你们的标注表来实现，这部分不要求标注同事写代码，只需在表格中清晰地列出“误判触发词 + 典型坏上下文”。

## 五、迭代流程建议

整体建议采用“小步快跑”的方式：

1. **第 1 轮**：
   - 选取若干公司/年份（例如当前已经放进 `data/raw/CN` 的样本），
   - 导出 evidence，
   - 标注出一批明显的好短语和误判模式，
   - 更新 `config_keywords_cn.py` 和简单规则。

2. **重新跑中文管线**：

   ```bash
   source .venv/bin/activate
   export PYTHONPATH=src
   python -m servitization_cn.pipeline_cn \
     --input-dir data/raw/CN \
     --output-csv data/outputs/servitization_results_cn.csv \
     --output-json data/outputs/servitization_results_cn.json
   ```

3. **第 2 轮**：
   - 再次导出新的 evidence，
   - 重点检查前一轮误判是否明显减少，有没有新的常见模式，
   - 如有需要，再小幅调整关键词和规则。

4. 当误判率/召回率在抽样结果中达到可以接受的水平时，
   - 再批量导入更多公司年报，
   - 用这套稳定的词库生成最终研究用的指标。

---

如需给标注同事的简化版要点，可以概括为：

1. 跑脚本导出 evidence；
2. 每个类别看典型片段：
   - 记下“应该算服务”的短语（准备加进词库）；
   - 标出“明显不是服务”的典型句式（准备做排除规则）；
3. 把这些内容填进两个表：`good_phrases.csv` 和 `bad_patterns.csv`；
4. 交给开发同事，把这些信息同步到 `config_keywords_cn.py` 和 `detector_cn.py` 中。
