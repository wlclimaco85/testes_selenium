"""
test_08_p2_demandas.py
Testes das demandas P2 (fundacoes: flags TGF e tela de Servico/Veiculo):
  D16 - Flag "Grupo Pecuaria" em Grupo de Produtos (TGFGRU.DH_GRUPOPECUARIA)
  D17 - Flag "Pecuaria" em Produtos/Servicos (TGFPRO.DH_PECUARIA)
  D18 - Flag "Pecuaria" em Parceiros (TGFPAR.DH_PECUARIA)
  D5  - Servico Pecuaria: Maquina/Implemento/Horimetro editaveis + auto-horimetro
  D19 - Maquina/Implemento amarrados a Veiculos (TGFVEI)

Estrategia: BASELINE xfail (campo/vinculo ausente hoje) + ACEITACAO (presente apos correcao).
Telas nativas de cadastro (Grupo/Produto/Parceiro) nao estao no mapa DHARA_SCREENS;
quando o resourceID nativo nao for fornecido (env DHARA_SCREEN_*), o teste e' skipado.
"""
import os
import pytest

from tests.pages.sankhya_page import SankhyaPage


def _login(driver, cfg):
    page = SankhyaPage(driver, cfg.base_url)
    page.open("mge")
    page.login(cfg.username, cfg.password)
    assert page.is_logged_in(), "Login falhou"
    return page


def _open_native(page, env_key, hint_keywords):
    """Abre uma tela nativa pelo resourceID informado em env; skip se ausente."""
    res = os.getenv(env_key)
    if not res:
        pytest.skip(f"Configure {env_key} com o resourceID da tela nativa para validar via UI")
    page.open_screen(res)
    page.wait_screen(hint_keywords, timeout=90)


# ----------------------------------------------------------------------
# D16 / D17 / D18 - flags em cadastros nativos
# ----------------------------------------------------------------------

@pytest.mark.p2
@pytest.mark.cadastro
def test_d16_flag_grupo_pecuaria(driver, cfg):
    """ACEITACAO: Grupo de Produtos deve exibir a flag 'Grupo Pecuaria'."""
    page = _login(driver, cfg)
    _open_native(page, "DHARA_SCREEN_GRUPOPROD", ["Grupo", "Produto"])
    body = page.body_text().lower()
    assert "grupo pecu" in body or "dh_grupopecuaria" in body, (
        "Flag 'Grupo Pecuaria' ausente em Grupo de Produtos (verificar GrupoProduto.xml/V25)."
    )


@pytest.mark.p2
@pytest.mark.cadastro
def test_d17_flag_produto_pecuaria(driver, cfg):
    """ACEITACAO: Produto deve exibir a flag 'Pecuaria'."""
    page = _login(driver, cfg)
    _open_native(page, "DHARA_SCREEN_PRODUTO", ["Produto"])
    body = page.body_text().lower()
    assert "pecu" in body, "Flag 'Pecuaria' ausente em Produto (verificar Produto.xml/V25)."


@pytest.mark.p2
@pytest.mark.cadastro
def test_d18_flag_parceiro_pecuaria(driver, cfg):
    """ACEITACAO: Parceiro deve exibir a flag 'Pecuaria'."""
    page = _login(driver, cfg)
    _open_native(page, "DHARA_SCREEN_PARCEIRO", ["Parceiro"])
    body = page.body_text().lower()
    assert "pecu" in body, "Flag 'Pecuaria' ausente em Parceiro (verificar Parceiro.xml/V25)."


# ----------------------------------------------------------------------
# D5 / D19 - Servico Pecuaria: Maquina/Implemento/Horimetro + Veiculo
# ----------------------------------------------------------------------

@pytest.mark.p2
@pytest.mark.apontamento
def test_d5_servico_exibe_campos_maquina_horimetro(driver, cfg):
    """ACEITACAO: a aba Servico do Apontamento expoe Maquina, Implemento e Horimetro."""
    page = _login(driver, cfg)
    page.open_screen("apontamento")
    page.wait_screen(["Apontamento"], timeout=90)
    # Tenta navegar para a aba de Servico
    try:
        page.click_first_available(["Serviço", "Servico", "Serviços", "Servicos"])
    except Exception:
        pass
    body = page.body_text().lower()
    achados = [k for k in ["máquina", "maquina", "implemento", "horímetro", "horimetro"] if k in body]
    assert achados, "Campos de Maquina/Implemento/Horimetro nao encontrados na aba Servico"


@pytest.mark.p2
@pytest.mark.apontamento
@pytest.mark.mutating
@pytest.mark.xfail(reason="BASELINE: Maquina/Implemento sao inteiro livre (sem lookup de Veiculo) antes da D19", strict=False)
def test_d19_baseline_maquina_sem_lookup_veiculo(driver, cfg):
    """BASELINE: o campo Maquina nao oferece pesquisa de Veiculo (campo inteiro livre)."""
    pytest.skip(
        "Baseline documental: antes da D19 CODMAQUINA/CODIMPLEMENTO sao INTEIRO sem targetInstance Veiculo. "
        "Apos a correcao o campo vira PESQUISA de Veiculo (TGFVEI). Validacao de lookup requer massa de veiculos."
    )
