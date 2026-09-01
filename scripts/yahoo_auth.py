#!/usr/bin/env python3
"""One-time Yahoo OAuth handshake + token refresh helper.

Prereqs:
  1. Create a Yahoo developer app at https://developer.yahoo.com/apps/create/
     - API permission: Fantasy Sports (read)
     - Redirect URI: see docs/yahoo-api.md for what's currently allowed
  2. Copy .env.example to .env and fill in YAHOO_CLIENT_ID / YAHOO_CLIENT_SECRET.
  3. Run: python3 scripts/yahoo_auth.py
     Opens the consent URL (you click Agree), then exchanges the code for tokens
     and writes the refresh token back to .env.

This is a starter — swap in the yfpy / yahoo_fantasy_api library once
docs/yahoo-api.md settles on one.
"""
import base64
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

AUTH_URL = "https://api.login.yahoo.com/oauth2/request_auth"
TOKEN_URL = "https://api.login.yahoo.com/oauth2/get_token"
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


def save_refresh_token(token: str) -> None:
    lines = ENV_PATH.read_text().splitlines()
    out, found = [], False
    for line in lines:
        if line.startswith("YAHOO_REFRESH_TOKEN="):
            out.append(f"YAHOO_REFRESH_TOKEN={token}")
            found = True
        else:
            out.append(line)
    if not found:
        out.append(f"YAHOO_REFRESH_TOKEN={token}")
    ENV_PATH.write_text("\n".join(out) + "\n")


def token_request(client_id: str, client_secret: str, data: dict) -> dict:
    auth = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    req = urllib.request.Request(
        TOKEN_URL,
        data=urllib.parse.urlencode(data).encode(),
        headers={
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)


def main() -> None:
    env = load_env()
    client_id = env.get("YAHOO_CLIENT_ID")
    client_secret = env.get("YAHOO_CLIENT_SECRET")
    if not client_id or not client_secret:
        sys.exit("Fill in YAHOO_CLIENT_ID and YAHOO_CLIENT_SECRET in .env first.")

    redirect_uri = "oob"  # out-of-band: Yahoo shows you a code to paste back here
    params = urllib.parse.urlencode(
        {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "language": "en-us",
        }
    )
    print("\nOpen this URL, sign in, click Agree, and copy the code shown:\n")
    print(f"  {AUTH_URL}?{params}\n")
    code = input("Paste the code here: ").strip()

    tokens = token_request(
        client_id,
        client_secret,
        {
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri,
            "code": code,
        },
    )
    save_refresh_token(tokens["refresh_token"])
    print("\nRefresh token saved to .env — you're wired up.")
    print("Access token (expires in ~1h) obtained; future pulls will auto-refresh.")


if __name__ == "__main__":
    main()
