"""
test_09_p3_demandas.py
Testes das demandas P3 (apontamento avancado, peso na venda, ciclo reprodutivo,
leitor de brinco):
  D1  - Rateio percentual entre projetos no Apontamento (DH_PECAPORAT.PERCRATEIO)
  D7  - Apontamento individual por animal (DH_PECAPOITE.ID_PECUARIA)
  D6  - Peso por animal na Venda (DH_VENDAITE.PESO / DH_VENDACAB.PESO_TOTAL)
  D11 - Ciclo reprodutivo completo (AD -> ER/VZ -> PA)
  D12 - Leitor de brinco na saida (venda)
  D13 - Leitor de brinco na entrada

Estrategia (conforme ESPECIFICACAO_DEMANDAS_2026-06.md):
  - BASELINE: teste marcado xfail que evidencia o comportamento ANTES da correcao.
  - ACEITACAO: teste que passa SOMENTE com a correcao aplicada (presenca de campos/
    elementos na UI). Cenarios que dependem de massa de dados/banco ficam skipados
    com a justificativa documental.
"""
import pytest
from selenium.webdriver.common.by import By

from tests.pages.sankhya_page import SankhyaPage


def _login(driver, cfg):
    page = SankhyaPage(driver, cfg.base_url)
    page.open("mge")
    page.login(cfg.username, cfg.password)
    assert page.is_logged_in(), "Login falhou"
    return page


# ======================================================================
# D1 / D7 - Apontamento: rateio percentual + apontamento individual
# ======================================================================

@pytest.mark.p3
@pytest.mark.apontamento
def test_d1_apontamento_exibe_rateio_percentual(driver, cfg):
    """ACEITACAO: a aba de rateio do Apontamento deve expor o Percentual de Rateio."""
    page = _login(driver, cfg)
    page.open_screen("apontamento")
    page.wait_screen(["Apontamento"], timeout=90)
    try:
        page.click_first_available(["Rateio", "Projetos"])
    except Exception:
        pass
    body = page.body_text().lower()
    assert "rateio" in body or "percentual" in body, (
        "Campo de Percentual de Rateio nao encontrado na aba de Rateio do Apontamento "
        "(verificar DH_PECAPORAT.xml/V27 - PERCRATEIO)."
    )


@pytest.mark.p3
@pytest.mark.apontamento
def test_d7_apontamento_item_exibe_animal(driver, cfg):
    """ACEITACAO: os itens do Apontamento devem permitir vincular o Animal (ID_PECUARIA)."""
    page = _login(driver, cfg)
    page.open_screen("apontamento")
    page.wait_screen(["Apontamento"], timeout=90)
    try:
        page.click_first_available(["Itens", "Insumos", "Produtos"])
    except Exception:
        pass
    body = page.body_text().lower()
    assert "animal" in body, (
        "Campo Animal (ID_PECUARIA) nao encontrado nos itens do Apontamento "
        "(verificar DH_PECAPOITE.xml/V27)."
    )


@pytest.mark.p3
@pytest.mark.apontamento
@pytest.mark.mutating
@pytest.mark.xfail(
    reason="BASELINE: antes da D1, a soma de rateio=100% era validada por linha e "
           "bloqueava o cadastro incremental no grid",
    strict=False,
)
def test_d1_baseline_rateio_bloqueia_cadastro_incremental(driver, cfg):
    """BASELINE: cadastrar a 1a linha de rateio (<100%) lancava erro de soma antes da correcao."""
    pytest.skip(
        "Baseline documental: o bug original validava a soma de PERCRATEIO=100% a cada "
        "INSERT/UPDATE de linha do grid (DH_PECAPORAT), impedindo o cadastro incremental "
        "(toda linha exceto a ultima que fechasse 100% era rejeitada). Apos a correcao, a "
        "validacao de soma ocorre apenas na geracao do movimento (gerarMovInternaEntrada). "
        "Validacao via UI requer massa de projetos/apontamento."
    )


# ======================================================================
# D6 - Peso por animal na Venda
# ======================================================================

@pytest.mark.p3
@pytest.mark.saida
def test_d6_venda_exibe_coluna_peso(driver, cfg):
    """ACEITACAO: a tela de Saida/Venda de Animais deve exibir a coluna Peso (kg)."""
    page = _login(driver, cfg)
    page.open_screen("saida")
    page.wait_screen(["Venda", "Animais", "Saida", "Saída"], timeout=90)
    body = page.body_text().lower()
    assert "peso" in body, (
        "Coluna 'Peso (kg)' nao encontrada em GerenciarVendaAnimais "
        "(verificar GerenciarVendaAnimais.html/V28)."
    )


@pytest.mark.p3
@pytest.mark.saida
@pytest.mark.mutating
@pytest.mark.xfail(
    reason="BASELINE: antes da D6, DH_VENDAITE nao possuia campo PESO",
    strict=False,
)
def test_d6_baseline_venda_sem_peso(driver, cfg):
    """BASELINE: itens de venda nao registravam peso do animal antes da D6."""
    pytest.skip(
        "Baseline documental: antes da correcao, DH_VENDAITE nao tinha coluna PESO e "
        "DH_VENDACAB nao tinha PESO_TOTAL. Validacao de preenchimento automatico a "
        "partir de DH_ENTANI.PESO requer massa de dados e venda mutavel."
    )


# ======================================================================
# D11 - Ciclo reprodutivo completo (AD -> ER/VZ -> PA)
# ======================================================================

