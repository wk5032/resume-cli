# AI 简历解析 CLI 工具 (resume-cli)

一个基于 AI 的命令行简历解析工具，支持 **PDF 简历读取**、**AI 结构化信息提取** 和 **岗位匹配评分**。

## 技术选型

| 组件 | 技术 |
|------|------|
| 编程语言 | Python >= 3.9 |
| CLI 框架 | [Click](https://click.palletsprojects.com/) |
| PDF 解析 | [PyPDF2](https://pypi.org/project/PyPDF2/) |
| AI 模型 | OpenAI API（兼容任意 API Proxy） |
| 环境变量 | python-dotenv |

## 环境变量配置

复制 `.env.example` 为 `.env` 并填写配置：

```bash
cp .env.example .env
```

编辑 `.env`：

```ini
# OpenAI API Key（支持 OpenAI 或任何兼容 API）
OPENAI_API_KEY=sk-your-api-key-here
# 可选：自定义 API Base URL（如使用代理或其他兼容模型）
OPENAI_BASE_URL=https://api.openai.com/v1
# 可选：模型名称
OPENAI_MODEL=gpt-4o-mini
```

> 如果没有 API Key，可以使用 `--mock` 模式演示，无需真实接口。

## 安装方式

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 安装 CLI 工具
pip install -e .
```

或使用 Makefile：

```bash
make install
```

## CLI 命令说明

### 1. `parse` — 解析 PDF 提取文本

```bash
resume-cli parse ./resume.pdf
```

输出简历文本内容和字符数。

选项：
- `--output, -o` — 保存结果为 JSON 文件

**示例输出：**

```json
{
  "text": "简历文本内容...",
  "char_count": 1234
}
```

### 2. `extract` — AI 结构化信息提取

```bash
resume-cli extract ./resume.pdf
```

输出 JSON 格式的结构化信息，包含以下字段：

| 字段 | 说明 |
|------|------|
| `name` | 姓名 |
| `phone` | 电话 |
| `email` | 邮箱 |
| `city` | 所在城市 |
| `education` | 教育经历数组 |
| `skills` | 技能列表 |

选项：
- `--output, -o` — 保存结果为 JSON 文件
- `--mock, -m` — 使用 Mock 模式（无需 AI API Key）

**示例输出：**

```json
{
  "name": "张三",
  "phone": "13800138000",
  "education": [
    {
      "school": "北京大学",
      "major": "计算机科学与技术",
      "degree": "硕士",
      "graduation_time": "2024年6月"
    }
  ],
  "skills": ["Python", "Go", "React"]
}
```

### 3. `score` — 简历与岗位描述匹配评分

```bash
resume-cli score ./resume.pdf --jd ./jd.txt
```

输出 JSON 格式评分结果：

| 字段 | 说明 |
|------|------|
| `overall_score` | 综合评分 (0-100) |
| `skill_score` | 技能匹配度 (0-100) |
| `experience_score` | 经验匹配度 (0-100) |
| `education_score` | 学历匹配度 (0-100) |
| `comment` | 评语 |
| `interview_questions` | 建议面试问题列表 |

选项：
- `--output, -o` — 保存结果为 JSON 文件
- `--mock, -m` — 使用 Mock 模式

## 示例输入和输出

### Mock 模式演示（无需 API Key）

```bash
# 提取结构化信息
resume-cli --mock extract ./resume.pdf

# 匹配评分
resume-cli --mock score ./resume.pdf --jd ./examples/sample_jd.txt
```

### 真实模式

```bash
# 提取结构化信息
resume-cli extract ./resume.pdf

# 保存为 JSON
resume-cli extract ./resume.pdf -o result.json

# 匹配评分
resume-cli score ./resume.pdf --jd ./jd.txt
```

## 已实现功能

- [x] 简历文本解析 (parse)
  - PDF 文件读取
  - 文件不存在/非 PDF 格式/无法读取/内容为空 等错误提示
- [x] AI 结构化信息提取 (extract)
  - OpenAI API 调用
  - JSON 自动修复（去 markdown 标记、提取 JSON 对象）
  - 字段缺失默认值填充
  - Mock 模式
- [x] JD 匹配评分 (score)
  - JD 文件读取
  - 多维度评分（综合、技能、经验、学历）
  - 面试问题推荐
  - Mock 模式
- [x] CLI 完整命令支持
  - `--help` 帮助信息
  - `--output` 保存 JSON 结果
  - `--mock` 无 API Key 演示
- [x] 日志输出
- [x] Makefile
- [x] 基础测试
- [x] JSON 格式错误自动修复

## 项目结构

```
resume-cli/
├── resume_cli/           # 核心模块
│   ├── __init__.py       # 包信息
│   ├── main.py           # CLI 主入口
│   ├── pdf_parser.py     # PDF 解析
│   ├── ai_client.py      # AI API 调用
│   ├── jd_reader.py      # JD 文件读取
│   ├── config.py         # 配置管理
│   └── logger.py         # 日志模块
├── tests/                # 测试
│   ├── conftest.py
│   └── test_basic.py
├── examples/             # 示例文件
│   └── sample_jd.txt
├── Makefile
├── setup.py
├── requirements.txt
└── .env.example
```

## 测试

```bash
make test
# 或
pytest tests/ -v
```

## 已知问题 / 未完成内容

- 需要提供真实 PDF 文件或使用 --mock 模式演示
- score 命令需要同时提供简历 PDF 和 JD 文件
# resume-cli
