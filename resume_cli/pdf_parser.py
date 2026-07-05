"""PDF 解析模块"""
import os
from PyPDF2 import PdfReader
from .logger import get_logger

logger = get_logger(__name__)


class PDFParserError(Exception):
    """PDF 解析异常基类"""
    pass


class FileNotFound(PDFParserError):
    """文件不存在"""
    pass


class NotPDFFile(PDFParserError):
    """文件不是 PDF"""
    pass


class PDFUnreadable(PDFParserError):
    """PDF 无法读取"""
    pass


class PDFEmpty(PDFParserError):
    """PDF 文本为空"""
    pass


def parse_pdf(file_path: str) -> str:
    """读取本地 PDF 简历并提取文本内容。

    Args:
        file_path: PDF 文件路径

    Returns:
        提取的文本内容

    Raises:
        FileNotFound: 文件不存在
        NotPDFFile: 文件不是 PDF
        PDFUnreadable: PDF 无法读取
        PDFEmpty: PDF 文本为空
    """
    logger.info(f"开始解析 PDF 文件: {file_path}")

    # 检查文件是否存在
    if not os.path.exists(file_path):
        logger.error(f"文件不存在: {file_path}")
        raise FileNotFound(f"文件不存在: {file_path}")

    # 检查扩展名
    if not file_path.lower().endswith(".pdf"):
        logger.error(f"文件不是 PDF 格式: {file_path}")
        raise NotPDFFile(f"文件不是 PDF 格式，请提供 .pdf 文件: {file_path}")

    # 读取 PDF
    try:
        reader = PdfReader(file_path)
    except Exception as e:
        logger.error(f"PDF 文件无法读取: {e}")
        raise PDFUnreadable(f"PDF 文件无法读取: {e}")

    # 提取文本
    text_parts = []
    for i, page in enumerate(reader.pages):
        try:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
        except Exception as e:
            logger.warning(f"第 {i+1} 页文本提取失败: {e}")

    full_text = "\n".join(text_parts).strip()

    if not full_text:
        logger.error("PDF 文本内容为空")
        raise PDFEmpty(f"PDF 文件文本内容为空: {file_path}")

    logger.info(f"成功解析 PDF，共 {len(reader.pages)} 页，{len(full_text)} 个字符")
    return full_text
