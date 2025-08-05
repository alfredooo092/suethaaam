# Analisador PagBank Pro

Sistema completo de análise de extratos do PagBank com dashboard organizado, configuração de taxas por cliente e cálculo automático de lucro.

## 🚀 Funcionalidades

- **Upload de Extratos CSV**: Importação automática de dados do PagBank
- **Dashboard Organizado**: Visualização clara de máquinas e transações
- **Configuração de Taxas**: Taxas independentes para cada cliente/máquina
- **Cálculo de Lucro**: Análise automática de rentabilidade
- **Acumulação de Dados**: Múltiplos uploads sem perder dados anteriores
- **Tabela Detalhada**: Visualização completa com valor líquido e lucro

## 📊 Como Usar

1. **Upload**: Faça upload do seu arquivo CSV do PagBank
2. **Visualização**: Veja todas as suas máquinas no dashboard
3. **Configuração**: Configure as taxas que você cobra de cada cliente
4. **Análise**: Calcule automaticamente seu lucro vs custos PagBank
5. **Relatórios**: Visualize tabelas detalhadas com todos os valores

## 🛠️ Deploy no Render

### Opção 1: Deploy Automático
1. Faça fork deste repositório no GitHub
2. Conecte sua conta do Render ao GitHub
3. Crie um novo Web Service no Render
4. Selecione este repositório
5. O Render detectará automaticamente as configurações

### Opção 2: Deploy Manual
1. Baixe todos os arquivos deste projeto
2. Crie um novo repositório no GitHub
3. Faça upload de todos os arquivos
4. Conecte ao Render e faça deploy

### Configurações do Render
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn --bind 0.0.0.0:$PORT src.main:app`
- **Python Version**: 3.11.0

## 📁 Estrutura do Projeto

```
pagbank-analyzer/
├── src/
│   ├── main.py              # Aplicação principal Flask
│   ├── routes/
│   │   └── pagbank.py       # Rotas da API
│   ├── models/
│   │   └── machine.py       # Modelos do banco de dados
│   └── static/
│       └── index.html       # Interface web
├── requirements.txt         # Dependências Python
├── render.yaml             # Configuração do Render
├── Procfile                # Configuração de processo
├── runtime.txt             # Versão do Python
└── README.md               # Este arquivo
```

## 🔧 Desenvolvimento Local

1. Clone o repositório
2. Instale as dependências: `pip install -r requirements.txt`
3. Execute: `python src/main.py`
4. Acesse: `http://localhost:5000`

## 📈 Recursos Técnicos

- **Backend**: Flask + SQLAlchemy
- **Frontend**: HTML5 + CSS3 + JavaScript
- **Banco de Dados**: SQLite (desenvolvimento) / PostgreSQL (produção)
- **Deploy**: Render.com
- **Funcionalidades**: Upload CSV, Dashboard, Cálculos financeiros

## 🎯 Casos de Uso

- **Consultores PagBank**: Análise de rentabilidade por cliente
- **Empresas**: Controle de taxas e lucros
- **Contadores**: Relatórios financeiros detalhados
- **Gestores**: Dashboard executivo de performance

---

Desenvolvido para análise profissional de extratos PagBank com foco em rentabilidade e gestão de clientes.

