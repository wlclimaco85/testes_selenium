"""
test_01_cadastros_base.py
Valida abertura e estrutura das telas de cadastros base do addon:
- Configuração Pecuária
- Faixa Etária
- Raça de Animais
- Tipo de Exame

Testes smoke: abrem a tela e verificam elementos esperados.
Testes mutating (DHARA_E2E_MUTATING=1): criam e excluem registros de teste.
"""
import pytest
from tests.pages.sankhya_page import SankhyaPage


def _login(driver, cfg):
    page = SankhyaPage(driver, cfg.base_url)
    page.open("mge")
    page.login(cfg.username, cfg.password)
    assert page.is_logged_in(), "Login falhou"
    return page


@pytest.mark.smoke
@pytest.mark.cadastro
def test_configuracao_abre(driver, cfg):
    """Configuração Pecuária deve abrir o formulário de config."""
    page = _login(driver, cfg)
    page.open_screen("configuracao")
    page.wait_screen(["Configuração", "Configuracao", "Pecuária", "Empresa"], timeout=90)


@pytest.mark.smoke
@pytest.mark.cadastro
def test_faixa_etaria_abre(driver, cfg):
    """Faixa Etária deve exibir grid e botão Novo."""
    page = _login(driver, cfg)
    page.open_screen("faixa_etaria")
    page.wait_screen(["Faixa", "Etária", "Descrição"], timeout=90)
    page.assert_button("Novo")


@pytest.mark.smoke
@pytest.mark.cadastro
def test_raca_abre(driver, cfg):
    """Raça de Animais deve exibir grid e botão Novo."""
    page = _login(driver, cfg)
    page.open_screen("raca")
    page.wait_screen(["Raça", "Raca", "Descrição", "Animal"], timeout=90)
    page.assert_button("Novo")


@pytest.mark.smoke
@pytest.mark.cadastro
def test_tipo_exame_abre(driver, cfg):
    """Tipo de Exame deve exibir grid e botão Novo."""
    page = _login(driver, cfg)
    page.open_screen("tipo_exame")
    page.wait_screen(["Tipo", "Exame", "Descrição"], timeout=90)
    page.assert_button("Novo")


@pytest.mark.mutating
@pytest.mark.cadastro
def test_faixa_etaria_criar_excluir(driver, cfg):
    """Cria e exclui uma faixa etária de teste."""
    if not cfg.mutating:
        pytest.skip("DHARA_E2E_MUTATING=0 — pulando teste mutante")

    page = _login(driver, cfg)
    page.open_screen("faixa_etaria")
    page.wait_screen(["Faixa", "Etária"], timeout=90)

    page.click_text("Novo")
    page.fill_field("Descrição", cfg.faixa_descricao)
    page.click_first_available(["Salvar", "Confirmar"])
    page.wait_any_text([cfg.faixa_descricao, "salv", "sucesso"], timeout=30)

    # Excluir o registro criado
    page.open_screen("faixa_etaria")
    page.wait_screen([cfg.faixa_descricao], timeout=30)
    page.select_grid_row(0)
    page.click_first_available(["Excluir", "Deletar", "Remover"])
    page.click_first_available(["Sim", "Confirmar", "OK"])


@pytest.mark.mutating
@pytest.mark.cadastro
def test_raca_criar_excluir(driver, cfg):
    """Cria e exclui uma raça de teste."""
    if not cfg.mutating:
        pytest.skip("DHARA_E2E_MUTATING=0 — pulando teste mutante")

    page = _login(driver, cfg)
    page.open_screen("raca")
    page.wait_screen(["Raça", "Raca"], timeout=90)

    page.click_text("Novo")
    page.fill_field("Descrição", cfg.raca_descricao)
    page.click_first_available(["Salvar", "Confirmar"])
    page.wait_any_text([cfg.raca_descricao, "salv", "sucesso"], timeout=30)

    page.open_screen("raca")
    page.wait_screen([cfg.raca_descricao], timeout=30)
    page.select_grid_row(0)
    page.click_first_available(["Excluir", "Deletar", "Remover"])
    page.click_first_available(["Sim", "Confirmar", "OK"])


@pytest.mark.mutating
@pytest.mark.cadastro
def test_tipo_exame_criar_excluir(driver, cfg):
    """Cria e exclui um tipo de exame de teste."""
    if not cfg.mutating:
        pytest.skip("DHARA_E2E_MUTATING=0 — pulando teste mutante")

    page = _login(driver, cfg)
    page.open_screen("tipo_exame")
    page.wait_screen(["Tipo", "Exame"], timeout=90)

    page.click_text("Novo")
    page.fill_field("Descrição", cfg.tipo_exame_descricao)
    page.click_first_available(["Salvar", "Confirmar"])
    page.wait_any_text([cfg.tipo_exame_descricao, "salv", "sucesso"], timeout=30)

    page.open_screen("tipo_exame")
    page.wait_screen([cfg.tipo_exame_descricao], timeout=30)
    page.select_grid_row(0)
    page.click_first_available(["Excluir", "Deletar", "Remover"])
    page.click_first_available(["Sim", "Confirmar", "OK"])
