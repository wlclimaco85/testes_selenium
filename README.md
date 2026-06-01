# 🐄 Testes Selenium — Dhara Pecuária Addon Sankhya

Suite de testes Selenium para o addon **Dhara Pecuária** rodando no **Sankhya Om 4.35b185 + WildFly**.

> Branch do addon testada: **desenv**
> Repo do addon: `C:\dharatecnologia\dhara-pecuaria`

---

## 📁 Estrutura

```
testes_selenium/
├── .env.example              # Template de configuração
├── pytest.ini                # Marcadores e configuração pytest
├── requirements.txt          # Dependências Python
└── tests/
    ├── conftest.py           # Driver, login shadow-DOM, fixtures
    ├── pages/
    │   └── sankhya_page.py   # Page Object — login, navegação, esperas GWT
    ├── test_00_smoke_navigation.py    # Abre todas as 11 telas
    ├── test_01_cadastros_base.py      # Faixa Etária, Raça, Tipo Exame
    ├── test_02_entrada_animais.py     # Entrada, Histórico
    ├── test_03_reproducao.py          # IATF, Diagnóstico, Parto
    ├── test_04_apontamento_saida.py   # Apontamento, Saída
    ├── test_05_botoes_acao.py         # Inventário de botões Java
    └── test_06_fluxo_completo.py      # Fluxo ponta a ponta
```

---

## ⚠️ Pré-requisitos

### 1. WildFly rodando
```
http://localhost:8080/mge/ → HTTP 200
```

### 2. Patch sf.js aplicado (OBRIGATÓRIO)
O `system.jsp` do Sankhya 4.35 precisa ter **antes** do `snk.js`:
```html
<script src="scripts/vendors/sf/sf.js"></script>
<script src="scripts/snk.js?v=0"></script>
```
Arquivo: `standalone/tmp/vfs/deployment/.../mge-4.35b185.war-.../system.jsp`

### 3. Oracle 21c rodando
Verificar que `SANKHYA/tecsis@localhost:1522/xepdb1` conecta.

---

## ⚙️ Configuração

```bash
cp .env.example .env
# Editar .env com os dados do seu ambiente
```

Campos obrigatórios:
| Variável | Descrição |
|----------|-----------|
| `SANKHYA_BASE_URL` | URL base do Sankhya (ex: http://localhost:8080) |
| `SANKHYA_USER` | Usuário (padrão: `sup`) |
| `SANKHYA_PASSWORD` | Senha |

---

## 🚀 Executar

### Instalar dependências
```bash
pip install -r requirements.txt
```

### Smoke — todas as 11 telas (sem alterar dados)
```bash
python -m pytest tests/ -m smoke -v
```

### Cadastros base
```bash
python -m pytest tests/test_01_cadastros_base.py -v
```

### Reprodução (IATF, Diagnóstico, Parto)
```bash
python -m pytest tests/test_03_reproducao.py -v
```

### Apenas verificar se botões Java existem
```bash
python -m pytest tests/test_05_botoes_acao.py -v
```

### Suite completa (smoke, sem dados mutantes)
```bash
python -m pytest tests/ -v --ignore=tests/test_06_fluxo_completo.py
```

### Tudo incluindo testes mutantes (requer DHARA_E2E_MUTATING=1)
```bash
DHARA_E2E_MUTATING=1 python -m pytest tests/ -v
```

### Headless
```bash
HEADLESS=1 python -m pytest tests/ -v
```

---

## 🗺️ Telas cobertas

| Tela | Menu ID | Test |
|------|---------|------|
| Configuração Pecuária | `pecuaria.configuracao` | test_00, test_01 |
| Faixa Etária | `pecuaria.faixa` | test_00, test_01 |
| Raça de Animais | `pecuaria.raca` | test_00, test_01 |
| Tipo de Exame | `pecuaria.tipexame` | test_00, test_01 |
| Histórico de Animais | `pecuaria.historico` | test_00, test_02 |
| Entrada de Animais | `pecuaria.entrada` | test_00, test_02 |
| IATF / Monta | `pecuaria.iatf` | test_00, test_03 |
| Diagnóstico de Gestação | `pecuaria.diag` | test_00, test_03 |
| Registro de Parto | `pecuaria.parto` | test_00, test_03 |
| Apontamento Pecuária | `pecuaria.apontamento` | test_00, test_04 |
| Saída de Animais | `pecuaria.saida` | test_00, test_04 |

---

## 🔐 Login shadow-DOM

O Sankhya 4.35 usa `<sankhya-login>` com Shadow DOM. O `conftest.py` já lida com isso automaticamente:

```python
# Etapa 1: usuario via shadow_root
root = driver.find_element(By.CSS_SELECTOR, "sankhya-login").shadow_root
root.find_element(By.CSS_SELECTOR, "#user").send_keys("sup")
# clicar Prosseguir → preencher senha → clicar Prosseguir
```

---

## 📸 Evidências

Screenshots são salvas automaticamente em `artifacts/`:
- `artifacts/screens/` — screenshots de telas aprovadas
- `artifacts/FAILED_*.png` — captura automática em falhas

---

## 🏷️ Marcadores

| Marcador | O que cobre |
|----------|-------------|
| `smoke` | Apenas abre/navega, nao altera dados |
| `cadastro` | CRUD de cadastros base |
| `entrada` | Entrada de animais |
| `reproducao` | IATF, Diagnostico, Parto |
| `apontamento` | Apontamento de pecuaria |
| `saida` | Saida e venda de animais |
| `mutating` | Altera dados — requer `DHARA_E2E_MUTATING=1` |

---

*Branch testada: **desenv** · Gerado por @dhara-sankhya-orchestrator*
