import os
import secrets
from flask import Flask, request, redirect, jsonify, make_response

# naver_openapi.py 에서 제공하는 함수 사용
from naver_openapi import auth_url, exchange_token

app = Flask(__name__)
# 세션/상태(state) 검증을 위해 비밀키 필요
app.secret_key = os.environ.get("FLASK_SECRET_KEY", secrets.token_hex(16))

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/")
def home():
    return '<a href="/naver_auth">네이버 블로그 연동 시작</a>'

@app.get("/naver_auth")
def naver_auth():
    # 필요시 state를 세션에 넣고 검증하도록 확장 가능
    return redirect(auth_url())

@app.get("/naver/callback")
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

    # naver_openapi.exchange_token 내부에서 파일 저장을 한다면 여기선 결과만 반환
    return jsonify({"message": "연동 완료! tokens saved.", "tokens": tokens})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "10000"))  # Render가 주입하는 포트 사용
    app.run(host="0.0.0.0", port=port)           # 외부 접속 허용
