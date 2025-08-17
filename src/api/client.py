from __future__ import annotations

import os
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class ChangeNowClient:
    """HTTP-клиент для ChangeNOW API с ретраями и опц. API-ключом."""

    def __init__(
        self,
        base_url: str,
        timeout: int = 30,
        api_key: str | None = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

        sess = requests.Session()
        sess.headers.update({"Accept": "application/json"})

        api_key = api_key or os.getenv("API_KEY") or os.getenv(
            "X_CHANGENOW_API_KEY"
        )
        if api_key:
            sess.headers.update({"x-changenow-api-key": api_key})

        retry = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods={"GET", "POST"},
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry)
        sess.mount("http://", adapter)
        sess.mount("https://", adapter)

        self.s = sess

    def get(self, path: str, **kwargs):
        """GET {base_url}{path}."""
        return self.s.get(
            self.base_url + path,
            timeout=self.timeout,
            **kwargs,
        )

    def post(self, path: str, json: dict):
        """POST {base_url}{path} c JSON-телом."""
        return self.s.post(
            self.base_url + path,
            json=json,
            timeout=self.timeout,
        )
