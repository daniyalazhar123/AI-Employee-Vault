"""
dependency_fallback_guard.py — Transparent dependency proxy for AI-Employee-Vault.

Decouples third-party transport layers (twilio, fastapi, uvicorn, PyPDF2) from
local core orchestration by providing proxy/wrapper classes that:

- Pass through to real libraries when detected via importlib.util.
- Fall back to local non-dependent alternatives when libraries are missing.
- Emit structured architecture warnings via audit_logger on every fallback.

Usage:
    from dependency_fallback_guard import (
        TwilioClientProxy,
        FastAPIProxy,
        UvicornProxy,
        PyPDF2Proxy,
        Response,
        FileResponse,
        HTMLResponse,
        PlainTextResponse,
        Request,
        HTTPException,
        CORSMiddleware,
        StaticFiles,
        TWILIO_AVAILABLE,
        FASTAPI_AVAILABLE,
        UVICORN_AVAILABLE,
        PYPDF2_AVAILABLE,
    )
"""

__all__: list[str] = [
    'TwilioClientProxy',
    'FastAPIProxy',
    'UvicornProxy',
    'PyPDF2Proxy',
    'PdfPageProxy',
    'PdfReaderProxy',
    'Response',
    'FileResponse',
    'HTMLResponse',
    'PlainTextResponse',
    'Request',
    'HTTPException',
    'CORSMiddleware',
    'StaticFiles',
    'TWILIO_AVAILABLE',
    'FASTAPI_AVAILABLE',
    'UVICORN_AVAILABLE',
    'PYPDF2_AVAILABLE',
]

import importlib.util
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable

from audit_logger import log_action

logger = logging.getLogger('DependencyGuard')
if not logger.handlers:
    from audit_logger import setup_logging
    logger = setup_logging('DependencyGuard')


# =====================================================================
# Module presence detection via importlib.util
# =====================================================================

def _module_available(module_name: str) -> bool:
    try:
        spec = importlib.util.find_spec(module_name)
        return spec is not None
    except (ValueError, TypeError, ImportError):
        return False


TWILIO_AVAILABLE: bool = _module_available('twilio')
FASTAPI_AVAILABLE: bool = _module_available('fastapi')
UVICORN_AVAILABLE: bool = _module_available('uvicorn')
PYPDF2_AVAILABLE: bool = _module_available('PyPDF2')


# =====================================================================
# Twilio Proxy
# =====================================================================

class TwilioCallProxy:
    __slots__ = ('sid',)

    def __init__(self, sid: str = 'FALLBACK_CALL_SID') -> None:
        self.sid: str = sid


class TwilioCallsProxy:
    __slots__ = ()

    def create(self, url: str = '', to: str = '', from_: str = '',
               timeout: int = 30, machine_detection: str = '') -> TwilioCallProxy:
        log_action(
            'twilio_proxy',
            {'to': to, 'from_': from_, 'status': 'fallback'},
            'info',
            actor='dependency_guard',
            target='twilio.calls.create',
        )
        return TwilioCallProxy(sid='FALLBACK_SID')


class TwilioClientProxy:
    __slots__ = ('_account_sid', '_auth_token', '_real_client', '_calls_proxy')

    def __init__(self, account_sid: str = '', auth_token: str = '') -> None:
        self._account_sid: str = account_sid
        self._auth_token: str = auth_token
        self._real_client: Any = None
        self._calls_proxy: Optional[TwilioCallsProxy] = None
        if TWILIO_AVAILABLE:
            try:
                from twilio.rest import Client as _RealTwilioClient
                self._real_client = _RealTwilioClient(account_sid, auth_token)
            except Exception as exc:
                log_action(
                    'twilio_proxy',
                    {'error': str(exc)},
                    'failed',
                    actor='dependency_guard',
                    target='twilio.rest.Client',
                )
                self._real_client = None

    @property
    def calls(self) -> Any:
        if self._real_client is not None:
            return self._real_client.calls
        if self._calls_proxy is None:
            self._calls_proxy = TwilioCallsProxy()
        return self._calls_proxy


# =====================================================================
# FastAPI Fallback Types
# (used only when fastapi is NOT installed)
# =====================================================================

class _FallbackRequest:
    __slots__ = ()


