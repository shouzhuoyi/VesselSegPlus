# 3VV 评估项目

## 概述
3VV 评估项目旨在处理医学图像并评估各种模型在测量解剖结构方面的性能。该项目包括用于图像处理、模型评估和结果汇总的脚本，使其成为分析血管测量的综合工具。

## 文件结构
```
3vv-evaluation
├── src
│   ├── biometric.py       # 处理图像以测量解剖结构的直径
│   ├── evaluate.py        # 通过将专家注释与模型预测进行比较来评估模型性能
│   └── summary.py         # 根据评估结果计算全局平均值
├── config.yaml            # 输入/输出路径和模型文件映射的配置设置
├── requirements.txt       # 列出项目所需的 Python 依赖项
└── README.md              # 项目的英文文档
└── README_zh.md           # 项目的中文文档
```

## 安装
要设置项目，请按照以下步骤操作：

1. 克隆存储库：
   ```
   git clone <repository-url>
   cd 3vv-evaluation
   ```

2. 安装所需的依赖项：
   ```
   pip install -r requirements.txt
   ```

## 配置
在运行脚本之前，请确保 `config.yaml` 文件已正确配置，其中包含输入图像、输出目录和模型文件的正确路径。

## 使用
### 图像处理
要处理图像并测量直径，请运行 `biometric.py` 脚本：
```
python src/biometric.py
```
该脚本将从指定的输入文件夹中读取图像，测量解剖结构的直径，并以 CSV 和 JSON 格式保存结果。

### 模型评估
要评估模型性能，请使用 `evaluate.py` 脚本：
```
python src/evaluate.py
```
该脚本将从 CSV 文件加载测量值，计算误差，并以 JSON 格式保存评估结果。

### 汇总计算
要从评估结果中计算全局平均值，请执行 `summary.py` 脚本：
```
python src/summary.py
```
该脚本将计算平均值，同时忽略异常值，并将汇总结果保存回 JSON 文件。

## 贡献
欢迎对项目做出贡献。如有任何建议或改进，请提交拉取请求或开启一个 issue。

## 许可证
该项目根据 MIT 许可证授权。有关详细信息，请参阅 LICENSE 文件。
