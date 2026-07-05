"""CLI 主入口"""
import json
import sys
import io
import click

from .pdf_parser import parse_pdf, PDFParserError
from .ai_client import extract_resume_info, score_resume
from .jd_reader import read_jd, JDError
from .logger import get_logger
from .config import Config

# Windows GBK 终端兼容：避免 emoji 编码错误
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

logger = get_logger(__name__)


def _save_output(data: dict, output_path: str):
    """保存结果到 JSON 文件"""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    click.echo(f"\n✅ 结果已保存到: {output_path}")


def _format_json(data: dict) -> str:
    """格式化 JSON 输出"""
    return json.dumps(data, ensure_ascii=False, indent=2)


@click.group()
@click.option("--mock", is_flag=True, default=False, help="使用 Mock 模式，无需 AI API Key")
@click.pass_context
def cli(ctx, mock):
    """AI 简历解析 CLI 工具 - 读取 PDF 简历，调用 AI 提取关键信息并进行岗位匹配评分"""
    ctx.ensure_object(dict)
    ctx.obj["mock"] = mock


@cli.command()
@click.argument("pdf_path", type=click.Path(exists=False))
@click.option("--output", "-o", default=None, help="保存解析结果到 JSON 文件")
@click.pass_context
def parse(ctx, pdf_path, output):
    """解析 PDF 简历并提取文本内容"""
    try:
        text = parse_pdf(pdf_path)
        result = {"text": text, "char_count": len(text)}
        click.echo(_format_json(result))
        if output:
            _save_output(result, output)
    except PDFParserError as e:
        click.echo(f"❌ 错误: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("pdf_path", type=click.Path(exists=False))
@click.option("--output", "-o", default=None, help="保存提取结果到 JSON 文件")
@click.option("--mock", "-m", is_flag=True, default=None, help="使用 Mock 模式")
@click.pass_context
def extract(ctx, pdf_path, output, mock):
    """从 PDF 简历中提取结构化信息（调用 AI）"""
    # 确定是否使用 mock 模式
    use_mock = mock if mock is not None else ctx.obj.get("mock", False)

    try:
        # 1. 解析 PDF
        text = parse_pdf(pdf_path)
        click.echo(f"📄 已解析 PDF，共 {len(text)} 个字符")

        # 2. 调用 AI 提取
        click.echo("🤖 正在调用 AI 提取结构化信息...")
        result = extract_resume_info(text, mock=use_mock)

        click.echo(_format_json(result))
        if output:
            _save_output(result, output)
    except PDFParserError as e:
        click.echo(f"❌ 错误: {e}", err=True)
        sys.exit(1)
    except (RuntimeError, ValueError) as e:
        click.echo(f"❌ AI 调用错误: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("pdf_path", type=click.Path(exists=False))
@click.option("--jd", "-j", required=True, help="岗位描述文件路径")
@click.option("--output", "-o", default=None, help="保存评分结果到 JSON 文件")
@click.option("--mock", "-m", is_flag=True, default=None, help="使用 Mock 模式")
@click.pass_context
def score(ctx, pdf_path, jd, output, mock):
    """对简历和岗位描述进行匹配评分"""
    use_mock = mock if mock is not None else ctx.obj.get("mock", False)

    try:
        # 1. 解析 PDF
        resume_text = parse_pdf(pdf_path)
        click.echo(f"📄 已解析简历 PDF，共 {len(resume_text)} 个字符")

        # 2. 读取 JD
        jd_text = read_jd(jd)
        click.echo(f"📋 已读取岗位描述，共 {len(jd_text)} 个字符")

        # 3. AI 评分
        click.echo("🤖 正在调用 AI 进行匹配评分...")
        result = score_resume(resume_text, jd_text, mock=use_mock)

        # 美化输出
        click.echo("\n" + "=" * 50)
        click.echo("📊 简历匹配评分结果")
        click.echo("=" * 50)
        click.echo(f"综合评分: {result['overall_score']}/100")
        click.echo(f"技能评分: {result['skill_score']}/100")
        click.echo(f"经验评分: {result['experience_score']}/100")
        click.echo(f"学历评分: {result['education_score']}/100")
        click.echo(f"\n💬 评语: {result['comment']}")
        if result.get("interview_questions"):
            click.echo("\n❓ 建议面试问题:")
            for i, q in enumerate(result["interview_questions"], 1):
                click.echo(f"  {i}. {q}")
        click.echo("=" * 50)

        if output:
            _save_output(result, output)
    except PDFParserError as e:
        click.echo(f"❌ PDF 错误: {e}", err=True)
        sys.exit(1)
    except JDError as e:
        click.echo(f"❌ JD 错误: {e}", err=True)
        sys.exit(1)
    except (RuntimeError, ValueError) as e:
        click.echo(f"❌ AI 调用错误: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
