def validate_pdf(filename: str, file_size: int) -> tuple[bool, str]:
    """校验上传文件"""
    if not filename.lower().endswith(".pdf"):
        return False, "只支持 PDF 格式文件"
    if file_size > 10 * 1024 * 1024:  # 10MB 上限
        return False, "文件大小不能超过 10MB"
    if file_size == 0:
        return False, "文件内容为空"
    return True, ""


def validate_score_request(body: dict) -> tuple[bool, str]:
    """校验评分请求体"""
    if not body.get("file_hash"):
        return False, "缺少 file_hash 参数"
    if not body.get("job_description"):
        return False, "缺少 job_description 参数"
    if len(body["job_description"].strip()) < 10:
        return False, "岗位描述内容太短，请详细描述"
    return True, ""