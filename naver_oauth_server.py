import os
import secrets
from flask import Flask, request, redirect, jsonify, make_response

# naver_openapi.py의 헬퍼 사용
from naver_openapi import auth_url, exchange_token

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", secrets.token_hex(16))

# ───────────────────────── routes ─────────────────────────

@app.route("/health", methods=["GET"])
def health():
    # 간단한 상태 확인용
    return jsonify({"ok": True})

@app.route("/", methods=["GET"])
def home():
    return '<a href="/naver_auth">네이버 블로그 연동 시작</a>'

@app.route("/naver_auth", methods=["GET"])
def naver_auth():
    # 필요시 state를 세션에 저장해 검증하도록 확장 가능
    return redirect(auth_url())

@app.route("/naver/callback", methods=["GET"])
def naver_callback():
    error = request.args.get("error")
    if error:
        return make_response(f"네이버 오류: {error}", 400)

    code = request.args.get("code")
    state = request.args.get("state") or "starbuild-blog"
    if not code:
        return make_response("네이버에서 code가 오지 않았습니다.", 400)

    try:
        tokens = exchange_token(code, state)
    except Exception as e:
        return make_response(f"토큰 교환 실패: {e}", 500)

    return jsonify({"message": "연동 완료! tokens saved.", "tokens": tokens})

# ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "10000"))
    app.run(host="0.0.0.0", port=port)
