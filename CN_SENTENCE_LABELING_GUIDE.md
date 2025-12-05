# 中文服务化句子级标注操作指南

本指南面向负责人工标注的同事，目标是：

- 从上市公司中文年报中导出句子级样本；
- 按 **13 类制造服务化类型** 对每句进行多标签标注；
- 生成可用于模型训练/评估的标注数据集。

> 不需要了解代码实现，只需会运行一个脚本并在表格中打标签即可。

---

## 一、前提条件

在项目根目录下：

1. 已经创建并激活虚拟环境，并安装依赖：

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. 已经准备好中文年报原始文件，放在：

   ```
   data/raw/CN/
   ```

   - 文件名中需要包含“股票代码+年份”等字段（例如：`688708_2024_佳驰科技_2024年年度报告_2025-04-18.pdf`）。
   - 具体解析规则由代码自动处理，标注同事无需关心细节。

---

## 二、导出句子级样本 CSV

在项目根目录执行：

```bash
source .venv/bin/activate
export PYTHONPATH=src
python scripts/export_cn_sentences_for_labeling.py \
  --input-dir data/raw/CN \
  --output-csv data/outputs/cn_sentences_for_labeling.csv
```

脚本完成后，将生成：

- `data/outputs/cn_sentences_for_labeling.csv`

该文件就是需要进行人工标注的主文件，可以用 Excel / WPS / Sheets 打开。

> 如需控制句子最短长度，可以增加 `--min-len` 参数（单位：字数），例如：
>
> ```bash
> python scripts/export_cn_sentences_for_labeling.py \
>   --input-dir data/raw/CN \
>   --output-csv data/outputs/cn_sentences_for_labeling.csv \
>   --min-len 10
> ```

---

## 三、CSV 列说明

打开 `cn_sentences_for_labeling.csv` 后，你会看到类似下面的列：

- `company`：公司代码（从文件名解析而来）
- `year`：年份
- `sent_id`：句子在该公司-该年份中的序号（从 0 开始）
- `sentence`：句子内容（经过简单断句和清洗）
- 后面 13 列：每一列对应一种制造服务化类别，多为英文标识，例如：
  - `maintenance_and_repair`
  - `spare_parts_support`
  - `leasing_and_rental`
  - `warranty_and_insurance`
  - `installation_and_commissioning`
  - `technical_support`
  - `customization_and_r&d_services`
  - `distribution_and_procurement`
  - `training_and_consulting`
  - `solutions_system_integration`
  - `digital_and_streaming_services`
  - `performance_based_contracts`
  - `recycling_and_process_management`

这些 13 列就是要打的标签列。

---

## 四、标注原则（多标签）

### 4.1 可以同时属于多个类别

- 一句话可以同时涉及多种服务类型，例如：
  - “公司提供**设备维修保养**、**备件供应**以及**云平台订阅服务**。”
  - 对应标签应为：
    - `maintenance_and_repair = 1`
    - `spare_parts_support = 1`
    - `digital_and_streaming_services = 1`
    - 其他类别全部为 `0`。

### 4.2 也可以全部为 0

- 若一句话**完全与服务无关**（纯财务描述、宏观政策、股东权益等），可以所有 13 个标签都标为 `0`。

### 4.3 标签取值

- 每个标签列只填：
  - `1`：该句**明确属于**此类服务；
  - `0`：该句**不属于**此类服务。

不要使用其他符号（如空白、Y/N 等），以便后续模型训练时自动读取。

---

## 五、各类别的直观理解

这里只给出直观判断标准，帮助快速决策。正式学术定义以研究方案为准。

- **maintenance_and_repair（维修与维护服务）**  
  出现“维修、维护、检修、保养、运维服务”等，与设备/系统维护有关。

- **spare_parts_support（备件与零部件供应）**  
  主要是“备件、零部件供应、配件供应、备品备件”等，强调**零部件/配件销售或保障**。

- **leasing_and_rental（租赁与租用服务）**  
  出现“租赁、租用、融资租赁、经营租赁、租赁服务”等，强调将设备/系统**以租代售**或租借使用。

