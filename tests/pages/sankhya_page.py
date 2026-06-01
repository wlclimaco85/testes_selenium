"""
SankhyaPage — Page Object para o Sankhya Om 4.35b185.

PARTICULARIDADES:
- Login: web component <sankhya-login> com Shadow DOM — 2 etapas.
- Patch sf.js: system.jsp deve ter sf.js antes de snk.js para o workspace renderizar.
- Esperas: GWT + AngularJS nao escreve texto em body.text — usar innerHTML.
"""
from __future__ import annotations

import re
import time
from pathlib import Path

from selenium.common.exceptions import TimeoutException
from selenium.webdriver import Chrome, Edge
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

Driver = Chrome | Edge

# Mapa completo das telas do addon Dhara Pecuaria
DHARA_SCREENS = {
    "configuracao":  "pecuaria.configuracao",
    "faixa_etaria":  "pecuaria.faixa",
    "raca":          "pecuaria.raca",
    "tipo_exame":    "pecuaria.tipexame",
    "historico":     "pecuaria.historico",
    "entrada":       "pecuaria.entrada",
    "iatf":          "pecuaria.iatf",
    "diagnostico":   "pecuaria.diag",
    "parto":         "pecuaria.parto",
    "apontamento":   "pecuaria.apontamento",
    "saida":         "pecuaria.saida",
}


