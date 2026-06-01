from __future__ import annotations

import os
import time
from dataclasses import dataclass
from pathlib import Path

import pytest
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"

load_dotenv(ROOT / ".env")


@dataclass(frozen=True)
class DharaConfig:
    base_url: str
    username: str
    password: str
    headless: bool
    viewport: tuple[int, int]
    mutating: bool
    codemp: str
    codproj: str
    codparc: str
    codprod_animal: str
    faixa_descricao: str
    raca_descricao: str
    tipo_exame_descricao: str
    identificacao_prefix: str
    nunota_entrada_base: str
    auto_find_nota: bool


def _bool(name: str, default: str = "0") -> bool:
    return os.getenv(name, default).strip().lower() in {"1", "true", "s", "sim", "yes"}


def _viewport() -> tuple[int, int]:
    raw = os.getenv("VIEWPORT", "1366x768").lower()
    w, h = raw.split("x", 1)
    return int(w), int(h)


@pytest.fixture(scope="session")
def cfg() -> DharaConfig:
    return DharaConfig(
        base_url=os.getenv("SANKHYA_BASE_URL", "http://localhost:8080").rstrip("/"),
        username=os.getenv("SANKHYA_USER", ""),
        password=os.getenv("SANKHYA_PASSWORD", ""),
        headless=_bool("HEADLESS"),
        viewport=_viewport(),
        mutating=_bool("DHARA_E2E_MUTATING"),
        codemp=os.getenv("DHARA_CODEMP", "1"),
        codproj=os.getenv("DHARA_CODPROJ", ""),
        codparc=os.getenv("DHARA_CODPARC", ""),
        codprod_animal=os.getenv("DHARA_CODPROD_ANIMAL", ""),
        faixa_descricao=os.getenv("DHARA_FAIXA_DESCRICAO", "Bezerro Selenium"),
        raca_descricao=os.getenv("DHARA_RACA_DESCRICAO", "Nelore Selenium"),
        tipo_exame_descricao=os.getenv("DHARA_TIPO_EXAME_DESCRICAO", "Ultrassom Selenium"),
        identificacao_prefix=os.getenv("DHARA_IDENTIFICACAO_PREFIX", "SEL"),
        nunota_entrada_base=os.getenv("DHARA_NUNOTA_ENTRADA_BASE", ""),
        auto_find_nota=_bool("DHARA_AUTO_FIND_NOTA_ENTRADA", "1"),
    )


@pytest.fixture()
def driver(cfg: DharaConfig, request: pytest.FixtureRequest):
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    (ARTIFACTS / "screens").mkdir(exist_ok=True)

    width, height = cfg.viewport
    opts = webdriver.ChromeOptions()
    if cfg.headless:
        opts.add_argument("--headless=new")
    opts.add_argument(f"--window-size={width},{height}")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")

    browser = webdriver.Chrome(options=opts)
    browser.implicitly_wait(0)

    yield browser

    failed = hasattr(request.node, "rep_call") and request.node.rep_call.failed
    if failed:
        safe = request.node.nodeid.replace("::", "__").replace("/", "_").replace("\\", "_")
        browser.save_screenshot(str(ARTIFACTS / f"FAILED_{safe}.png"))

    browser.quit()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    setattr(item, "rep_" + call.when, outcome.get_result())
