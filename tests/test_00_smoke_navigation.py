"""
test_00_smoke_navigation.py
Valida que todas as 11 telas do addon Dhara Pecuaria abrem sem erro.
Nao altera dados (DHARA_E2E_MUTATING ignorado).
"""
from pathlib import Path

import pytest

from tests.pages.sankhya_page import SankhyaPage, DHARA_SCREENS

SCREENS = list(DHARA_SCREENS.items())  # (chave, menu_id)


@pytest.mark.smoke
@pytest.mark.parametrize("screen_key,menu_id", SCREENS)
def test_abre_tela_dhara(driver, cfg, screen_key, menu_id):
    """Cada tela do addon deve abrir sem erro de profile/404."""
    page = SankhyaPage(driver, cfg.base_url)

    # Login
    page.open("mge")
    page.login(cfg.username, cfg.password)
    assert page.is_logged_in(), "Login falhou"

    # Navegar para a tela
    page.open_screen(screen_key)

    # Aguardar render — aceita qualquer keyword relevante
    keywords = {
        "configuracao": ["Configuração", "Configuracao", "Pecuária"],
        "faixa_etaria": ["Faixa", "Etária", "Bezerro", "Animal"],
        "raca":         ["Raça", "Raca", "Animal"],
        "tipo_exame":   ["Tipo", "Exame", "Ultrassom"],
        "historico":    ["Histórico", "Historico", "Animal", "Movimentação"],
        "entrada":      ["Entrada", "Animal", "Lote", "Nota"],
        "iatf":         ["IATF", "Monta", "Matriz", "Reprodução"],
        "diagnostico":  ["Diagnóstico", "Diagnostico", "Gestação", "Exame"],
        "parto":        ["Parto", "Nascimento", "Cria"],
        "apontamento":  ["Apontamento", "Pecuária", "Insumo"],
        "saida":        ["Saída", "Saida", "Animal", "Venda"],
    }.get(screen_key, ["Dhara", "Pecu", "Salvar", "Novo", "Pesquisar"])

    page.wait_screen(keywords, timeout=90)

    # Screenshot de evidencia
    page.save_screenshot(Path(f"artifacts/screens/{screen_key}.png"))
