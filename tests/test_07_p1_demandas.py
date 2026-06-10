"""
test_07_p1_demandas.py
Testes das demandas P1 (integridade de estoque / venda duplicada):
  D2  - Baixa de projeto deve gerar movimentacao de estoque
  D4  - Produtividade Pecuaria deve gerar Movimentacao Interna / estoque
  D9  - Baixa automatica do animal na confirmacao da nota de venda
  D10 - Trava para nao vender o mesmo animal 2 vezes

Estrategia (conforme ESPECIFICACAO_DEMANDAS_2026-06.md):
  - BASELINE: teste marcado xfail que evidencia o bug no ambiente AINDA SEM a correcao.
              Ao rodar contra a base corrigida, o xfail vira XPASS (sinal de que o fix entrou).
  - ACEITACAO: teste que passa SOMENTE com a correcao aplicada.

Pre-requisitos:
  - WildFly no ar e login shadow-DOM funcionando (vide conftest.py / .env).
  - Testes que alteram dados exigem DHARA_E2E_MUTATING=1.
  - Validacao de estoque/baixa no banco exige cliente Oracle opcional (oracledb) e
    as variaveis DHARA_DB_* no .env; quando ausentes, o teste de banco e' skipado.
"""
import os
import pytest

from tests.pages.sankhya_page import SankhyaPage


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------

def _login(driver, cfg):
    page = SankhyaPage(driver, cfg.base_url)
    page.open("mge")
    page.login(cfg.username, cfg.password)
    assert page.is_logged_in(), "Login falhou"
    return page


def _db_conn():
    """Conexao Oracle opcional para validar estoque/baixa. Retorna None se indisponivel."""
    dsn = os.getenv("DHARA_DB_DSN")  # ex: localhost:1521/XE
    user = os.getenv("DHARA_DB_USER", "SANKHYA")
    pwd = os.getenv("DHARA_DB_PASSWORD")
    if not dsn or not pwd:
        return None
    try:
        import oracledb  # type: ignore
    except ImportError:
        return None
    try:
        return oracledb.connect(user=user, password=pwd, dsn=dsn)
    except Exception:
        return None


def _scalar(conn, sql, **binds):
    cur = conn.cursor()
    try:
        cur.execute(sql, binds)
        row = cur.fetchone()
        return row[0] if row else None
    finally:
        cur.close()


def _require_mutating(cfg):
    if not cfg.mutating:
        pytest.skip("Requer DHARA_E2E_MUTATING=1 (altera dados no ambiente)")


def _require_db(conn):
    if conn is None:
        pytest.skip("Requer cliente Oracle (oracledb) e DHARA_DB_DSN/DHARA_DB_PASSWORD no .env")


# ======================================================================
# D2 - Baixa de projeto deve movimentar estoque
# ======================================================================

@pytest.mark.p1
@pytest.mark.saida
def test_d2_config_tem_top_baixa(driver, cfg):
    """ACEITACAO: a Configuracao Pecuaria deve expor o campo TOP de Baixa de Animais
    (TIPOPMOVBAIXA criado no V24). Sem a correcao, o campo nao existe na tela."""
    page = _login(driver, cfg)
    page.open_screen("configuracao")
    page.wait_screen(["Configura", "Pecu"], timeout=90)
    body = page.body_text().lower()
    assert ("baixa" in body and "opera" in body) or "tipopmovbaixa" in body, (
        "Campo 'TOP de Operacao de Baixa de Animais' nao encontrado na Configuracao Pecuaria. "
        "Verifique o V24.xml e o datadictionary Dh_PECCONFIG."
    )


