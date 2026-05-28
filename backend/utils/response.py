import json


def _build(code, message, data, start_response=None, status="200 OK"):
    body = json.dumps({
        "code": code,
        "message": message,
        "data": data
    }, ensure_ascii=False).encode("utf-8")

    headers = [
        ("Content-Type", "application/json; charset=utf-8"),
        ("Content-Length", str(len(body))),
        # 解决前端跨域
        ("Access-Control-Allow-Origin", "*"),
        ("Access-Control-Allow-Methods", "GET, POST, OPTIONS"),
        ("Access-Control-Allow-Headers", "Content-Type"),
    ]

    # FC环境用start_response，本地Flask直接返回dict
    if start_response:
        start_response(status, headers)
        return [body]
    return {"code": code, "message": message, "data": data}


def success(data, start_response=None):
    return _build(0, "success", data, start_response)


def error(http_code, message, start_response=None):
    status_map = {
        400: "400 Bad Request",
        404: "404 Not Found",
        500: "500 Internal Server Error"
    }
    return _build(http_code, message, None, start_response, status_map.get(http_code, "500 Internal Server Error"))