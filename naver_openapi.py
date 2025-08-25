import os, json, time
from urllib.parse import urlencode
import requests
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")
REDIRECT_URI = os.getenv("NAVER_REDIRECT_URI")
TOK_PATH = os.path.join("data", "naver_tokens.json")
os.makedirs("data", exist_ok=True)

AUTH_BASE = "https://nid.naver.com/oauth2.0/authorize"
TOKEN_URL = "https://nid.naver.com/oauth2.0/token"
WRITE_POST_URL = "https://openapi.naver.com/blog/writePost.json"
LIST_CATEGORY_URL = "https://openapi.naver.com/blog/listCategory.json"

def save_tokens(tok):
    with open(TOK_PATH, "w", encoding="utf-8") as f:
        json.dump(tok, f, ensure_ascii=False, indent=2)

def load_tokens():
    if not os.path.exists(TOK_PATH):
        return None
    with open(TOK_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def auth_url(state="starbuild-blog"):
    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "state": state,
        "scope": "blog"
    }
    return f"{AUTH_BASE}?{urlencode(params)}"

def exchange_token(code, state="starbuild-blog"):
    params = {
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "state": state,
    }
    r = requests.post(TOKEN_URL, params=params, timeout=30)
    r.raise_for_status()
    tok = r.json()
    tok["saved_at"] = int(time.time())
    save_tokens(tok)
    return tok

def refresh_token():
    tok = load_tokens()
    if not tok or "refresh_token" not in tok:
        raise RuntimeError("토큰이 없습니다. 먼저 /naver_auth 로 승인하세요.")
    params = {
        "grant_type": "refresh_token",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": tok["refresh_token"],
    }
    r = requests.post(TOKEN_URL, params=params, timeout=30)
    r.raise_for_status()
    newt = tok | r.json()
    newt["saved_at"] = int(time.time())
    save_tokens(newt)
    return newt

def _auth_headers():
    tok = load_tokens()
    if not tok or "access_token" not in tok:
        raise RuntimeError("액세스 토큰이 없습니다. /naver_auth 후 다시 시도하세요.")
    return {"Authorization": f"Bearer {tok['access_token']}"}

def list_categories():
    headers = _auth_headers()
    r = requests.post(LIST_CATEGORY_URL, headers=headers, timeout=30)
    r.raise_for_status()
    return r.json()

def write_post(title:str, contents:str, category_no:str|None=None, tags:str|None=None):
    headers = _auth_headers()
    data = {"title": title, "contents": contents}
    if category_no:
        data["categoryNo"] = category_no
    if tags:
        data["tag"] = tags
    r = requests.post(WRITE_POST_URL, headers=headers, data=data, timeout=30)
    if r.status_code == 401:
        refresh_token()
        headers = _auth_headers()
        r = requests.post(WRITE_POST_URL, headers=headers, data=data, timeout=30)
    r.raise_for_status()
    return r.json()
