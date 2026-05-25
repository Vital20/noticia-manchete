# 📰 Analisador de Manchetes e Enquadramento Midiático

**Projeto Acadêmico** — Sistema de coleta, análise de sentimento e visualização de manchetes de notícias.

## 🎯 Objetivo

O sistema permite que o usuário pesquise um tema (ex: "Flamengo", "Lula", "Inteligência Artificial") e obtenha:

1. **Coleta automática** de manchetes recentes de 5 grandes portais brasileiros
2. **Classificação de tom** (Positivo, Negativo, Neutro) para cada manchete
3. **Dashboard interativo** com gráficos, tabelas e nuvem de palavras
4. **Comparação** entre o enquadramento de diferentes portais
5. **Resumo por IA** utilizando a API Groq

## 🏗️ Estrutura do Projeto

```
projeto/
├── app.py              # Interface Streamlit (dashboard completo)
├── scraper.py          # Coleta de manchetes dos portais
├── sentiment.py        # Análise de sentimento em português
├── ia_resumo.py        # Integração com API Groq (resumo por IA)
├── visualizacoes.py    # Gráficos (Plotly) e nuvem de palavras (WordCloud)
├── banco.py            # Persistência em SQLite
├── utils.py            # Utilitários (limpeza de texto, stopwords, constantes)
├── requirements.txt    # Dependências do projeto
├── .env.example        # Template para configuração da chave da API
├── noticias.db         # Banco de dados (criado automaticamente)
├── assets/             # Recursos visuais
│   └── logo.png
└── dados/              # Exportação de dados
```

## 🚀 Como Executar

### 1. Instalar Python 3.11+

Certifique-se de ter Python 3.11 ou superior instalado.

### 2. Criar ambiente virtual (recomendado)

```bash
python -m venv venv
```

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar chave da API Groq (opcional)

Copie o arquivo de exemplo e adicione sua chave:

```bash
cp .env.example .env
```

Edite o arquivo `.env` e substitua `sua_chave_aqui` pela sua chave da API Groq.

> Obtenha sua chave em: [https://console.groq.com](https://console.groq.com)

A chave é necessária apenas para o recurso de **resumo por IA**. O restante do sistema funciona sem ela.

### 5. Executar

```bash
streamlit run app.py
```

O sistema abrirá automaticamente no navegador em `http://localhost:8501`.

## 📡 Portais Analisados

| Portal | Site |
|--------|------|
| G1 | g1.globo.com |
| CNN Brasil | cnnbrasil.com.br |
| UOL | uol.com.br |
| Folha de S.Paulo | folha.uol.com.br |
| Estadão | estadao.com.br |

## 🧠 Funcionalidades

- **Análise de Sentimento**: Classificação baseada em léxico de palavras positivas/negativas em português
- **Gráficos Interativos**: Plotly com design moderno e dark mode
- **Nuvem de Palavras**: Visualização das palavras mais frequentes nas manchetes
- **Linha do Tempo**: Frequência de publicações ao longo do tempo
- **Comparação entre Portais**: Diferenças de tom e volume por portal
- **Resumo por IA**: Resumo automático usando Groq API (modelo principal + fallback)
- **Histórico**: Banco SQLite com análises anteriores
- **Design Responsivo**: Layout profissional adaptado para apresentação acadêmica

## 🛠️ Tecnologias

- **Python 3.11+**
- **Streamlit** — Interface web interativa
- **Pandas** — Manipulação de dados
- **Plotly + Matplotlib** — Visualizações
- **NLTK + TextBlob** — Processamento de linguagem natural
- **WordCloud** — Nuvem de palavras
- **BeautifulSoup4 + Requests** — Web scraping
- **Groq API** — IA para resumo
- **SQLite** — Banco de dados local

## ⚙️ Requisitos

- Python 3.11+
- Conexão com internet (para coleta de manchetes e API Groq)
- ~500 MB de espaço em disco (bibliotecas e dados)

## 📝 Notas Acadêmicas

Este projeto foi desenvolvido para fins acadêmicos, demonstrando a aplicação de técnicas de:

- Web scraping e coleta de dados
- Processamento de linguagem natural (NLP)
- Análise de sentimento em português
- Visualização de dados interativa
- Integração com APIs de IA
- Arquitetura de software modular

---