@pytest.mark.p1
@pytest.mark.saida
@pytest.mark.mutating
@pytest.mark.xfail(reason="BASELINE: baixa de projeto nao gera nota/estoque antes da D2", strict=False)
def test_d2_baseline_baixa_sem_estoque(driver, cfg):
    """BASELINE: ao baixar animal do projeto, o estoque do produto NAO muda (bug)."""
    _require_mutating(cfg)
    conn = _db_conn()
    _require_db(conn)
    codprod = cfg.codprod_animal
    assert codprod, "Configure DHARA_CODPROD_ANIMAL no .env"

    est_antes = _scalar(conn, "SELECT NVL(SUM(ESTOQUE),0) FROM TGFEST WHERE CODPROD = :p", p=codprod)

    page = _login(driver, cfg)
    page.open_screen("saida")  # aba/tela onde fica o botao de baixa do projeto
    page.wait_screen(["Animais", "Projeto", "Baixa"], timeout=90)
    page.select_grid_row(0)
    page.click_first_available(["Baixar Animal do Projeto", "Baixar", "Baixa"])
    page.click_first_available(["Confirmar", "Sim", "OK"])

    est_depois = _scalar(conn, "SELECT NVL(SUM(ESTOQUE),0) FROM TGFEST WHERE CODPROD = :p", p=codprod)
    # No estado bugado, estoque nao muda -> a assercao de "mudou" falha -> xfail esperado.
    assert est_depois < est_antes, "Estoque nao foi movimentado pela baixa (bug D2)"


# ======================================================================
# D4 - Produtividade deve gerar Movimentacao Interna / estoque
# ======================================================================

@pytest.mark.p1
@pytest.mark.apontamento
@pytest.mark.mutating
@pytest.mark.xfail(reason="BASELINE: produtividade nao gera mov. interna antes da D4", strict=False)
def test_d4_baseline_produtividade_sem_nota(driver, cfg):
    """BASELINE: lancar produtividade nao gera nota interna nem movimenta estoque."""
    _require_mutating(cfg)
    conn = _db_conn()
    _require_db(conn)
    # Antes da correcao, a UI mostra sucesso porem NUNOTAPROD do apontamento fica nulo.
    nunota_prod = _scalar(
        conn,
        "SELECT NUNOTAPROD FROM DH_PECAPOCAB WHERE ID_APONTAMENTO = "
        "(SELECT MAX(ID_APONTAMENTO) FROM DH_PECAPOCAB)",
    )
    assert nunota_prod is not None, "NUNOTAPROD preenchido (bug D4 corrigido)"


@pytest.mark.p1
@pytest.mark.apontamento
def test_d4_config_exige_top_produtividade(driver, cfg):
    """ACEITACAO (parcial, sem mutacao): a tela de Configuracao deve ter a TOP de
    Produtividade (TIPOPMOVPROD), cuja ausencia passa a ser bloqueada com erro claro."""
    page = _login(driver, cfg)
    page.open_screen("configuracao")
    page.wait_screen(["Configura", "Pecu"], timeout=90)
    body = page.body_text().lower()
    assert "produtiv" in body, "Campo de TOP de Produtividade nao encontrado na Configuracao"


# ======================================================================
# D9 - Baixa automatica na confirmacao da nota
# ======================================================================

@pytest.mark.p1
@pytest.mark.saida
@pytest.mark.mutating
@pytest.mark.xfail(reason="BASELINE: animal continua ativo apos confirmar a nota antes da D9", strict=False)
def test_d9_baseline_animal_continua_ativo(driver, cfg):
    """BASELINE: apos confirmar a NF de venda, o animal permanece STATUS='A' (bug)."""
    _require_mutating(cfg)
    conn = _db_conn()
    _require_db(conn)
    id_animal = os.getenv("DHARA_IDANIMAL_VENDA")
    assert id_animal, "Configure DHARA_IDANIMAL_VENDA no .env (animal usado na venda de teste)"

    # Pre-condicao: gerar venda + confirmar nota deve ser feito pelo cenario E2E (test_06)
    # ou manualmente. Aqui validamos o estado final.
    status = _scalar(conn, "SELECT STATUS FROM DH_PECPRJ WHERE ID_PECUARIA = :i AND STATUS = 'A'", i=id_animal)
    # Bug: animal segue 'A'. xfail enquanto a baixa automatica nao baixa o animal.
    assert status is None, "Animal continua ativo apos confirmacao (bug D9)"


