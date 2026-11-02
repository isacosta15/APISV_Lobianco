🚀 APIs & Data Analytics | Projetos de Integração e Visualização de Dados

"Python" (https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
"Streamlit" (https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
"Pandas" (https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
"Plotly" (https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)
"REST API" (https://img.shields.io/badge/REST%20APIs-005571?style=for-the-badge&logo=fastapi&logoColor=white)

Repositório dedicado ao desenvolvimento de aplicações em Python que consomem APIs públicas, processam dados reais e transformam informações complexas em dashboards interativos.

O projeto reúne três aplicações independentes, desenvolvidas com foco em integração de serviços, tratamento de dados, autenticação, análise exploratória e visualização gráfica.

A proposta é explorar diferentes domínios de conhecimento — política, aviação e astronomia — demonstrando como dados disponibilizados por instituições e plataformas públicas podem ser utilizados para construir ferramentas de consulta e análise.

---

📌 Índice

- "Sobre o projeto" (#-sobre-o-projeto)
- "Projetos desenvolvidos" (#-projetos-desenvolvidos)
  - "10. Dashboard de Atividade Legislativa" (#10--dashboard-de-atividade-legislativa)
  - "11. Rastreador de Voos" (#11--rastreador-de-voos)
  - "12. Dashboard de Exploração Espacial" (#12--dashboard-de-exploração-espacial)
- "Tecnologias utilizadas" (#-tecnologias-utilizadas)
- "Conceitos aplicados" (#-conceitos-aplicados)
- "Estrutura do repositório" (#-estrutura-do-repositório)
- "Instalação e execução" (#-instalação-e-execução)
- "Configuração das APIs" (#-configuração-das-apis)
- "Objetivos de aprendizagem" (#-objetivos-de-aprendizagem)
- "Possíveis melhorias" (#-possíveis-melhorias)
- "Fontes e documentação" (#-fontes-e-documentação)
- "Autoria" (#-autoria)

---

🎯 Sobre o projeto

Este repositório faz parte de uma jornada de desenvolvimento voltada ao aprofundamento em Python, consumo de APIs REST e análise de dados.

Os projetos foram concebidos para trabalhar com informações disponibilizadas por diferentes fontes, explorando desde consultas simples até estruturas JSON complexas, autenticação, filtros, paginação e visualizações geográficas.

Cada aplicação possui uma finalidade específica:

Projeto| Área| Fonte principal
Dashboard Legislativo| Política e transparência pública| Câmara dos Deputados
Flight Radar| Aviação e geolocalização| OpenSky Network
Cosmos| Astronomia e ciência| NASA Open APIs

Objetivo principal: desenvolver aplicações capazes de transformar dados públicos em informações acessíveis, organizadas e visualmente compreensíveis.

---

🏛️ Projetos desenvolvidos

10. Dashboard de Atividade Legislativa

Área: Política, transparência pública e análise de dados.

<details>
<summary><strong>Descrição do projeto</strong></summary>Aplicação destinada à consulta e análise de informações relacionadas à atividade legislativa brasileira, utilizando dados abertos disponibilizados pela Câmara dos Deputados e, opcionalmente, pelo Senado Federal.

A proposta é explorar dados sobre parlamentares, proposições, votações, partidos e despesas, permitindo acompanhar indicadores de atuação parlamentar e identificar padrões de atividade legislativa.

</details>Fonte de dados

- "API de Dados Abertos da Câmara dos Deputados" (https://dadosabertos.camara.leg.br/)
- "Dados Abertos do Senado Federal" (https://www12.senado.leg.br/dados-abertos)

Funcionalidades planejadas

- Consulta de deputados e informações parlamentares.
- Busca de proposições legislativas.
- Consulta de votações e resultados.
- Análise de despesas parlamentares.
- Filtros por ano, partido, parlamentar e tema.
- Gráficos de atividade legislativa.
- Rankings de atuação parlamentar.
- Análise de participação em votações.

Desafios de análise

Desafio 1 — Ranking de proposições por tema

Identificar os deputados que mais apresentaram proposições relacionadas a um determinado tema, como saúde ou educação, durante um ano específico.

Representação: gráfico de barras horizontal, organizado por quantidade de proposições.

Desafio 2 — Participação em votações por partido

Construir um heatmap que apresente a participação dos partidos nas votações ao longo dos meses, identificando períodos de maior e menor atividade.

Conceitos técnicos

- Paginação de requisições.
- Autenticação opcional.
- Relacionamento entre deputados, proposições e votações.
- Tratamento de estruturas JSON aninhadas.
- Agrupamento e agregação de dados.
- Análise temporal e comparativa.

---

11. Flight Radar — Rastreador de Voos

Área: Aviação, geolocalização e monitoramento de dados.

<details>
<summary><strong>Descrição do projeto</strong></summary>Aplicação de rastreamento aéreo que utiliza dados disponibilizados pela OpenSky Network para consultar posições de aeronaves e visualizar trajetórias geográficas.

O sistema permite explorar informações de tráfego aéreo em regiões específicas, identificar aeronaves por seu código ICAO24 e analisar dados como velocidade, altitude, direção e país de origem.

</details>Fonte de dados

- "OpenSky Network" (https://opensky-network.org/)
- "Documentação da API" (https://openskynetwork.github.io/opensky-api/)

Funcionalidades implementadas

- Consulta de aeronaves em uma área geográfica.
- Definição de limites de latitude e longitude.
- Filtro por país de origem.
- Filtro por categoria de aeronave.
- Visualização de posições em mapa interativo.
- Consulta de trajetórias por ICAO24.
- Indicadores de velocidade, altitude e situação operacional.
- Gráficos de distribuição das aeronaves.
- Exportação dos dados em CSV.
- Autenticação OAuth2 opcional.

Desafios de análise

Desafio 1 — Monitoramento aéreo do Brasil

Criar um mapa interativo que apresente as aeronaves identificadas dentro de uma região que cobre o território brasileiro, com filtros por categoria, incluindo helicópteros e aviões.

Desafio 2 — Rastreamento de trajetórias

Informar o código ICAO24 de uma aeronave, recuperar os pontos de trajetória disponíveis e representar seu percurso em um mapa interativo.

Conceitos técnicos

- APIs REST.
- Coordenadas geográficas e bounding boxes.
- Dados de rastreamento ADS-B.
- Autenticação OAuth2.
- Manipulação de timestamps Unix.
- Visualização geográfica.
- Tratamento de dados ausentes.
- Análise de trajetórias.

Observação: a disponibilidade de posições e trajetórias depende da cobertura, dos registros armazenados e dos limites de acesso da OpenSky Network. O rastreamento não representa necessariamente o percurso completo de uma aeronave.

---

12. Cosmos — Dashboard de Exploração Espacial

Área: Astronomia, ciência e análise de dados.

<details>
<summary><strong>Descrição do projeto</strong></summary>Dashboard científico desenvolvido para explorar informações astronômicas e fenômenos naturais por meio das APIs disponibilizadas pela NASA e pelo NASA Exoplanet Archive.

A aplicação reúne diferentes fontes de dados em uma única interface, permitindo consultar asteroides próximos da Terra, imagens astronômicas, exoplanetas confirmados e eventos naturais registrados mundialmente.

</details>Fontes de dados

- "NASA Open APIs" (https://api.nasa.gov/)
- "NASA NeoWs" (https://api.nasa.gov/)
- "NASA APOD" (https://science.nasa.gov/astrophysics/programs/cosmic-origins/astronomy-picture-of-the-day/)
- "NASA EONET" (https://eonet.gsfc.nasa.gov/)
- "NASA Exoplanet Archive" (https://exoplanetarchive.ipac.caltech.edu/)

Funcionalidades implementadas

Asteroides próximos da Terra (NeoWs)

- Consulta por intervalo de datas.
- Identificação de objetos próximos da Terra.
- Análise de diâmetro estimado.
- Identificação de asteroides potencialmente perigosos.
- Comparação entre distância e velocidade relativa.
- Gráfico de dispersão com escala logarítmica.
- Exportação dos dados em CSV.

Imagem Astronômica do Dia (APOD)

- Consulta de imagens por data.
- Exibição do título e da descrição científica.
- Apresentação dos créditos da publicação.
- Suporte a conteúdos audiovisuais quando disponibilizados.

Exoplanetas

- Consulta de exoplanetas confirmados.
- Identificação dos métodos de descoberta.
- Gráfico de distribuição por método.
- Filtro pela quantidade de registros.
- Exportação dos resultados.

Eventos Naturais (EONET)

- Consulta de eventos naturais.
- Filtro por período.
- Identificação de categorias de eventos.
- Extração de coordenadas geográficas.
- Visualização de eventos em mapa interativo.
- Exportação dos registros em CSV.

Desafios de análise

Desafio 1 — Análise de asteroides

Permitir que o usuário escolha um intervalo de datas e gere um gráfico de dispersão relacionando a distância da Terra e a velocidade relativa dos asteroides próximos.

Desafio 2 — Dashboard científico integrado

Desenvolver uma interface com diferentes seções para apresentar:

- Imagem astronômica do dia, com título e explicação.
- Gráfico de barras dos métodos de descoberta de exoplanetas.
- Mapa geográfico dos eventos naturais registrados pela EONET.

Conceitos técnicos

- Integração com múltiplos endpoints.
- Autenticação por API Key.
- Consumo e tratamento de JSON.
- Consultas SQL via TAP.
- Escalas logarítmicas.
- Análise exploratória de dados.
- Visualização geográfica.
- Manipulação de unidades científicas.

---

🛠️ Tecnologias utilizadas

As aplicações foram desenvolvidas utilizando ferramentas do ecossistema Python.

Tecnologia| Aplicação
Python| Linguagem principal
Requests| Consumo de APIs REST
Pandas| Manipulação e análise de dados
Streamlit| Desenvolvimento das interfaces
Plotly| Gráficos e mapas interativos
Seaborn| Visualizações estatísticas complementares
Matplotlib| Visualizações gráficas complementares

Principais recursos

- Integração com serviços externos.
- Tratamento de respostas HTTP.
- Processamento de dados estruturados.
- Construção de indicadores.
- Visualização interativa.
- Exportação de dados.
- Organização modular de aplicações.

---

🧠 Conceitos aplicados

O desenvolvimento dos projetos explora diferentes conceitos técnicos:

Conceito| Aplicação
APIs REST| Comunicação com serviços externos
HTTP| Requisições e respostas
JSON| Estruturas de dados recebidas das APIs
Autenticação| API Keys e OAuth2
Paginação| Consulta de grandes volumes de dados
DataFrames| Organização e transformação de dados
ETL| Extração, transformação e preparação
Geolocalização| Mapas e coordenadas geográficas
Data Visualization| Gráficos, indicadores e dashboards
Tratamento de erros| Respostas inválidas e falhas de conexão

---

📁 Estrutura do repositório

O repositório está organizado em diretórios independentes para facilitar a manutenção e a evolução de cada aplicação.

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

Cada diretório possui sua própria aplicação e suas dependências, permitindo executar os projetos separadamente.

---

⚙️ Instalação e execução

1. Pré-requisitos

Antes de iniciar, tenha instalado:

- Python 3.10 ou superior.
- Git.
- Visual Studio Code ou outro editor de código.
- Conexão com a internet.

2. Clonar o repositório

git clone https://github.com/SEU-USUARIO/APIs-Dados-Avancados.git

Entre no diretório:

cd APIs-Dados-Avancados

3. Criar um ambiente virtual

python -m venv venv

Ativar no Windows:

venv\Scripts\activate

Ativar no Linux ou macOS:

source venv/bin/activate

4. Instalar as dependências

Entre na pasta do projeto desejado.

Exemplo:

cd cosmos

Instale as dependências:

pip install -r requirements.txt

5. Executar a aplicação

streamlit run app.py

O Streamlit disponibilizará o endereço local para acessar a aplicação pelo navegador.

Repita o processo para os demais projetos.

---

🔐 Configuração das APIs

Algumas integrações utilizam autenticação para acessar os dados.

NASA Open APIs

É possível obter uma chave gratuita em:

https://api.nasa.gov/

A chave pode ser informada diretamente pela interface do dashboard ou configurada por variável de ambiente:

NASA_API_KEY=sua_chave_aqui

OpenSky Network

A OpenSky permite consultas básicas sem autenticação, mas oferece autenticação OAuth2 para condições de acesso e limites diferenciados.

Para utilizar credenciais, configure:

OPENSKY_CLIENT_ID=seu_client_id
OPENSKY_CLIENT_SECRET=seu_client_secret

Câmara dos Deputados

A API de Dados Abertos da Câmara permite consultas públicas e documentadas. A autenticação não é obrigatória para os endpoints públicos utilizados pelo projeto.

Documentação:

https://dadosabertos.camara.leg.br/swagger/api.html

Importante: nunca publique chaves de API, tokens ou credenciais diretamente no repositório. Utilize variáveis de ambiente ou arquivos ".env" protegidos pelo ".gitignore".

---

📈 Objetivos de aprendizagem

Com o desenvolvimento dessas aplicações, busca-se aprofundar conhecimentos em:

- Consumo e integração de APIs públicas.
- Autenticação e autorização de serviços.
- Tratamento de dados complexos.
- Manipulação de grandes conjuntos de dados.
- Análise exploratória e estatística.
- Construção de dashboards interativos.
- Visualização de dados geográficos.
- Organização e documentação de projetos Python.
- Desenvolvimento de soluções orientadas a dados.

---

🚀 Possíveis melhorias

Os projetos podem evoluir com a implementação de novos recursos:

Projeto| Evoluções
Dashboard Legislativo| Comparação entre legislaturas, análise de discursos e acompanhamento de votações
Flight Radar| Histórico de voos, identificação de rotas recorrentes e filtros geográficos avançados
Cosmos| Comparação de asteroides, catálogo ampliado de exoplanetas e análises astronômicas adicionais

Outras melhorias gerais incluem:

- Testes automatizados.
- Cache inteligente de consultas.
- Separação entre interface, serviços e processamento.
- Integração com bancos de dados.
- Deploy em serviços de hospedagem.
- Melhorias de acessibilidade e responsividade.

---

📚 Fontes e documentação

Documentações oficiais utilizadas como referência:

Fonte| Documentação
Câmara dos Deputados| https://dadosabertos.camara.leg.br/
Senado Federal| https://www12.senado.leg.br/dados-abertos
OpenSky Network| https://openskynetwork.github.io/opensky-api/
NASA Open APIs| https://api.nasa.gov/
NASA EONET| https://eonet.gsfc.nasa.gov/
NASA Exoplanet Archive| https://exoplanetarchive.ipac.caltech.edu/
Python| https://docs.python.org/3/
Streamlit| https://docs.streamlit.io/
Pandas| https://pandas.pydata.org/docs/
Plotly| https://plotly.com/python/

---

👩‍💻 Autoria

Desenvolvido por Isabela Costa Nunes

Estudante de Análise e Desenvolvimento de Sistemas, com interesse em desenvolvimento de software, análise de dados, integração de APIs e construção de soluções tecnológicas.

Este repositório representa uma jornada prática de aprendizado, exploração de tecnologias e desenvolvimento de aplicações orientadas a dados.

Tecnologia, dados e conhecimento transformando informações em possibilidades.

---

<p align="center">
  Desenvolvido com Python e curiosidade pelo universo dos dados.
</p><p align="center">
  ⭐ Se este repositório foi útil, considere deixar uma estrela!
</p>