class SankhyaPage:
    def __init__(self, driver: Driver, base_url: str, timeout: int = 20) -> None:
        self.driver = driver
        self.base_url = base_url.rstrip("/")
        self.wait = WebDriverWait(driver, timeout)

    # ------------------------------------------------------------------
    # Navegacao
    # ------------------------------------------------------------------

    def open(self, path: str) -> None:
        url = path if path.startswith("http") else f"{self.base_url}/{path.lstrip('/')}"
        self.driver.get(url)
        self._wait_ready()

    def open_screen(self, screen_key: str) -> None:
        """Abre uma tela DH_ pelo nome amigavel (ex: 'faixa_etaria')."""
        menu_id = DHARA_SCREENS.get(screen_key, screen_key)
        self.driver.get(f"{self.base_url}/mge/system.jsp#app/{menu_id}")

    def _wait_ready(self) -> None:
        self.wait.until(lambda d: d.execute_script("return document.readyState") == "complete")

    # ------------------------------------------------------------------
    # Login — shadow DOM obrigatorio (Sankhya Om 4.35)
    # ------------------------------------------------------------------

    def login(self, username: str, password: str) -> None:
        if not username:
            return

        # Aguardar web component aparecer
        host = None
        for _ in range(20):
            hosts = self.driver.find_elements(By.CSS_SELECTOR, "sankhya-login")
            if hosts:
                host = hosts[0]
                break
            time.sleep(0.5)

        if host is None:
            return  # ja logado ou pagina diferente

        def _vsubmit(root):
            for b in root.find_elements(By.CSS_SELECTOR, "button"):
                try:
                    if b.is_displayed() and (b.text or "").strip().lower() in {"prosseguir", "entrar", "acessar"}:
                        return b
                except Exception:
                    pass
            return None

        # Etapa 1: usuario
        user_el = None
        for _ in range(20):
            try:
                root = self.driver.find_element(By.CSS_SELECTOR, "sankhya-login").shadow_root
                c = root.find_element(By.CSS_SELECTOR, "#user, input[name='user']")
                if c.is_displayed():
                    user_el = c
                    break
            except Exception:
                pass
            time.sleep(0.5)

        if user_el is None:
            return

        user_el.send_keys(username)
        root = self.driver.find_element(By.CSS_SELECTOR, "sankhya-login").shadow_root
        btn = _vsubmit(root)
        if btn:
            btn.click()

        # Etapa 2: senha
        pwd_el = None
        for _ in range(20):
            try:
                root = self.driver.find_element(By.CSS_SELECTOR, "sankhya-login").shadow_root
                c = root.find_element(By.CSS_SELECTOR, "input[type='password']")
                if c.is_displayed():
                    pwd_el = c
                    break
            except Exception:
                pass
            time.sleep(0.5)

        if pwd_el is not None:
            if password:
                pwd_el.send_keys(password)
            root = self.driver.find_element(By.CSS_SELECTOR, "sankhya-login").shadow_root
            btn = _vsubmit(root)
            if btn:
                btn.click()

        # Aguardar component sumir (login concluido)
        for _ in range(40):
            if not self.driver.find_elements(By.CSS_SELECTOR, "sankhya-login"):
                break
            time.sleep(0.5)

        self._wait_ready()

    def is_logged_in(self) -> bool:
        return not bool(self.driver.find_elements(By.CSS_SELECTOR, "sankhya-login"))

    # ------------------------------------------------------------------
    # Esperas especificas do GWT + AngularJS
    # ------------------------------------------------------------------

    def wait_screen(self, keywords: list[str], timeout: int = 90) -> None:
        """Aguarda tela DH_ carregar (usa innerHTML porque GWT nao escreve em body.text)."""
        pattern = "|".join(re.escape(k) for k in keywords)

        def _check(d):
            for fn in [
                lambda: d.find_element(By.TAG_NAME, "body").text,
                lambda: d.execute_script("return document.body.innerText || ''"),
                lambda: d.execute_script("return document.body.innerHTML || ''"),
            ]:
                try:
                    if re.search(pattern, fn(), re.IGNORECASE):
                        return True
                except Exception:
                    pass
            return False

        WebDriverWait(self.driver, timeout).until(_check)

    def wait_any_text(self, texts: list[str], timeout: int = 30) -> None:
        self.wait_screen(texts, timeout)

    # ------------------------------------------------------------------
    # Interacoes basicas
    # ------------------------------------------------------------------

    def click_text(self, label: str) -> None:
        xpath = (
            f"//*[self::button or self::a or @role='button' or contains(@class,'btn')]"
            f"[contains(normalize-space(.), '{label}')]"
        )
        el = WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.XPATH, xpath)))
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'})", el)
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(el)).click()

    def click_first_available(self, labels: list[str]) -> str:
        last: Exception | None = None
        for label in labels:
            try:
                self.click_text(label)
                return label
            except Exception as e:
                last = e
        raise AssertionError(f"Nenhum botao encontrado: {labels}") from last

    def fill_field(self, label: str, value: str) -> None:
        f = self._first_visible([
            (By.XPATH, f"//*[contains(normalize-space(.),'{label}')]/following::input[1]"),
            (By.NAME, label),
            (By.CSS_SELECTOR, f"input[ng-model*='{label.lower()}']"),
        ], timeout=10)
        if not f:
            raise AssertionError(f"Campo nao encontrado: {label}")
        f.clear()
        f.send_keys(value)
        f.send_keys(Keys.TAB)

    def select_grid_row(self, row_index: int = 0) -> None:
        rows = WebDriverWait(self.driver, 15).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".ui-grid-row, tr[role='row'], tbody tr"))
        )
        if rows:
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'})", rows[row_index])
            rows[row_index].click()

    def assert_button(self, label: str) -> None:
        xpath = (
            f"//*[self::button or self::a or @role='button' or contains(@class,'btn')]"
            f"[contains(normalize-space(.), '{label}')]"
        )
        WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.XPATH, xpath)))

    def save_screenshot(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        self.driver.save_screenshot(str(path))

    def body_text(self) -> str:
        try:
            return self.driver.find_element(By.TAG_NAME, "body").text
        except Exception:
            return ""

    # ------------------------------------------------------------------
    # Helpers internos
    # ------------------------------------------------------------------

    def _first_visible(self, locators, timeout: int = 8):
        for by, sel in locators:
            try:
                return WebDriverWait(self.driver, timeout).until(
                    EC.visibility_of_element_located((by, sel))
                )
            except TimeoutException:
                continue
        return None
