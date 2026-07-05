"""测试模块"""
import os
import json
import tempfile
import pytest
from unittest.mock import patch, MagicMock

from resume_cli.pdf_parser import parse_pdf, FileNotFound, NotPDFFile
from resume_cli.jd_reader import read_jd, JDFileNotFound, JDEmpty
from resume_cli.ai_client import extract_resume_info, score_resume, _fix_json


class TestPDFParser:
    """PDF 解析测试"""

    def test_file_not_found(self):
        """测试文件不存在的情况"""
        with pytest.raises(FileNotFound):
            parse_pdf("./nonexistent_file.pdf")

    def test_not_pdf_extension(self):
        """测试非 PDF 文件扩展名"""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"test content")
            tmp_path = f.name
        try:
            with pytest.raises(NotPDFFile):
                parse_pdf(tmp_path)
        finally:
            os.unlink(tmp_path)


class TestJDReader:
    """JD 读取测试"""

    def test_jd_not_found(self):
        """测试 JD 文件不存在"""
        with pytest.raises(JDFileNotFound):
            read_jd("./nonexistent_jd.txt")

    def test_jd_empty(self):
        """测试 JD 文件为空"""
        with tempfile.NamedTemporaryFile(suffix=".txt", mode="w", delete=False, encoding="utf-8") as f:
            f.write("")
            tmp_path = f.name
        try:
            with pytest.raises(JDEmpty):
                read_jd(tmp_path)
        finally:
            os.unlink(tmp_path)

    def test_jd_read_success(self):
        """测试 JD 文件正常读取"""
        content = "招聘全栈工程师，要求精通 Python 和 React"
        with tempfile.NamedTemporaryFile(suffix=".txt", mode="w", delete=False, encoding="utf-8") as f:
            f.write(content)
            tmp_path = f.name
        try:
            result = read_jd(tmp_path)
            assert result == content
        finally:
            os.unlink(tmp_path)


class TestAIClient:
    """AI 客户端测试（Mock 模式）"""

    def test_extract_mock(self):
        """测试 Mock 模式下的信息提取"""
        resume_text = "张三，北京大学硕士，技能：Python, React"
        result = extract_resume_info(resume_text, mock=True)
        assert "name" in result
        assert "phone" in result
        assert "email" in result
        assert "education" in result
        assert "skills" in result
        assert isinstance(result["education"], list)
        assert isinstance(result["skills"], list)

    def test_score_mock(self):
        """测试 Mock 模式下的评分"""
        resume_text = "张三的简历内容"
        jd_text = "招聘全栈工程师"
        result = score_resume(resume_text, jd_text, mock=True)
        assert "overall_score" in result
        assert "skill_score" in result
        assert "experience_score" in result
        assert "education_score" in result
        assert "comment" in result
        assert "interview_questions" in result
        assert 0 <= result["overall_score"] <= 100
        assert isinstance(result["interview_questions"], list)

    def test_fix_json_markdown(self):
        """测试 JSON 修复 - markdown 代码块"""
        input_text = '```json\n{"name": "test"}\n```'
        result = _fix_json(input_text)
        data = json.loads(result)
        assert data["name"] == "test"

    def test_fix_json_plain(self):
        """测试 JSON 修复 - 纯 JSON"""
        input_text = '{"name": "test"}'
        result = _fix_json(input_text)
        data = json.loads(result)
        assert data["name"] == "test"
