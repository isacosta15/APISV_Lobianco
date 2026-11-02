APIs & Data Analytics

Projetos de integração de APIs, processamento de dados e visualização interativa

Repositório dedicado ao desenvolvimento de projetos práticos utilizando APIs públicas, Python e ferramentas de análise de dados. O objetivo é transformar dados disponibilizados por diferentes fontes em informações estruturadas, visualizações interativas e indicadores que facilitem a exploração e a interpretação dos dados.

---

Projetos

Projeto| Descrição| Fonte de dados
"Dashboard de Atividade Legislativa" (./atividade-legislativa/)| Análise de proposições, votações e participação parlamentar.| Câmara dos Deputados e Senado Federal
"Rastreador de Voos em Tempo Real" (./flight-radar/)| Visualização de aeronaves e acompanhamento de voos.| OpenSky Network
"Dashboard de Exploração Espacial" (./cosmos/)| Exploração de asteroides, exoplanetas e eventos naturais.| NASA APIs

---

1. Dashboard de Atividade Legislativa

Objetivo: desenvolver um dashboard para explorar e analisar dados da atividade parlamentar brasileira, utilizando informações disponibilizadas por APIs públicas.

Funcionalidades propostas

- Consulta de deputados e partidos.
- Listagem de proposições legislativas.
- Consulta de votações e participação parlamentar.
- Análise de despesas e gastos parlamentares.
- Ranking de deputados por assunto e período.
- Visualização da participação por partido e mês.
- Gráficos e indicadores interativos.

Tecnologias

- Python
- Requests
- Pandas
- Plotly
- Seaborn
- Streamlit

Desafios de análise

1. Criar um ranking dos deputados mais atuantes por tema e ano.
2. Desenvolver um mapa de calor da participação parlamentar por partido e mês.

Fonte de dados

- "API de Dados Abertos da Câmara dos Deputados" (https://dadosabertos.camara.leg.br/swagger/api.html)
- "Dados Abertos do Senado Federal" (https://www12.senado.leg.br/dados-abertos)

---

2. Rastreador de Voos em Tempo Real

Objetivo: desenvolver uma aplicação para acompanhar aeronaves em tempo real, utilizando dados disponibilizados pela OpenSky Network.

Funcionalidades

- Consulta de aeronaves em operação.
- Visualização de aeronaves em um mapa.
- Filtro por região geográfica.
- Identificação de aeronaves por código ICAO24.
- Exibição de informações como altitude, velocidade e direção.
- Consulta de trajetórias históricas, quando disponíveis pela API.

Tecnologias

- Python
- Requests
- Pandas
- Folium
- Plotly
- Streamlit

Desafios de análise

1. Criar um mapa interativo com a localização das aeronaves sobre o território brasileiro.
2. Implementar filtros para explorar aeronaves por categoria.
3. Selecionar uma aeronave pelo código ICAO24 e consultar sua trajetória, quando disponível.

Fonte de dados

- "OpenSky Network" (https://opensky-network.org/)
- "Documentação da API" (https://openskynetwork.github.io/opensky-api/)

---

3. Dashboard de Exploração Espacial

Objetivo: desenvolver uma aplicação interativa para explorar dados astronômicos e eventos naturais por meio das APIs disponibilizadas pela NASA.

APIs utilizadas

API| Descrição
NeoWs| Consulta de asteroides próximos à Terra.
APOD| Imagem astronômica do dia.
NASA Exoplanet Archive| Consulta de dados sobre exoplanetas.
EONET| Monitoramento de eventos naturais.

Funcionalidades

- Consulta de asteroides próximos à Terra.
- Identificação de asteroides potencialmente perigosos.
- Exibição da imagem astronômica do dia.
- Exploração de exoplanetas conhecidos.
- Visualização de eventos naturais em mapas.
- Gráficos e indicadores para análise dos dados.

Tecnologias

- Python
- Requests
- Pandas
- Seaborn
- Plotly
- Streamlit

Desafios de análise

1. Identificar os asteroides com maior aproximação da Terra em determinado período.
2. Criar visualizações para comparar características de exoplanetas.
3. Mapear a distribuição de eventos naturais por categoria e localização.

Fontes de dados

- "NASA APIs" (https://api.nasa.gov/)
- "NASA Open Data" (https://data.nasa.gov/)
- "NASA Exoplanet Archive" (https://exoplanetarchive.ipac.caltech.edu/)
- "EONET" (https://eonet.gsfc.nasa.gov/)

---

Tecnologias e ferramentas

As principais tecnologias utilizadas e exploradas nos projetos são:

"Python" (https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
"Pandas" (https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
"Plotly" (https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)
"Streamlit" (https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
"Requests" (https://img.shields.io/badge/Requests-2CA5E0?style=for-the-badge&logo=python&logoColor=white)
"Git" (https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white)
"GitHub" (https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)

Conceitos aplicados

- Consumo e integração de APIs REST.
- Requisições HTTP e tratamento de respostas JSON.
- Paginação e filtragem de dados.
- Limpeza e transformação de dados.
- Análise exploratória de dados (EDA).
- Manipulação de dados com Pandas.
- Construção de gráficos e dashboards interativos.
- Geolocalização e visualização em mapas.
- Tratamento de erros e dados ausentes.

---

Como executar os projetos

1. Clone o repositório

git clone https://github.com/SEU-USUARIO/SEU-REPOSITORIO.git

2. Acesse a pasta do projeto

cd SEU-REPOSITORIO

3. Crie um ambiente virtual

python -m venv venv

No Windows:

venv\Scripts\activate

No Linux ou macOS:

source venv/bin/activate

4. Instale as dependências

Acesse a pasta do projeto desejado e execute:

pip install -r requirements.txt

5. Execute a aplicação

Se o projeto utilizar Streamlit:

streamlit run app.py

---

Organização do repositório

APIs-Dados-Avancados/
│
├── README.md
│
├── atividade-legislativa/
│   ├── app.py
│   ├── requirements.txt
│   └── README.md
│
├── flight-radar/
│   ├── app.py
│   ├── requirements.txt
│   └── README.md
│
└── cosmos/
    ├── app.py
    ├── requirements.txt
    └── README.md

---

Observações

- Algumas funcionalidades podem depender dos limites de requisição estabelecidos pelas APIs.
- A disponibilidade de dados históricos depende de cada fonte.
- A API da NASA disponibiliza uma chave gratuita, que pode ser obtida no portal oficial.
- O acesso à OpenSky pode ter limites diferentes conforme o tipo de autenticação e as políticas vigentes.
- O Dashboard de Atividade Legislativa representa uma proposta de desenvolvimento e pode receber novas funcionalidades conforme sua implementação.

---

Autora

Isabela Costa Nunes

Estudante de Análise e Desenvolvimento de Sistemas, interessada em desenvolvimento de software, análise de dados, integração de APIs e visualização de informações.

""GitHub" (https://img.shields.io/badge/GitHub-isacosta15-181717?style=for-the-badge&logo=github)" (https://github.com/isacosta15)

---

Projetos desenvolvidos com foco em aprendizado prático, exploração de dados abertos e desenvolvimento de soluções interativas.