class _FallbackResponse:
    __slots__ = ('content', 'media_type', 'status_code')

    def __init__(self, content: Any = '', media_type: str = 'text/plain',
                 status_code: int = 200) -> None:
        self.content: Any = content
        self.media_type: str = media_type
        self.status_code: int = status_code


class _FallbackFileResponse(_FallbackResponse):
    __slots__ = ()


class _FallbackHTMLResponse(_FallbackResponse):
    __slots__ = ()


class _FallbackPlainTextResponse(_FallbackResponse):
    __slots__ = ()


class _FallbackCORSMiddleware:
    __slots__ = ()


class _FallbackStaticFiles:
    __slots__ = ('directory', 'packages', 'html', 'check_dir')

    def __init__(self, directory: Optional[str] = None,
                 packages: Optional[List[str]] = None,
                 html: bool = False, check_dir: bool = True) -> None:
        self.directory = directory
        self.packages = packages
        self.html = html
        self.check_dir = check_dir


class _FallbackHTTPException(Exception):
    __slots__ = ('status_code', 'detail')

    def __init__(self, status_code: int = 500, detail: str = '') -> None:
        self.status_code: int = status_code
        self.detail: str = detail
        super().__init__(detail)


# =====================================================================
# FastAPI sub-imports: resolve once at module level
# =====================================================================

if FASTAPI_AVAILABLE:
    try:
        from fastapi import Request as Request  # type: ignore[assignment]
        from fastapi import HTTPException as HTTPException  # type: ignore[assignment]
        from fastapi.responses import Response as Response  # type: ignore[assignment]
        from fastapi.responses import FileResponse as FileResponse  # type: ignore[assignment]
        from fastapi.responses import HTMLResponse as HTMLResponse  # type: ignore[assignment]
        from fastapi.responses import PlainTextResponse as PlainTextResponse  # type: ignore[assignment]
        from fastapi.middleware.cors import CORSMiddleware as CORSMiddleware  # type: ignore[assignment]
        from fastapi.staticfiles import StaticFiles as StaticFiles  # type: ignore[assignment]
    except ImportError as exc:
        logger.error(f"fastapi import failed despite find_spec: {exc}")
        Request = _FallbackRequest
        HTTPException = _FallbackHTTPException
        Response = _FallbackResponse
        FileResponse = _FallbackFileResponse
        HTMLResponse = _FallbackHTMLResponse
        PlainTextResponse = _FallbackPlainTextResponse
        CORSMiddleware = _FallbackCORSMiddleware
        StaticFiles = _FallbackStaticFiles
else:
    Request = _FallbackRequest
    HTTPException = _FallbackHTTPException
    Response = _FallbackResponse
    FileResponse = _FallbackFileResponse
    HTMLResponse = _FallbackHTMLResponse
    PlainTextResponse = _FallbackPlainTextResponse
    CORSMiddleware = _FallbackCORSMiddleware
    StaticFiles = _FallbackStaticFiles


# =====================================================================
# FastAPI App Proxy
# =====================================================================

class _RouteStore:
    __slots__ = ('routes', 'events')

    def __init__(self) -> None:
        self.routes: Dict[str, Callable] = {}
        self.events: Dict[str, Callable] = {}

    def get(self, path: str) -> Callable:
        def _inner(func: Callable) -> Callable:
            key: str = f'GET {path}'
            self.routes[key] = func
            return func
        return _inner

    def post(self, path: str) -> Callable:
        def _inner(func: Callable) -> Callable:
            key: str = f'POST {path}'
            self.routes[key] = func
            return func
        return _inner

    def put(self, path: str) -> Callable:
        def _inner(func: Callable) -> Callable:
            key: str = f'PUT {path}'
            self.routes[key] = func
            return func
        return _inner

    def delete(self, path: str) -> Callable:
        def _inner(func: Callable) -> Callable:
            key: str = f'DELETE {path}'
            self.routes[key] = func
            return func
        return _inner

    def on_event(self, event: str) -> Callable:
        def _inner(func: Callable) -> Callable:
            self.events[event] = func
            return func
        return _inner

    def add_middleware(self, middleware_class: Any, **kwargs: Any) -> None:
        log_action(
            'fastapi_proxy',
            {'middleware': getattr(middleware_class, '__name__', str(middleware_class))},
            'info',
            actor='dependency_guard',
            target='fastapi.add_middleware',
        )

    def mount(self, path: str, app: Any, name: str = '') -> None:
        log_action(
            'fastapi_proxy',
            {'mount_path': path, 'name': name},
            'info',
            actor='dependency_guard',
            target='fastapi.mount',
        )


