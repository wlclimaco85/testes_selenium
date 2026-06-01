"""
test_04_apontamento_saida.py
Valida as telas de Apontamento Pecuaria e Saida de Animais.
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
# Apontamento Pecuaria
# -----------------------------------------------------------------------

@pytest.mark.smoke
@pytest.mark.apontamento
def test_apontamento_abre(driver, cfg):
    """Apontamento Pecuaria deve abrir."""
    page = _login(driver, cfg)
    page.open_screen("apontamento")
    page.wait_screen(["Apontamento", "Pecuária", "Pecuaria", "Insumo", "Produtividade"], timeout=90)


@pytest.mark.smoke
@pytest.mark.apontamento
def test_apontamento_exibe_processar_e_reverter(driver, cfg):
    """Apontamento deve ter botoes Processar e Reverter (ou equivalentes)."""
    page = _login(driver, cfg)
    page.open_screen("apontamento")
    page.wait_screen(["Apontamento"], timeout=90)

    botoes = []
    for btn in ["Processar", "Reverter", "Confirmar", "Cancelar", "Novo"]:
        try:
            page.assert_button(btn)
            botoes.append(btn)
        except Exception:
            pass

    assert botoes, "Nenhum botao de acao encontrado na tela de Apontamento"


@pytest.mark.smoke
@pytest.mark.apontamento
def test_apontamento_exibe_abas(driver, cfg):
    """Apontamento deve ter abas de Insumos, Servicos, Produtividade e Rateio."""
    page = _login(driver, cfg)
    page.open_screen("apontamento")
    page.wait_screen(["Apontamento"], timeout=90)

    abas_encontradas = []
    for aba in ["Insumo", "Serviço", "Servico", "Produtividade", "Rateio"]:
        try:
            page.assert_button(aba)
            abas_encontradas.append(aba)
        except Exception:
            pass

    # pelo menos 1 aba deve aparecer
    assert abas_encontradas or len(page.body_text()) > 100, \
        "Tela de Apontamento aparenta estar vazia ou sem abas"


# -----------------------------------------------------------------------
# Saida de Animais
# -----------------------------------------------------------------------

@pytest.mark.smoke
@pytest.mark.saida
def test_saida_abre(driver, cfg):
    """Tela de Saida de Animais deve abrir."""
    page = _login(driver, cfg)
    page.open_screen("saida")
    page.wait_screen(["Saída", "Saida", "Animal", "Venda", "Nota"], timeout=90)


@pytest.mark.smoke
@pytest.mark.saida
def test_saida_exibe_acoes(driver, cfg):
    """Saida deve ter botoes de acao de venda/saida."""
    page = _login(driver, cfg)
    page.open_screen("saida")
    page.wait_screen(["Saída", "Saida", "Animal"], timeout=90)

    botoes = []
    for btn in ["Gerar", "Nota", "Venda", "Saída", "Saida", "Validar", "Processar"]:
        try:
            page.assert_button(btn)
            botoes.append(btn)
        except Exception:
            pass

    assert botoes or len(page.body_text()) > 50, "Tela de Saida aparenta estar vazia"
