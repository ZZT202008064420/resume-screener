import io
import re
import hashlib
import pdfplumber


class ResumeParser:

    def parse(self, pdf_bytes: bytes) -> dict:
        """主入口：提取文本 + 清洗"""
        file_hash = hashlib.md5(pdf_bytes).hexdigest()
        file_size = len(pdf_bytes)

        # 优先用 pdfplumber
        result = self._extract_with_pdfplumber(pdf_bytes)

        # 文本太少（可能是扫描件），降级到 PyMuPDF
        if len(result["raw_text"].strip()) < 50:
            result = self._extract_with_pymupdf(pdf_bytes)

        result["file_hash"] = file_hash
        result["file_size"] = file_size
        result["cleaned_text"] = self._clean(result["raw_text"])
        return result

    # ── 提取器 ──────────────────────────────────────────────

    def _extract_with_pdfplumber(self, pdf_bytes: bytes) -> dict:
        pages_text = []
        try:
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                page_count = len(pdf.pages)
                for page in pdf.pages:
                    text = page.extract_text(x_tolerance=3, y_tolerance=3) or ""
                    pages_text.append(text)
        except Exception as e:
            return {"raw_text": "", "page_count": 0, "parser": "pdfplumber_failed", "error": str(e)}

        return {
            "raw_text": "\n".join(pages_text),
            "page_count": page_count,
            "parser": "pdfplumber"
        }

    def _extract_with_pymupdf(self, pdf_bytes: bytes) -> dict:
        """备用：PyMuPDF，对扫描件更友好"""
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            pages_text = [page.get_text() for page in doc]
            return {
                "raw_text": "\n".join(pages_text),
                "page_count": len(doc),
                "parser": "pymupdf"
            }
        except Exception as e:
            return {"raw_text": "", "page_count": 0, "parser": "pymupdf_failed", "error": str(e)}

    # ── 清洗 ─────────────────────────────────────────────────

    def _clean(self, text: str) -> str:
        # 去控制字符
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
        # 合并多余空格（保留换行）
        text = re.sub(r'[ \t]+', ' ', text)
        # 超过2个空行压缩
        text = re.sub(r'\n{3,}', '\n\n', text)
        # 去除每行首尾空格
        lines = [line.strip() for line in text.split('\n')]
        # 去掉纯空行堆叠
        cleaned_lines = []
        prev_empty = False
        for line in lines:
            is_empty = line == ''
            if is_empty and prev_empty:
                continue
            cleaned_lines.append(line)
            prev_empty = is_empty

        return '\n'.join(cleaned_lines).strip()