- **warranty_and_insurance（质保与保险服务）**  
  如“质保、保修、保固、延保、保险服务、保险保障”等，与产品/服务提供的保障条款有关。

- **installation_and_commissioning（安装与调试服务）**  
  “安装调试、安装服务、调试服务、系统安装、工程安装”等，与交付后的**安装与上线**相关。

- **technical_support（技术支持与技术服务）**  
  “技术支持、技术服务、售后技术服务、技术保障”等，强调专业技术人员提供的支持服务。

- **customization_and_r&d_services（定制化 / 研发服务）**  
  “定制化、个性化定制、方案定制、研发服务、技术开发服务”等，与**按客户需求进行设计/研发**相关。

- **distribution_and_procurement（经销 / 分销 / 采购服务）**  
  “经销、分销、代理销售、代理经销、物流配送、供应链服务、采购服务”等，与**渠道、供应链与采购代理**相关。

- **training_and_consulting（培训与咨询服务）**  
  “培训服务、技术培训、咨询服务、顾问服务”等，提供**知识、培训或咨询**本身属于服务产品。

- **solutions_system_integration（解决方案与系统集成）**  
  “系统集成、整体解决方案、解决方案服务、一体化解决方案”等，强调**整套解决方案或系统集成**。

- **digital_and_streaming_services（数字化 / 平台 / 订阅服务）**  
  “云服务、SaaS、平台服务、订阅服务、在线服务、数字化服务”等，强调**基于数字平台/云/订阅的持续服务**。

- **performance_based_contracts（绩效 / 按效付费合约）**  
  “绩效合同、按效付费、效果付费、服务水平协议、SLA”等，强调**按结果或绩效定价的合约**。

- **recycling_and_process_management（回收 / 再制造 / 流程托管）**  
  “回收利用、再制造、循环利用、废弃物处理、环保回收、流程外包、托管运营”等，与**回收处理或流程外包/托管**相关。

---

## 六、典型例子

下面是几个示例，帮助理解如何打多标签。

### 示例 1

> “公司为客户提供设备**维修保养**和**备品备件供应**服务。”

- `maintenance_and_repair = 1`
- `spare_parts_support = 1`
- 其他 11 类 = 0

### 示例 2

> “公司通过**融资租赁**方式向客户提供生产线设备，并提供**云平台订阅服务**用于远程监控。”

- `leasing_and_rental = 1`
- `digital_and_streaming_services = 1`
- 若提到后续维护，也可同时标 `maintenance_and_repair = 1`
- 其他未涉及则 = 0

### 示例 3

> “为保障股东合法权益，公司持续**维护公司形象**和品牌声誉。”

- 这类句子与“服务化”无直接关系，仅是治理/形象表述：
  - 所有 13 个标签均为 `0`。

---

## 七、标注结果的保存与交付

1. 标注时建议：
   - 先复制一份原始 CSV，避免覆盖源文件，例如：
     - `cn_sentences_for_labeling_annotated_v1.xlsx`；
   - 在副本中进行修改与标注。

2. 标注完成后：
   - 确保 13 个标签列中只包含 `0` 或 `1`；
   - 将文件统一保存为：
     - Excel 版本便于人工查看；
     - 同时导出为 CSV（UTF-8 编码），供后续模型训练脚本使用。

3. 交付给开发同事时，建议说明：
   - 使用的原始样本文件名；
   - 标注轮次/版本号（例如 v1, v2 等）；
   - 如有特殊约定（如某些边界样本的处理规则），可附在单独文档中。

---

如需给标注同事的极简要点，可概括为：

1. 运行脚本生成 `cn_sentences_for_labeling.csv`；
2. 在表格中查看 `sentence` 列，按 13 类服务，在对应列填 `0` 或 `1`，允许多列同时为 `1`；
3. 与服务完全无关的句子，所有标签列都填 `0`；
4. 保存并导出为带 13 个标签列的 CSV，交给开发同事即可。
