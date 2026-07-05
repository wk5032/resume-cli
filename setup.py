from setuptools import setup, find_packages

setup(
    name="resume-cli",
    version="1.0.0",
    description="AI 简历解析 CLI 工具 - 读取 PDF 简历，调用 AI 提取关键信息并进行岗位匹配评分",
    author="Sidereus AI Candidate",
    packages=find_packages(),
    install_requires=[
        "click>=8.0.0",
        "PyPDF2>=3.0.0",
        "openai>=1.0.0",
        "python-dotenv>=1.0.0",
        "fpdf2>=2.7.0",
    ],
    entry_points={
        "console_scripts": [
            "resume-cli=resume_cli.main:cli",
        ],
    },
    python_requires=">=3.9",
)
