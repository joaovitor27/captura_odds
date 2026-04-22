# Captura de Odds - Rei do Pitaco

Uma automação em Python projetada para navegar no site Rei do Pitaco, extrair competições e partidas, e mapear os mercados de odds ativas (como Resultado Final e outros). O projeto armazena os dados encontrados em um banco de dados local e gera um relatório em Excel completo com os resultados consolidados.

## ✨ Funcionalidades Principais

- **Mapeamento Automático de Competições e Jogos**: Navega nas abas e captura em memória a base de jogos do dia.
- **Leitura em Massa de Virtuoso/React Rendering**: Usa scroll programático para revelar dados renderizados dinamicamente via React Virtuoso.
- **Arquitetura de Estratégias Pluggáveis**: Usa o padrão *Strategy* para processar diferentes tipos de mercados esportivos.
- **Exportação para Excel**: Consolida o extraído em uma planilha `.xlsx` organizada.
- **Interface Visual Rica**: Usa a biblioteca `rich` para dar visibilidade estendida do processo direto no terminal.

## 🛠️ Tecnologias Utilizadas

- **Selenium**: Para automação do navegador.
- **Pandas / OpenPyxl**: Para manipulação e exportação para `.xlsx`.
- **Rich**: Para interface colorida e barra de progresso no terminal.
- **Python 3.10+** (recomendado).

## 🗂️ Estrutura do Projeto

```
📦 captura_odds
 ┣ 📂 database       # Lida com conexões de BD locais e repositórios
 ┣ 📂 models         # Classes de modelo e escopo de dados (dataclasses/Pydantic)
 ┣ 📂 scrapers       # Lógica base do Selenium para raspar os dados (ReiDoPitacoScraper)
 ┣ 📂 strategies     # Padrão strategy para parsing de odds em variados mercados
 ┣ 📂 utils          # Utilitários globais para toda a aplicação (Logs, Formatação)
 ┣ 📜 chromium.py    # Driver customizado para o Chromium/Chrome
 ┣ 📜 driver.py      # Funções utilitárias relacionadas ao Selenium Driver
 ┣ 📜 main.py        # O ponto de entrada principal do projeto
 ┗ 📜 README.md      # Este arquivo
```

## 🚀 Como Executar

### 1. Pré-Requisitos

Certifique-se de ter o Python instalado. O projeto utiliza um ambiente gerido por `.venv` ou `uv`.

### 2. Instalando as Dependências

Ative seu ambiente virtual (se aplicável), e instale as dependências via pip, uv ou outro gerenciador:

```bash
# Exemplo com pip
pip install -r requirements.txt
```
*(Caso utilize `uv`, rode `uv sync` ou conforme necessário pelo seu arquivo `pyproject.toml` ou `uv.lock` local).*

### 3. Rodando o Robô (Scraper)

Apenas execute o arquivo principal na raiz do projeto:

```bash
python main.py
```

O navegador Chromium se abrirá, processará as competições, fará a captura e ao fim da rotina um arquivo Excel será gerado no mesmo diretório no formato:
`relatorio_odds_YYYYMMDD_HHMMSS.xlsx`

## 📝 Boas Práticas e Arquitetura

O código foca na separação de responsabilidades (Repository, Strategy, Scraper, Model). Em caso de desenvolvimento ou manutenção:
- **Novos Mercados**: Implemente uma nova classe herdando de `MarketStrategy` e adicione a mesma à lista `strategies` instanciada em `main.py`.
- **Atrasos/Timeouts**: Como o site utiliza muito client-side rendering (React), `driver.py` fornece `wait_presence_by_xpath` que deve ser utilizado contra renderizações condicionais.
