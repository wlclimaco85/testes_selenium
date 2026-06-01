"""
test_06_fluxo_completo.py
Fluxo ponta a ponta: Entrada → Projeto → IATF → Diagnostico → Parto → Apontamento → Saida.
Requer DHARA_E2E_MUTATING=1 e dados configurados no .env.
"""
import pytest
from tests.pages.sankhya_page import SankhyaPage


def _login(driver, cfg):
    page = SankhyaPage(driver, cfg.base_url)
    page.open("mge")
    page.login(cfg.username, cfg.password)
    assert page.is_logged_in(), "Login falhou"
    return page


@pytest.mark.mutating
def test_fluxo_completo_skip_sem_mutating(driver, cfg):
    """Garante que o fluxo completo e pulado sem MUTATING=1."""
    if not cfg.mutating:
        pytest.skip("DHARA_E2E_MUTATING=0 — fluxo completo requer ambiente configurado")

    if not all([cfg.codprod_animal, cfg.codparc]):
        pytest.skip("DHARA_CODPROD_ANIMAL e DHARA_CODPARC sao obrigatorios para o fluxo completo")

    page = _login(driver, cfg)

    # Etapa 1: Abrir Entrada de Animais
    page.open_screen("entrada")
    page.wait_screen(["Entrada", "Animal"], timeout=90)

    # Etapa 2: Verificar acoes disponiveis
    page.open_screen("historico")
    page.wait_screen(["Histórico", "Historico"], timeout=90)

    # Etapa 3: IATF
    page.open_screen("iatf")
    page.wait_screen(["IATF", "Monta"], timeout=90)

    # Etapa 4: Diagnostico
    page.open_screen("diagnostico")
    page.wait_screen(["Diagnóstico", "Diagnostico"], timeout=90)

    # Etapa 5: Parto
    page.open_screen("parto")
    page.wait_screen(["Parto", "Nascimento"], timeout=90)

    # Etapa 6: Apontamento
    page.open_screen("apontamento")
    page.wait_screen(["Apontamento"], timeout=90)

    # Etapa 7: Saida
    page.open_screen("saida")
    page.wait_screen(["Saída", "Saida", "Animal"], timeout=90)

    # Screenshot final do fluxo
    page.save_screenshot(page.__class__.__module__.split(".")[0])
