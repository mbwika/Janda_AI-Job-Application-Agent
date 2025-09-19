"""Utility for downloading model files with retries, timeouts, atomic write and optional SHA256 verification.

This module provides `download_model` so other parts of the project can reuse it.

Design goals / notes:
- Use timeouts and retries to avoid hanging network calls (addresses Bandit B113).
- Write to a temporary file and atomically replace the destination to avoid partial files.
- Optional SHA256 verification to ensure integrity of large model files.
- Keep imports lightweight so this module can be used in tests and CI.
"""
from __future__ import annotations

import hashlib
import logging
import os
import tempfile
import time
from typing import Optional, Tuple

import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import RequestException
from urllib3.util.retry import Retry


logger = logging.getLogger(__name__)


def download_model(
    url: str,
    dest_path: str,
    *,
    model_sha256: Optional[str] = None,
    timeout: Tuple[int, int] = (10, 60),
    total_retries: int = 5,
    backoff_factor: float = 1.0,
    progress: bool = False,
) -> None:
    """Download a model from `url` to `dest_path`.

    Parameters
    - url: remote HTTP(S) URL to stream-download.
    - dest_path: local filesystem path where the model will be saved.
    - model_sha256: optional lower-hex SHA256 checksum to verify the download.
    - timeout: pair (connect_timeout, read_timeout) passed to requests.
    - total_retries/backoff_factor: retry policy for transient failures.
    - progress: when True, emits periodic INFO logs about progress.

    Raises RuntimeError on network failures or checksum mismatch.
    """

    logger.info("Model file not found at %s. Downloading from %s...", dest_path, url)

    session = requests.Session()
    retries = Retry(
        total=total_retries,
        backoff_factor=backoff_factor,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "POST"],
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    try:
        with session.get(url, stream=True, timeout=timeout) as response:
            response.raise_for_status()

            # Read content-length header and convert to int when present.
            # Use a separate variable to avoid `str | None` -> `int` assignment
            # which mypy flags as incompatible.
            total_header = response.headers.get("content-length")
            total: Optional[int] = None
            if total_header is not None:
                try:
                    total = int(total_header)
                except (TypeError, ValueError):
                    # If header is malformed, treat as unknown size.
                    total = None

            with tempfile.NamedTemporaryFile(delete=False) as tmpf:
                tmp_path = tmpf.name
                sha256 = hashlib.sha256()
                downloaded = 0
                start = time.time()
                for chunk in response.iter_content(chunk_size=8192):
                    if not chunk:
                        continue
                    tmpf.write(chunk)
                    if model_sha256:
                        sha256.update(chunk)
                    downloaded += len(chunk)

                    if progress and (downloaded % (1024 * 1024) < len(chunk) or (total and downloaded == total)):
                        elapsed = time.time() - start
                        percent = (downloaded / total * 100) if total is not None and total != 0 else None
                        if percent is not None:
                            logger.info("Downloaded %d/%d bytes (%.1f%%) in %.1fs", downloaded, total, percent, elapsed)
                        else:
                            logger.info("Downloaded %d bytes in %.1fs", downloaded, elapsed)

            if model_sha256:
                digest = sha256.hexdigest()
                if digest != model_sha256.lower():
                    try:
                        os.remove(tmp_path)
                    except Exception as remove_err:
                        logger.warning("Failed to remove temporary file %s: %s", tmp_path, remove_err)
                    raise RuntimeError(
                        f"SHA256 mismatch for downloaded model: expected {model_sha256}, got {digest}"
                    )

            os.replace(tmp_path, dest_path)

        logger.info("Model downloaded to %s.", dest_path)
    except RequestException as e:
        raise RuntimeError(f"Failed to download model from {url}: {e}") from e
