import os
import json
import secrets
from pathlib import Path
from urllib.parse import urlencode

import requests
from flask import Flask, redirect, request, session, jsonify, make_response

from flask import Flask, request, redirect
from naver_openapi import auth_url, exchange_token

@app.get("/health")
def health():
    return {"ok": True}

app = Flask(__name__)

@app.get("/")
def home():
    return f'<a href="/naver_auth">네이버 블로그 연동 시작</a>'

@app.get("/naver_auth")
def naver_auth():
    return redirect(auth_url())

@app.get("/naver/callback")
def naver_callback():
    code = request.args.get("code")
    state = request.args.get("state")
    if not code:
        return "네이버에서 code가 오지 않았습니다.", 400
    tok = exchange_token(code, state or "starbuild-blog")
    return f"연동 완료! tokens saved. 파일: data/naver_tokens.json<br>{tok}"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "10000"))  # Render가 주입하는 포트를 사용
    app.run(host="0.0.0.0", port=port)           # 외부 접속 허용



