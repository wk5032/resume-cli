"""AI 客户端模块 - 调用 OpenAI API 进行简历解析和评分"""
import json
import re
from openai import OpenAI
from .config import Config
from .logger import get_logger

logger = get_logger(__name__)

EXTRACT_PROMPT = """你是一个专业的简历解析助手。请从以下简历文本中提取结构化信息。

请严格按照以下 JSON 格式返回，不要添加任何额外的文字说明或 markdown 标记：

{{
  "name": "姓名",
  "phone": "电话",
  "email": "邮箱",
  "city": "所在城市",
  "education": [
    {{
      "school": "学校",
      "major": "专业",
      "degree": "学历（如本科、硕士、博士等）",
      "graduation_time": "毕业时间"
    }}
  ],
  "skills": ["技能1", "技能2"]
}}

注意：
- 如果某个字段在简历中找不到，请填写空字符串 "" 或空数组 []
- education 是一个数组，每条教育经历一个对象
- skills 是字符串数组，列出简历中提到的所有技术技能
- 不要编造任何信息，只提取简历中实际存在的内容

简历文本：
---
{resume_text}
---"""

SCORE_PROMPT = """你是一个专业的招聘评估助手。请根据以下岗位描述(JD)对候选人简历进行匹配评分。

岗位描述：
---
{jd_text}
---

候选人简历：
---
{resume_text}
---

请严格按照以下 JSON 格式返回评分结果，不要添加任何额外的文字说明或 markdown 标记：

{{
  "overall_score": 82,
  "skill_score": 88,
  "experience_score": 80,
  "education_score": 75,
  "comment": "候选人具备较好的全栈开发基础，技能与岗位要求较匹配，但缺少明确的大模型应用经验。",
  "interview_questions": [
    "请介绍一个你主导过的全栈项目。",
    "你是否有调用大模型 API 的实际经验？"
  ]
}}

评分要求：
- overall_score 是综合评分，范围 0-100
- skill_score 是技能匹配度，范围 0-100
- experience_score 是经验匹配度，范围 0-100
- education_score 是学历匹配度，范围 0-100
- comment 是简要评语，说明匹配情况和不足
- interview_questions 是 2-3 个面试问题建议
- 评分需客观公正，依据实际匹配程度"""


def _create_client() -> OpenAI:
    """创建 OpenAI 客户端"""
    kwargs = {"api_key": Config.OPENAI_API_KEY}
    if Config.OPENAI_BASE_URL:
        kwargs["base_url"] = Config.OPENAI_BASE_URL
    return OpenAI(**kwargs)


def _fix_json(text: str) -> str:
    """尝试修复常见的 JSON 格式错误"""
    # 去除 markdown 代码块标记
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        # 移除第一行（```json 或 ```）
        if lines[0].startswith("```"):
            lines = lines[1:]
        # 移除最后一行（```）
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines)

    # 尝试提取 JSON 对象
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        text = match.group(0)

    return text.strip()


def _call_ai(prompt: str, mock: bool = False) -> str:
    """调用 AI API，返回文本响应

    Args:
        prompt: 提示词
        mock: 是否使用 mock 模式

    Returns:
        AI 响应的文本

    Raises:
        RuntimeError: AI 调用失败
    """
    if mock:
        logger.info("使用 Mock 模式生成响应")
        return _generate_mock_response(prompt)

    if not Config.is_configured():
        raise RuntimeError(
            "未配置 OPENAI_API_KEY 环境变量。"
            "请在 .env 文件中设置或使用 --mock 模式。"
        )

    try:
        client = _create_client()
        logger.info(f"调用 AI 模型: {Config.OPENAI_MODEL}")
        response = client.chat.completions.create(
            model=Config.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "你是一个专业的简历解析助手，始终返回合法的 JSON 格式。"},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
        )
        content = response.choices[0].message.content
        logger.info("AI 调用成功")
        return content
    except Exception as e:
        logger.error(f"AI 调用失败: {e}")
        raise RuntimeError(f"AI 调用失败: {e}")


