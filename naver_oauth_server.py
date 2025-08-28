# naver_oauth_server.py
import os
import secrets
from pathlib import Path
from flask import Flask, request, redirect, jsonify, make_response, render_template

from naver_openapi import auth_url, exchange_token

# ─────────────────────────────────────────────────────────
# Flask 설정: site/ 폴더를 템플릿/정적 경로(절대경로)로 사용
# ─────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent.resolve()

app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "site"),
    static_folder=str(BASE_DIR / "site"),
    static_url_path="/static",
)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", secrets.token_hex(16))


# ─────────────────────────────────────────────────────────
# 공통 보안 헤더
# ─────────────────────────────────────────────────────────
@app.after_request
def add_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Cache-Control"] = "no-store"
    return response


# ─────────────────────────────────────────────────────────
# 헬스체크
# ─────────────────────────────────────────────────────────
@app.get("/health")
def health():
    return jsonify({"ok": True})


# ─────────────────────────────────────────────────────────
# 기본 페이지
# ─────────────────────────────────────────────────────────
@app.get("/")
def home():
    return render_template("index.html")


@app.get("/about")
def about():
    return render_template("about.html")


@app.get("/privacy")
def privacy():
    return render_template("privacy.html")


@app.get("/tos")
def tos():
    return render_template("tos.html")


# ─────────────────────────────────────────────────────────
# .html → 깔끔 경로로 리다이렉트
# ─────────────────────────────────────────────────────────
@app.get("/about.html")
def about_html_redirect():
    return redirect("/about", code=301)

@app.get("/privacy.html")
def privacy_html_redirect():
    return redirect("/privacy", code=301)

@app.get("/tos.html")
def tos_html_redirect():
    return redirect("/tos", code=301)


# ─────────────────────────────────────────────────────────
# robots.txt & sitemap.xml  (site/에 두기)
# ─────────────────────────────────────────────────────────
@app.get("/robots.txt")
def robots():
    return app.send_static_file("robots.txt")

@app.get("/sitemap.xml")
def sitemap():
    return app.send_static_file("sitemap.xml")


# ─────────────────────────────────────────────────────────
# 네이버 OAuth 플로우
# ─────────────────────────────────────────────────────────
@app.get("/naver_auth")
def naver_auth():
    return redirect(auth_url())

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


# ─────────────────────────────────────────────────────────
# 에러 핸들러 (site/404.html, site/500.html 필요)
# ─────────────────────────────────────────────────────────
@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template("500.html"), 500


# ─────────────────────────────────────────────────────────
# 로컬 실행용 (Render에선 gunicorn 사용)
# ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", "10000"))
    app.run(host="0.0.0.0", port=port)
