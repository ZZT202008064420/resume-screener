import io
import json
import hashlib
import os
import cgi
from dotenv import load_dotenv

load_dotenv()  # 本地读取 .env，FC上从环境变量读

from modules.parser import ResumeParser
from modules.extractor import InfoExtractor
from modules.scorer import ResumeScorer
from modules.cache import CacheManager
from utils.response import success, error
from utils.validator import validate_pdf, validate_score_request

# 模块单例（FC实例复用，避免重复初始化）
parser = ResumeParser()
extractor = InfoExtractor()
scorer = ResumeScorer()
cache = CacheManager()


def handler(environ, start_response):
    """阿里云FC HTTP触发器入口（WSGI）"""
    method = environ.get("REQUEST_METHOD", "GET")
    path = environ.get("PATH_INFO", "/")

    # OPTIONS 预检（CORS）
    if method == "OPTIONS":
        start_response("200 OK", [
            ("Access-Control-Allow-Origin", "*"),
            ("Access-Control-Allow-Methods", "GET, POST, OPTIONS"),
            ("Access-Control-Allow-Headers", "Content-Type"),
        ])
        return [b""]

    routes = {
        ("POST", "/api/resume/upload"): handle_upload,
        ("POST", "/api/resume/score"):  handle_score,
        ("GET",  "/health"):            handle_health,
    }

    handler_fn = routes.get((method, path))
    if handler_fn:
        return handler_fn(environ, start_response)
    return error(404, f"路由不存在: {method} {path}", start_response)


# ── 路由处理函数 ──────────────────────────────────────────────────────────

def handle_health(environ, start_response):
    return success({"status": "ok", "version": "1.0.0"}, start_response)


def handle_upload(environ, start_response):
    try:
        content_type = environ.get("CONTENT_TYPE", "")
        content_length = int(environ.get("CONTENT_LENGTH", 0))

        if "multipart/form-data" not in content_type:
            return error(400, "Content-Type 必须为 multipart/form-data", start_response)

        # 解析 multipart 表单
        form = cgi.FieldStorage(
            fp=environ["wsgi.input"],
            environ=environ,
            keep_blank_values=True
        )

        if "file" not in form:
            return error(400, "未找到上传字段 'file'", start_response)

        file_item = form["file"]
        filename = file_item.filename or "unknown.pdf"
        pdf_bytes = file_item.file.read()

        # 校验
        ok, msg = validate_pdf(filename, len(pdf_bytes))
        if not ok:
            return error(400, msg, start_response)

        # 查缓存
        file_hash = hashlib.md5(pdf_bytes).hexdigest()
        cached = cache.get_parsed(file_hash)
        if cached:
            cached["from_cache"] = True
            return success(cached, start_response)

        # 解析 → 提取
        parse_result = parser.parse(pdf_bytes)
        if not parse_result["cleaned_text"].strip():
            return error(422, "PDF 内容为空，可能是扫描件或加密文件", start_response)

        extracted = extractor.extract(parse_result["cleaned_text"])

        result = {
            "file_hash": file_hash,
            "filename": filename,
            "page_count": parse_result["page_count"],
            "parser_used": parse_result["parser"],
            "extracted_info": extracted,
            "from_cache": False
        }

        cache.set_parsed(file_hash, result)
        return success(result, start_response)

    except Exception as e:
        print(f"[Upload] Error: {e}")
        return error(500, f"服务器内部错误: {str(e)}", start_response)


def handle_score(environ, start_response):
    try:
        content_length = int(environ.get("CONTENT_LENGTH", 0))
        body_raw = environ["wsgi.input"].read(content_length)

        try:
            body = json.loads(body_raw)
        except json.JSONDecodeError:
            return error(400, "请求体必须是合法的 JSON", start_response)

        # 校验
        ok, msg = validate_score_request(body)
        if not ok:
            return error(400, msg, start_response)

        file_hash = body["file_hash"]
        job_description = body["job_description"].strip()

        # 查简历缓存
        resume_data = cache.get_parsed(file_hash)
        if not resume_data:
            return error(404, "简历不存在，请重新上传", start_response)

        # 查评分缓存（简历hash + JD内容hash）
        jd_hash = hashlib.md5(job_description.encode()).hexdigest()
        cached_score = cache.get_scored(file_hash, jd_hash)
        if cached_score:
            cached_score["from_cache"] = True
            return success(cached_score, start_response)

        # 评分
        score_result = scorer.score(resume_data["extracted_info"], job_description)

        result = {
            "file_hash": file_hash,
            "jd_hash": jd_hash,
            "candidate_name": resume_data["extracted_info"]["basic_info"].get("name"),
            "score_detail": score_result,
            "total_score": score_result["total_score"],
            "hire_advice": score_result["hire_advice"],
            "from_cache": False
        }

        cache.set_scored(file_hash, jd_hash, result)
        return success(result, start_response)

    except Exception as e:
        print(f"[Score] Error: {e}")
        return error(500, f"服务器内部错误: {str(e)}", start_response)