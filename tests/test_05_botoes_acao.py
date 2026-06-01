"""
test_05_botoes_acao.py
Inventario dos botoes de acao customizados do addon.
Valida que os botoes existem no codigo Java (nao testa UI diretamente).

Para cada botao, verifica se o arquivo Java correspondente existe
na branch desenv do addon.
"""
import os
from pathlib import Path
import pytest

# Caminho para o addon (configurado via env ou default)
ADDON_PATH = Path(os.getenv("DHARA_ADDON_PATH", r"C:\dharatecnologia\dhara-pecuaria"))

BOTOES = [
    ("Baixar Animal",            "model/src/main/java/br/com/sankhya/dhara/pecuaria/buttons/BaixaAnimalButton.java"),
    ("Vincular Projeto",         "model/src/main/java/br/com/sankhya/dhara/pecuaria/buttons/VincularProjetoButton.java"),
    ("Vincular Animais Projeto", "model/src/main/java/br/com/sankhya/dhara/pecuaria/buttons/VincularAnimaisProjetoButton.java"),
    ("Diagnostico",              "model/src/main/java/br/com/sankhya/dhara/pecuaria/buttons/DiagnosticoButton.java"),
    ("Refazer Diagnostico",      "model/src/main/java/br/com/sankhya/dhara/pecuaria/buttons/RefazerDiagnosticoButton.java"),
    ("Gerar Nota de Venda",      "model/src/main/java/br/com/sankhya/dhara/pecuaria/buttons/GerarNotaVendaButton.java"),
    ("Preencher Saidas",         "model/src/main/java/br/com/sankhya/dhara/pecuaria/buttons/PreencherSaidasButton.java"),
    ("Validar Animais de Saida", "model/src/main/java/br/com/sankhya/dhara/pecuaria/buttons/ValidarSaidaButton.java"),
    ("Importar Lote",            "model/src/main/java/br/com/sankhya/dhara/pecuaria/buttons/ImportarLoteButton.java"),
    ("Importar Animais do Lote", "dbscripts/V13.xml"),
    ("Transferir Animal",        "model/src/main/java/br/com/sankhya/dhara/pecuaria/buttons/TransferirAnimalButton.java"),
]


@pytest.mark.parametrize("acao,arquivo", BOTOES)
def test_botao_implementado(acao, arquivo):
    """Cada botao de acao customizado deve ter seu arquivo Java implementado."""
    caminho = ADDON_PATH / arquivo
    assert caminho.exists(), (
        f"Acao sem implementacao: {acao}\n"
        f"Arquivo esperado: {caminho}\n"
        "Crie o arquivo antes de disponibilizar esta acao para o usuario."
    )
