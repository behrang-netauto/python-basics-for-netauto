from __future__ import annotations

from typing import Any, Dict


def extract_creds(vault: Dict[str, Any]) -> Dict[str, str]:
    """{
  "username": "<str>",
  "password": "<str>",
  "secret": "<str optional>"
    }"""
    creds = vault.get("credentials")
    if not isinstance(creds, dict):
        raise ValueError("vault.yml must contain top-level key 'credentials'")
    username = creds.get("username")
    password = creds.get("password")
    secret = creds.get("secret")
    if not username or not password:
        raise ValueError("vault credentials must include 'username' and 'password'")
    out = {"username": str(username), "password": str(password)}
    if secret:
        out["secret"] = str(secret)
    return out
