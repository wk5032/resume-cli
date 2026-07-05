.PHONY: install test clean demo help sample-pdf

# 默认目标
help:
	@echo "AI 简历解析 CLI 工具"
	@echo ""
	@echo "可用命令:"
	@echo "  make install      - 安装依赖"
	@echo "  make test         - 运行测试"
	@echo "  make demo         - 运行 Mock 模式演示（自动生成示例 PDF）"
	@echo "  make sample-pdf   - 生成示例 PDF 简历"
	@echo "  make clean        - 清理临时文件"
	@echo ""

# 安装依赖
install:
	pip install -r requirements.txt
	pip install -e .

# 运行测试
test:
	pytest tests/ -v

# 生成示例 PDF 简历
sample-pdf:
	python scripts/gen_sample_pdf.py
	copy /Y scripts\examples\sample_resume.pdf examples\sample_resume.pdf 2>nul

# Mock 模式演示
demo: sample-pdf
	@echo "========== Mock Demo: parse 命令 =========="
	resume-cli --mock parse ./examples/sample_resume.pdf
	@echo ""
	@echo "========== Mock Demo: extract 命令 =========="
	resume-cli --mock extract ./examples/sample_resume.pdf
	@echo ""
	@echo "========== Mock Demo: score 命令 =========="
	resume-cli --mock score ./examples/sample_resume.pdf --jd ./examples/sample_jd.txt

# 清理（兼容 Windows）
clean:
	@echo "清理 __pycache__ 和 .egg-info 目录..."
	@if exist resume_cli\__pycache__ rmdir /s /q resume_cli\__pycache__
	@if exist tests\__pycache__ rmdir /s /q tests\__pycache__
	@if exist resume_cli.egg-info rmdir /s /q resume_cli.egg-info
	@if exist examples\__pycache__ rmdir /s /q examples\__pycache__
	@echo "清理完成"
