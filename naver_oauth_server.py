import os
import secrets
from flask import Flask, request, redirect, jsonify, make_response, render_template

from naver_openapi import auth_url, exchange_token

# Flask 앱 정의: 템플릿/정적 파일을 site/에서 서빙
app = Flask(
    __name__,
    template_folder="site",   # index.html, about.html, privacy.html, tos.html
    static_folder="site",     # 필요한 경우 정적 리소스도 같은 폴더
    static_url_path="/static",
)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", secrets.token_hex(16))


# 상태 확인
@app.get("/health")
def health():
    return jsonify({"ok": True})


# 홈 화면
@app.get("/")
def home():
    return render_template("index.html")


# 네이버 로그인 시작
@app.get("/naver_auth")
def naver_auth():
    return redirect(auth_url())


# 네이버 콜백 처리
@app.get("/naver/callback")
def naver_callback():
    err = request.args.get("error")
    if err:
        return make_response(f"네이버 오류: {err}", 400)

    code = request.args.get("code")
    state = request.args.get("state") or "starbuild-blog"

    if not code:
        return make_response("네이버에서 code가 오지 않았습니다.", 400)

    tokens = exchange_token(code, state)
    return jsonify({"message": "연동 완료! tokens saved.", "tokens": tokens})


# 문서 페이지
@app.get("/about")
def about():
    return render_template("about.html")


@app.get("/privacy")
def privacy():
    return render_template("privacy.html")


@app.get("/tos")
def tos():
    return render_template("tos.html")


# *.html → 깔끔한 경로로 리다이렉트
@app.get("/about.html")
def about_html():
    return redirect("/about", code=301)


@app.get("/privacy.html")
def privacy_html():
    return redirect("/privacy", code=301)


@app.get("/tos.html")
def tos_html():
    return redirect("/tos", code=301)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "10000"))
    app.run(host="0.0.0.0", port=port)
