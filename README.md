# Sustainability Tool – Horticultural Residue Valorization Portal

本项目是一个面向研究人员的可视化门户，用于探索南荷兰与弗兰德地区（SNF 区域）的园艺作物产量、残余物库存以及残余物基生物产品（生物炭、堆肥、香豆酸）的潜在产量。

## 技术栈

- Python 3.10+
- Streamlit（Web 门户框架）
- pandas（Excel 数据读取与处理）
- Plotly（交互式图表与地图）

## 主要功能

- 从 Excel（.xlsx）数据集中读取园艺产量与残余物数据
- 交互式多级筛选：
  - 数据类型（产量、残余物、潜在生物炭/堆肥/香豆酸产量）
  - 地理范围（整个 SNF 区域 / 单省 / 多省）
  - 作物选择（单一或多个作物）
  - 残余物利用情景（1–100%，仅在潜在产品模式下显示）
- 交互式可视化：
  - 排名条形图
  - 饼图
  - 堆叠条形图
  - 省级尺度的着色地图（Choropleth）

## 目录结构（建议）

```text
CTCv0.1/
├─ app.py                    # Streamlit 主应用
├─ requirements.txt          # Python 依赖
├─ README.md
├─ data/
│  ├─ horticulture_data_example.xlsx  # 示例 Excel 数据（请用实际数据替换）
│  └─ geo/
│     └─ snf_provinces.geojson        # SNF 8 个省的 GeoJSON
└─ src/
   ├─ config.py               # 配置：省份、作物等
   ├─ data_loader.py          # 数据加载与预处理
   ├─ calculations.py         # 残余物与产品潜力计算
   └─ visualizations.py       # 图表与地图封装
```

> 注：示例仓库中可使用简化示例 Excel。实际研究中，只需保证列名与结构兼容，即可直接替换数据文件。

## 数据格式示例（Excel）

建议的 Excel 表结构（工作表名例如：`SNF_2022`）：

- `year`：年份（例如 2022）
- `province`：省名（与 GeoJSON 中一致）
- `crop`：作物名称（23 种园艺作物之一）
- `production_tonnes`：产量（吨）
- `residue_tonnes`：农艺残余物（吨）
- `residue_usable_fraction`：可用于转化的残余物比例（0–1，可选）
- `biochar_yield`：生物炭收率（吨产品 / 吨可用残余物，可选）
- `compost_yield`：堆肥收率（吨产品 / 吨可用残余物，可选）
- `moisture_content`：残余物含水率（0–1，用于香豆酸计算）
- `ca_content`：干基香豆酸含量（吨香豆酸 / 吨干残余物）

应用会根据 `year == 2022` 过滤，并在界面中聚合/筛选。

## 计算公式

- 可用残余物质量（吨）：
  - \[ residue\_usable = residue\_tonnes × utilization\_rate × residue\_usable\_fraction(若缺省视为 1) \]
- 生物炭潜力（吨）：
  - \[ biochar\_mass = residue\_usable × biochar\_yield \]
- 堆肥潜力（吨）：
  - \[ compost\_mass = residue\_usable × compost\_yield \]
- 香豆酸潜力（吨）：
  - \[ ca\_mass = residue\_usable × (1 - moisture\_content) × ca\_content \]

应用会对选定省份和作物求和，并在图表和地图中展示。

## 本地运行

1. 创建并激活虚拟环境（可选但推荐）：

```bash
cd CTCv0.1
python -m venv .venv
source .venv/bin/activate  # Windows 使用 .venv\Scripts\activate
```

2. 安装依赖：

```bash
pip install -r requirements.txt
```

3. 确认 `data/horticulture_data_example.xlsx` 与 `data/geo/snf_provinces.geojson` 存在。

4. 启动 Streamlit 应用：

```bash
streamlit run app.py
```

应用默认在 `http://localhost:8501` 打开。

## 部署与域名

完整的部署与域名配置步骤见文档底部“部署与域名配置”一节（在 `app.py` 以及本 README 末尾有详细说明）。

研究者只需：

- 在 Excel 中更新数据（保持列名不变）
- 将最新数据上传至部署平台（例如 Streamlit Community Cloud 的仓库）
- 无需修改代码即可更新门户展示内容。

