"""JD 文件读取模块"""
import os
from .logger import get_logger

logger = get_logger(__name__)


class JDError(Exception):
    """JD 读取异常基类"""
    pass


class JDFileNotFound(JDError):
    """JD 文件不存在"""
    pass


class JDEmpty(JDError):
    """JD 文件为空"""
    pass


def read_jd(file_path: str) -> str:
    """读取岗位描述文本文件

    Args:
        file_path: JD 文件路径（支持 .txt, .md 等文本格式）

    Returns:
        JD 文本内容

    Raises:
        JDFileNotFound: 文件不存在
        JDEmpty: 文件内容为空
    """
    logger.info(f"读取 JD 文件: {file_path}")

    if not os.path.exists(file_path):
        logger.error(f"JD 文件不存在: {file_path}")
        raise JDFileNotFound(f"JD 文件不存在: {file_path}")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
    except UnicodeDecodeError:
        with open(file_path, "r", encoding="gbk") as f:
            content = f.read().strip()

    if not content:
        logger.error(f"JD 文件内容为空: {file_path}")
        raise JDEmpty(f"JD 文件内容为空: {file_path}")

    logger.info(f"成功读取 JD 文件，{len(content)} 个字符")
    return content
