"""`jige` 실행 스크립트는 확장자가 없어서(curl 설치 후 바로 실행하는 용도) 일반
`import jige`로는 못 찾음 — importlib로 파일 경로를 직접 지정해서 불러옴.
"""
from __future__ import annotations

import importlib.util
import sys
from importlib.machinery import SourceFileLoader
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
JIGE_PATH = REPO_ROOT / "jige"


def load_jige():
    loader = SourceFileLoader("jige_cli", str(JIGE_PATH))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    sys.modules["jige_cli"] = module
    loader.exec_module(module)
    return module
