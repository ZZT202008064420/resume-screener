# app_local.py  ← 仅本地用，不上传FC
from flask import Flask, request, jsonify
from handler import handle_upload, handle_score, handle_health
import io
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
def make_wsgi_environ(req):
    """把 Flask request 转成 WSGI environ"""
    body = req.get_data()
    environ = {
        "REQUEST_METHOD": req.method,
        "PATH_INFO": req.path,
        "CONTENT_TYPE": req.content_type,
        "CONTENT_LENGTH": str(len(body)),
        "wsgi.input": io.BytesIO(body),
    }
    return environ

@app.route("/api/resume/upload", methods=["POST", "OPTIONS"])
def upload():
    if request.method == "OPTIONS":
        return "", 200, {"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "Content-Type"}
    environ = make_wsgi_environ(request)
    results = []
    def fake_start_response(status, headers):
        pass
    resp = handle_upload(environ, fake_start_response)
    import json
    return app.response_class(resp[0], mimetype="application/json")

@app.route("/api/resume/score", methods=["POST", "OPTIONS"])
def score():
    if request.method == "OPTIONS":
        return "", 200, {"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "Content-Type"}
    environ = make_wsgi_environ(request)
    def fake_start_response(status, headers): pass
    resp = handle_score(environ, fake_start_response)
    return app.response_class(resp[0], mimetype="application/json")

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(port=8080, debug=True)