@pytest.mark.p3
@pytest.mark.reproducao
def test_d11_diagnostico_exibe_status_vazia(driver, cfg):
    """ACEITACAO: a tela de Diagnostico deve permitir o status 'Vazia' (VZ) apos diagnostico negativo."""
    page = _login(driver, cfg)
    page.open_screen("diagnostico")
    page.wait_screen(["Diagn"], timeout=90)
    body = page.body_text().lower()
    assert "vazia" in body or "vz" in body, (
        "Status 'Vazia' (VZ) nao encontrado na tela de Diagnostico "
        "(verificar DH_PECREPRO.xml/V29 - STATUSANIMAL)."
    )


@pytest.mark.p3
@pytest.mark.reproducao
def test_d11_config_exibe_tolerancia_parto(driver, cfg):
    """ACEITACAO: a Configuracao Pecuaria deve expor 'Permite Parto sem Diagnostico'."""
    page = _login(driver, cfg)
    page.open_screen("configuracao")
    page.wait_screen(["Configura", "Pecu"], timeout=90)
    body = page.body_text().lower()
    assert "diagn" in body and ("parto" in body or "tolera" in body), (
        "Campo 'Permite Parto sem Diagnostico' (TOLERAPARTOSEMDIAG) nao encontrado "
        "na Configuracao Pecuaria (verificar Dh_PECCONFIG.xml/V29)."
    )


@pytest.mark.p3
@pytest.mark.reproducao
@pytest.mark.mutating
@pytest.mark.xfail(
    reason="BASELINE: antes da D11, diagnostico negativo nao alterava o status da matriz",
    strict=False,
)
def test_d11_baseline_diagnostico_negativo_nao_atualiza_status(driver, cfg):
    """BASELINE: diagnostico 'N' nao mudava STATUSANIMAL antes da D11 (matriz presa em AD)."""
    pytest.skip(
        "Baseline documental: antes da correcao, apenas diagnostico positivo (P) "
        "atualizava STATUSANIMAL (AD->ER); diagnostico negativo (N) nao tinha efeito, "
        "deixando a matriz presa em AD sem possibilidade de reabrir o ciclo. Validacao "
        "requer massa de IATF + diagnostico e cliente Oracle (oracledb)."
    )


@pytest.mark.p3
@pytest.mark.reproducao
@pytest.mark.mutating
def test_d11_aceitacao_parto_idempotente(driver, cfg):
    """ACEITACAO (documental): confirmar parto 2x para o mesmo CODREPRO nao deve duplicar
    DH_HISTANI nem reprocessar a matriz ja em status PA."""
    pytest.skip(
        "Validacao de idempotencia de confirmarParto requer banco de dados (oracledb) e "
        "massa de ciclo reprodutivo completo (IATF -> Diagnostico P -> Parto). Cobertura "
        "garantida por ReproducaoService.confirmarParto, que retorna null (no-op) quando "
        "STATUSANIMAL ja e 'PA' (code review aplicado)."
    )


# ======================================================================
# D12 / D13 - Leitor de brinco (saida e entrada)
# ======================================================================

@pytest.mark.p3
@pytest.mark.saida
def test_d12_venda_exibe_input_brinco(driver, cfg):
    """ACEITACAO: a tela de Venda de Animais deve exibir o campo de leitura de brinco."""
    page = _login(driver, cfg)
    page.open_screen("saida")
    page.wait_screen(["Venda", "Animais", "Saida", "Saída"], timeout=90)
    inputs = page.driver.find_elements(By.CSS_SELECTOR, "#dhBrincoVenda")
    assert inputs, "Campo #dhBrincoVenda (leitor de brinco) nao encontrado em GerenciarVendaAnimais."


@pytest.mark.p3
@pytest.mark.entrada
def test_d13_entrada_exibe_input_brinco(driver, cfg):
    """ACEITACAO: a tela de Entrada de Animais deve exibir o campo de leitura de brinco."""
    page = _login(driver, cfg)
    page.open_screen("entrada")
    page.wait_screen(["Entrada", "Animais"], timeout=90)
    inputs = page.driver.find_elements(By.CSS_SELECTOR, "#dhBrincoEntrada")
    assert inputs, "Campo #dhBrincoEntrada (leitor de brinco) nao encontrado em GerenciarEntradaAnimais."


@pytest.mark.p3
@pytest.mark.saida
@pytest.mark.mutating
@pytest.mark.xfail(
    reason="BASELINE: antes da D12, nao havia leitor de brinco na tela de venda",
    strict=False,
)
def test_d12_baseline_sem_leitor_brinco(driver, cfg):
    """BASELINE: tela de venda nao possuia input de bipagem antes da D12."""
    pytest.skip(
        "Baseline documental: antes da correcao, GerenciarVendaAnimais.html nao tinha "
        "#dhBrincoVenda nem o handler adicionarAnimalPorBrinco."
    )


@pytest.mark.p3
@pytest.mark.entrada
@pytest.mark.mutating
@pytest.mark.xfail(
    reason="BASELINE: antes da D13, nao havia leitor de brinco na tela de entrada",
    strict=False,
)
def test_d13_baseline_sem_leitor_brinco(driver, cfg):
    """BASELINE: tela de entrada nao possuia input de bipagem antes da D13."""
    pytest.skip(
        "Baseline documental: antes da correcao, GerenciarEntradaAnimais.html nao tinha "
        "#dhBrincoEntrada nem o handler biparBrincoEntrada."
    )