class FastAPIProxy:
    __slots__ = ('_real_app', '_route_store')

    def __init__(self, title: str = '') -> None:
        self._real_app: Any = None
        self._route_store: Optional[_RouteStore] = None
        if FASTAPI_AVAILABLE:
            try:
                from fastapi import FastAPI as _RealFastAPI
                self._real_app = _RealFastAPI(title=title)
            except Exception as exc:
                log_action(
                    'fastapi_proxy',
                    {'error': str(exc)},
                    'failed',
                    actor='dependency_guard',
                    target='fastapi.FastAPI',
                )
                self._route_store = _RouteStore()
        else:
            self._route_store = _RouteStore()

    def __getattr__(self, name: str) -> Any:
        if self._real_app is not None and hasattr(self._real_app, name):
            return getattr(self._real_app, name)
        if self._route_store is not None and hasattr(self._route_store, name):
            return getattr(self._route_store, name)
        raise AttributeError(
            f"'{type(self).__name__}' object has no attribute '{name}'"
        )

    def add_middleware(self, middleware_class: Any, **kwargs: Any) -> None:
        if self._real_app is not None:
            self._real_app.add_middleware(middleware_class, **kwargs)
        elif self._route_store is not None:
            self._route_store.add_middleware(middleware_class, **kwargs)

    def mount(self, path: str, app: Any, name: str = '') -> None:
        if self._real_app is not None:
            self._real_app.mount(path, app, name=name)
        elif self._route_store is not None:
            self._route_store.mount(path, app, name=name)


# =====================================================================
# Uvicorn Proxy
# =====================================================================

class UvicornProxy:
    __slots__ = ()

    @staticmethod
    def run(app: Any, host: str = '0.0.0.0', port: int = 8000,
            log_level: str = 'info', **kwargs: Any) -> None:
        if UVICORN_AVAILABLE:
            try:
                import uvicorn as _real_uvicorn
                _real_uvicorn.run(app, host=host, port=port,
                                  log_level=log_level, **kwargs)
            except Exception as exc:
                log_action(
                    'uvicorn_proxy', {'error': str(exc)},
                    'failed', actor='dependency_guard', target='uvicorn.run',
                )
                logger.error(f"uvicorn.run failed: {exc}")
        else:
            log_action(
                'uvicorn_proxy',
                {'host': host, 'port': port, 'status': 'fallback'},
                'info', actor='dependency_guard', target='uvicorn.run',
            )
            logger.info(
                f"uvicorn not available — server start skipped on {host}:{port}. "
                f"Install: pip install uvicorn"
            )


# =====================================================================
# PyPDF2 Proxy
# =====================================================================

class PdfPageProxy:
    __slots__ = ('_text',)

    def __init__(self, text: str = '') -> None:
        self._text: str = text

    def extract_text(self) -> str:
        return self._text


class PdfReaderProxy:
    __slots__ = ('pages',)

    def __init__(self, file_path: Path) -> None:
        self.pages: List[PdfPageProxy] = []
        if PYPDF2_AVAILABLE:
            try:
                import PyPDF2 as _real_pypdf2
                with open(file_path, 'rb') as f:
                    reader = _real_pypdf2.PdfReader(f)
                    for page in reader.pages:
                        self.pages.append(PdfPageProxy(page.extract_text()))
            except Exception as exc:
                log_action(
                    'pypdf2_proxy',
                    {'file': str(file_path), 'error': str(exc)},
                    'failed', actor='dependency_guard', target='PyPDF2.PdfReader',
                )
                logger.error(f"PyPDF2 read failed for {file_path}: {exc}")
        else:
            log_action(
                'pypdf2_proxy',
                {'file': str(file_path), 'status': 'fallback'},
                'info', actor='dependency_guard', target='PyPDF2.PdfReader',
            )
            logger.info(
                f"PyPDF2 not available — returning empty pages for {file_path.name}"
            )


class PyPDF2Proxy:
    __slots__ = ()

    @staticmethod
    def PdfReader(file_path: Path) -> PdfReaderProxy:
        return PdfReaderProxy(file_path)