def _generate_mock_response(prompt: str) -> str:
    """生成 mock 响应用于演示"""
    if "提取结构化信息" in prompt or "extract" in prompt.lower():
        return json.dumps({
            "name": "张三",
            "phone": "13800138000",
            "email": "zhangsan@example.com",
            "city": "北京",
            "education": [
                {
                    "school": "北京大学",
                    "major": "计算机科学与技术",
                    "degree": "硕士",
                    "graduation_time": "2024年6月"
                },
                {
                    "school": "武汉大学",
                    "major": "软件工程",
                    "degree": "本科",
                    "graduation_time": "2021年6月"
                }
            ],
            "skills": ["Python", "Go", "React", "PostgreSQL", "Docker", "Kubernetes", "Machine Learning", "LLM"]
        }, ensure_ascii=False, indent=2)
    elif "评分" in prompt or "score" in prompt.lower() or "匹配" in prompt:
        return json.dumps({
            "overall_score": 82,
            "skill_score": 88,
            "experience_score": 80,
            "education_score": 75,
            "comment": "候选人具备较好的全栈开发基础，技能与岗位要求较匹配，但缺少明确的大模型应用经验。",
            "interview_questions": [
                "请介绍一个你主导过的全栈项目，包括技术选型和架构设计。",
                "你是否有调用大模型 API 的实际经验？请举例说明。",
                "请谈谈你对 AI for Science 领域的理解。"
            ]
        }, ensure_ascii=False, indent=2)
    return "{}"


def extract_resume_info(resume_text: str, mock: bool = False) -> dict:
    """从简历文本中提取结构化信息

    Args:
        resume_text: 简历文本
        mock: 是否使用 mock 模式

    Returns:
        结构化的简历信息 dict

    Raises:
        RuntimeError: AI 调用失败
        ValueError: JSON 解析失败
    """
    prompt = EXTRACT_PROMPT.format(resume_text=resume_text)
    response = _call_ai(prompt, mock=mock)

    # 尝试解析 JSON，自动修复常见错误
    try:
        data = json.loads(response)
    except json.JSONDecodeError:
        logger.warning("AI 返回的 JSON 格式有误，尝试自动修复...")
        fixed = _fix_json(response)
        try:
            data = json.loads(fixed)
        except json.JSONDecodeError as e:
            logger.error(f"JSON 修复失败: {e}")
            raise ValueError(f"AI 返回结果无法解析为 JSON，原始响应: {response[:200]}...")

    # 基本校验
    required_fields = ["name", "phone", "email", "city", "education", "skills"]
    for field in required_fields:
        if field not in data:
            logger.warning(f"缺少字段: {field}，使用默认值")
            if field in ("education", "skills"):
                data[field] = []
            else:
                data[field] = ""

    return data


def score_resume(resume_text: str, jd_text: str, mock: bool = False) -> dict:
    """对简历进行岗位匹配评分

    Args:
        resume_text: 简历文本
        jd_text: 岗位描述文本
        mock: 是否使用 mock 模式

    Returns:
        评分结果 dict

    Raises:
        RuntimeError: AI 调用失败
        ValueError: JSON 解析失败
    """
    prompt = SCORE_PROMPT.format(jd_text=jd_text, resume_text=resume_text)
    response = _call_ai(prompt, mock=mock)

    try:
        data = json.loads(response)
    except json.JSONDecodeError:
        logger.warning("AI 返回的 JSON 格式有误，尝试自动修复...")
        fixed = _fix_json(response)
        try:
            data = json.loads(fixed)
        except json.JSONDecodeError as e:
            logger.error(f"JSON 修复失败: {e}")
            raise ValueError(f"AI 返回结果无法解析为 JSON，原始响应: {response[:200]}...")

    # 基本校验
    required_fields = [
        "overall_score", "skill_score", "experience_score",
        "education_score", "comment", "interview_questions"
    ]
    for field in required_fields:
        if field not in data:
            logger.warning(f"缺少字段: {field}")
            if field in ("interview_questions",):
                data[field] = []
            elif field == "comment":
                data[field] = ""
            else:
                data[field] = 0

    return data
