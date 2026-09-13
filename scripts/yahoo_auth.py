#!/usr/bin/env python3
"""Yahoo OAuth handshake + token refresh helper (localhost-redirect flow).

Usage:
  python3 scripts/yahoo_auth.py url
      Print the consent URL. Open it, sign in, click Agree. The browser will
      try to load https://localhost:8080/?code=... and fail to connect —
      that's expected. Copy the full URL from the address bar.

  python3 scripts/yahoo_auth.py code '<pasted url or bare code>'
      Exchange the code for tokens; saves the refresh token into .env.

  python3 scripts/yahoo_auth.py token
      Print a fresh access token (auto-refresh from the saved refresh token).
"""
import base64
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

AUTH_URL = "https://api.login.yahoo.com/oauth2/request_auth"
TOKEN_URL = "https://api.login.yahoo.com/oauth2/get_token"
REDIRECT_URI = "https://localhost:8080"
ENV_PATH = Path(__file__).resolve().parent.parent / ".env"


def load_env() -> dict:
    env = {}
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env


def set_env(key: str, value: str) -> None:
    lines = ENV_PATH.read_text().splitlines() if ENV_PATH.exists() else []
    out, found = [], False
    for line in lines:
        if line.startswith(key + "="):
            out.append(f"{key}={value}")
            found = True
        else:
            out.append(line)
    if not found:
        out.append(f"{key}={value}")
    ENV_PATH.write_text("\n".join(out) + "\n")


def token_request(data: dict) -> dict:
    env = load_env()
    auth = base64.b64encode(
        f"{env['YAHOO_CLIENT_ID']}:{env['YAHOO_CLIENT_SECRET']}".encode()
    ).decode()
    req = urllib.request.Request(
        TOKEN_URL,
        data=urllib.parse.urlencode(data).encode(),
        headers={
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as e:
        sys.exit(f"Token request failed: HTTP {e.code}\n{e.read().decode()}")


def cmd_url() -> None:
    env = load_env()
    params = urllib.parse.urlencode(
        {
            "client_id": env["YAHOO_CLIENT_ID"],
            "redirect_uri": REDIRECT_URI,
            "response_type": "code",
            "language": "en-us",
        }
    )
    print(f"{AUTH_URL}?{params}")


def cmd_code(raw: str) -> None:
    code = raw.strip()
    if "code=" in code:  # full redirect URL pasted
        code = urllib.parse.parse_qs(urllib.parse.urlparse(code).query)["code"][0]
    tokens = token_request(
        {"grant_type": "authorization_code", "redirect_uri": REDIRECT_URI, "code": code}
    )
    set_env("YAHOO_REFRESH_TOKEN", tokens["refresh_token"])
    print("Refresh token saved to .env.")


def cmd_token() -> None:
    env = load_env()
    rt = env.get("YAHOO_REFRESH_TOKEN")
    if not rt:
        sys.exit("No YAHOO_REFRESH_TOKEN in .env — run the url/code steps first.")
    tokens = token_request(
        {"grant_type": "refresh_token", "redirect_uri": REDIRECT_URI, "refresh_token": rt}
    )
    # Yahoo may rotate the refresh token — always persist the newest one.
    if tokens.get("refresh_token") and tokens["refresh_token"] != rt:
        set_env("YAHOO_REFRESH_TOKEN", tokens["refresh_token"])
    print(tokens["access_token"])


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in ("url", "code", "token"):
        sys.exit(__doc__)
    if sys.argv[1] == "url":
        cmd_url()
    elif sys.argv[1] == "code":
        if len(sys.argv) < 3:
            sys.exit("Usage: yahoo_auth.py code '<pasted url or code>'")
        cmd_code(sys.argv[2])
    else:
        cmd_token()
