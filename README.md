# LlamaIndex RAG 项目

这是一个使用 LlamaIndex 实现的检索增强生成 (RAG) 系统，可以帮助您将文档向量化存储到 FAISS 向量数据库中，并通过自然语言查询检索相关信息。此外，它还支持使用GPT-4o生成图像功能。

## 功能特点

- 读取并向量化各种格式的文档（PDF、TXT、DOCX 等）
- 使用 FAISS 向量数据库高效存储和检索文档嵌入
- 灵活的查询接口，支持语义搜索
- 可自定义提示词模板
- 命令行界面和交互式查询模式
- 支持中文和多语言文档处理
- **使用GPT-4o生成图像，支持文本分析优化**

## 安装

### 方法一：使用pip直接安装

1. 克隆此仓库：

```bash
git clone https://github.com/KenChenTY/llamaindex.git
cd llamaindex
```

2. 安装依赖：

```bash
pip install -r requirements.txt
```

### 方法二：使用Conda创建虚拟环境（推荐）

1. 克隆此仓库：

```bash
git clone https://github.com/KenChenTY/llamaindex.git
cd llamaindex
```

2. 创建Conda虚拟环境：

```bash
conda create -n llamaindex-env python=3.10
```

3. 激活虚拟环境：

```bash
# Windows
conda activate llamaindex-env

# Linux/macOS
source activate llamaindex-env
```

4. 安装依赖：

```bash
pip install -r requirements.txt
```

5. 使用完毕后，可以退出虚拟环境：

```bash
conda deactivate
```

### 配置API密钥

创建一个 `.env` 文件并添加您的 OpenAI API 密钥：

```
OPENAI_API_KEY="your-api-key-here"
```

或者在首次运行时，程序会提示您输入 API 密钥。

## 使用方法

### 添加文档

将您想要索引的文档放在 `documents` 目录下（默认），或者您指定的任何目录中。

### 索引文档

```bash
python app.py index
```

### 查询知识库

单次查询：

```bash
python app.py query --query "您的问题"
```

带自定义系统提示的查询：

```bash
python app.py query --query "您的问题" --system_prompt "自定义的系统提示"
```

### 生成图像

基本图像生成：

```bash
python app.py generate_image --prompt "一只在草地上奔跑的金毛犬"
```

使用GPT-4o分析文本优化图像描述：

```bash
python app.py generate_image --prompt "一只在草地上奔跑的金毛犬" --analyze
```

自定义图像参数：

```bash
python app.py generate_image --prompt "日落时分的海滩" --size "1792x1024" --quality "hd" --style "natural"
```

### 交互式模式

```bash
python app.py interactive
```

或者直接运行：

```bash
python app.py
```

在交互式模式中，您可以：
- 输入问题进行查询
- 输入 `prompt` 更新系统提示
- 输入 `reload` 重新加载索引
- 输入 `image:描述` 生成图像
- 输入 `analyze_image:描述` 使用GPT-4o分析文本并生成图像
- 输入 `exit` 或 `quit` 退出

### 更新系统提示

```bash
python app.py update_prompt --system_prompt "您的新系统提示"
```

## 目录结构

```
llamaindex-rag/
├── app.py                # 主应用程序入口
├── config.py             # 配置文件
├── document_processor.py # 文档处理模块
├── query_engine.py       # 查询引擎模块
├── image_generator.py    # 图像生成模块
├── requirements.txt      # 依赖项
├── documents/            # 默认文档目录
├── vector_store/         # FAISS 向量存储目录
├── generated_images/     # 生成图像存储目录
└── .env                  # 环境变量配置
```

## 自定义配置

您可以通过 `.env` 文件或者环境变量来自定义以下配置：

- `OPENAI_API_KEY`：OpenAI API 密钥
- `MODEL_NAME`：使用的 LLM 模型（默认为 "gpt-3.5-turbo"）
- `VECTOR_STORE_DIR`：向量存储目录
- `DOCUMENTS_DIR`：文档目录
- `TOP_K`：检索的相似文档数量
- `SIMILARITY_THRESHOLD`：相似度阈值
- `SYSTEM_PROMPT`：系统提示
- `IMAGE_MODEL`：用于文本分析的模型（默认为 "gpt-4o"）
- `IMAGE_OUTPUT_DIR`：图像输出目录
- `IMAGE_SIZE`：图像尺寸（默认为 "1024x1024"）
- `IMAGE_QUALITY`：图像质量（默认为 "standard"）
- `IMAGE_STYLE`：图像风格（默认为 "vivid"）

## 高级用法

### 自定义提示词模板

您可以通过编辑 `query_engine.py` 中的 `DEFAULT_QUERY_TEMPLATE` 来自定义提示词模板。

### 使用其他向量数据库

虽然此项目默认使用 FAISS，但您可以通过修改 `document_processor.py` 轻松替换为其他向量数据库，如 Pinecone、Weaviate 等。

### 图像生成优化

`image_generator.py` 模块提供了两种生成图像的方式：
1. 直接使用用户提供的描述生成图像
2. 使用GPT-4o分析用户描述，创建更优化的图像生成提示

对于复杂的场景描述，建议使用分析模式（`--analyze`参数或 `analyze_image:` 前缀）以获得更好的图像生成效果。

## 依赖项

- llama-index
- faiss-cpu (或 faiss-gpu)
- openai
- python-dotenv
- nltk
- torch
- transformers
- fastapi (用于未来的 API 服务)
- uvicorn
- pillow (用于图像处理)
- requests (用于下载图像)

## 许可证

MIT 