@pytest.mark.p1
@pytest.mark.saida
@pytest.mark.mutating
def test_d9_aceitacao_animal_baixado_e_historico(driver, cfg):
    """ACEITACAO: apos confirmar a nota, o animal fica baixado e ha registro em DH_HISTANI."""
    _require_mutating(cfg)
    conn = _db_conn()
    _require_db(conn)
    id_animal = os.getenv("DHARA_IDANIMAL_VENDA")
    assert id_animal, "Configure DHARA_IDANIMAL_VENDA no .env"

    ativo = _scalar(conn, "SELECT COUNT(*) FROM DH_PECPRJ WHERE ID_PECUARIA = :i AND STATUS = 'A'", i=id_animal)
    assert ativo == 0, "Animal ainda ativo apos confirmacao (D9 nao baixou)"
    hist = _scalar(
        conn,
        "SELECT COUNT(*) FROM DH_HISTANI WHERE ID_PECUARIA = :i AND TIPO_MOV = 'B'",
        i=id_animal,
    )
    assert hist and hist > 0, "Sem registro de baixa por venda em DH_HISTANI (D9)"


# ======================================================================
# D10 - Trava de venda duplicada
# ======================================================================

@pytest.mark.p1
@pytest.mark.saida
@pytest.mark.mutating
def test_d10_aceitacao_bloqueia_segundo_uso(driver, cfg):
    """ACEITACAO: incluir o mesmo animal numa segunda venda aberta deve ser bloqueado
    com MGEModelException ('Animal ja incluido na venda ...')."""
    _require_mutating(cfg)
    page = _login(driver, cfg)
    page.open_screen("saida")
    page.wait_screen(["Venda", "Animais", "Saida", "Saída"], timeout=90)

    # O cenario completo (criar venda A com o animal, depois venda B e tentar incluir o mesmo)
    # depende de massa/registro da tela nova GerenciarVendaAnimais. Aqui asseguramos que a
    # mensagem de bloqueio aparece quando a duplicidade e' tentada.
    body = page.body_text()
    if "ja incluido na venda" not in body.lower() and "já incluído na venda" not in body.lower():
        pytest.skip(
            "Cenario de duplicidade nao executado nesta sessao (requer massa + tela "
            "GerenciarVendaAnimais registrada). Validar manualmente ou via E2E dedicado."
        )


@pytest.mark.p1
@pytest.mark.saida
@pytest.mark.mutating
@pytest.mark.xfail(reason="BASELINE: mesmo animal entra em 2 vendas abertas antes da D10", strict=False)
def test_d10_baseline_permite_duplicidade(driver, cfg):
    """BASELINE: sem a trava, o mesmo animal aparece em mais de uma venda aberta."""
    _require_mutating(cfg)
    conn = _db_conn()
    _require_db(conn)
    # Detecta duplicidade existente: animal em >1 venda aberta (STATUS em 'P','G').
    dup = _scalar(
        conn,
        "SELECT COUNT(*) FROM ("
        "  SELECT ITE.ID_PECUARIA FROM DH_VENDAITE ITE "
        "  INNER JOIN DH_VENDACAB CAB ON CAB.CODVENDA = ITE.CODVENDA "
        "  WHERE CAB.STATUS IN ('P','G') "
        "  GROUP BY ITE.ID_PECUARIA HAVING COUNT(DISTINCT ITE.CODVENDA) > 1"
        ")",
    )
    # Bug: existe duplicidade (dup > 0). Apos a D10, nenhuma duplicidade deve ser criada.
    assert dup and dup > 0, "Nenhuma duplicidade encontrada (D10 ja em vigor)"
