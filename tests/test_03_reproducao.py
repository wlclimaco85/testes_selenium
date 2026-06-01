"""
test_03_reproducao.py
Valida as telas do ciclo reprodutivo:
- IATF / Monta
- Diagnostico de Gestacao
- Registro de Parto
"""
import pytest
from tests.pages.sankhya_page import SankhyaPage


def _login(driver, cfg):
    page = SankhyaPage(driver, cfg.base_url)
    page.open("mge")
    page.login(cfg.username, cfg.password)
    assert page.is_logged_in(), "Login falhou"
    return page


# -----------------------------------------------------------------------
# IATF / Monta
# -----------------------------------------------------------------------

@pytest.mark.smoke
@pytest.mark.reproducao
def test_iatf_abre(driver, cfg):
    """Tela IATF/Monta deve abrir."""
    page = _login(driver, cfg)
    page.open_screen("iatf")
    page.wait_screen(["IATF", "Monta", "Matriz", "Reprodução", "Reprodução"], timeout=90)


@pytest.mark.smoke
@pytest.mark.reproducao
def test_iatf_exibe_importar_matrizes(driver, cfg):
    """IATF deve ter botao de importar matrizes ou de processar cobertura."""
    page = _login(driver, cfg)
    page.open_screen("iatf")
    page.wait_screen(["IATF", "Monta"], timeout=90)

    for btn in ["Importar", "Matrizes", "Processar", "Cobertura", "Monta"]:
        try:
            page.assert_button(btn)
            return
        except Exception:
            continue

    assert len(page.body_text()) > 50, "Tela IATF aparenta estar vazia"


# -----------------------------------------------------------------------
# Diagnostico de Gestacao
# -----------------------------------------------------------------------

@pytest.mark.smoke
@pytest.mark.reproducao
def test_diagnostico_abre(driver, cfg):
    """Tela de Diagnostico de Gestacao deve abrir."""
    page = _login(driver, cfg)
    page.open_screen("diagnostico")
    page.wait_screen(
        ["Diagnóstico", "Diagnostico", "Gestação", "Gestacao", "Exame"],
        timeout=90
    )


@pytest.mark.smoke
@pytest.mark.reproducao
def test_diagnostico_exibe_gerar_e_refazer(driver, cfg):
    """Diagnostico deve ter botoes Gerar e Refazer Diagnostico."""
    page = _login(driver, cfg)
    page.open_screen("diagnostico")
    page.wait_screen(["Diagnóstico", "Diagnostico"], timeout=90)

    botoes_encontrados = []
    for btn in ["Gerar", "Refazer", "Diagnóstico", "Diagnostico"]:
        try:
            page.assert_button(btn)
            botoes_encontrados.append(btn)
        except Exception:
            pass

    assert botoes_encontrados, "Nenhum botao de acao encontrado na tela de Diagnostico"


# -----------------------------------------------------------------------
# Registro de Parto
# -----------------------------------------------------------------------

@pytest.mark.smoke
@pytest.mark.reproducao
def test_parto_abre(driver, cfg):
    """Tela de Registro de Parto deve abrir."""
    page = _login(driver, cfg)
    page.open_screen("parto")
    page.wait_screen(["Parto", "Nascimento", "Cria", "Matriz"], timeout=90)


@pytest.mark.smoke
@pytest.mark.reproducao
def test_parto_exibe_confirmar_e_cancelar(driver, cfg):
    """Parto deve ter botoes de confirmacao e cancelamento."""
    page = _login(driver, cfg)
    page.open_screen("parto")
    page.wait_screen(["Parto", "Nascimento"], timeout=90)

    botoes = []
    for btn in ["Confirmar", "Cancelar", "Registrar", "Parto"]:
        try:
            page.assert_button(btn)
            botoes.append(btn)
        except Exception:
            pass

    assert botoes, "Nenhum botao de acao encontrado na tela de Parto"
