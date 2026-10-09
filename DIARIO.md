# Diário de bordo — Radaris

Registro das sessões de desenvolvimento: o que foi feito, decisões, aprendizados e próximos passos.

---

## 2026-10-01 — Planejamento e exploração das APIs

**Feito:** definido o escopo do MVP (monitoramento de proposições, filtros por tema/autor, alertas e agenda); escolhida a stack; criado o repositório; primeira exploração das APIs da Câmara e do Senado pelo navegador e pelo Swagger.

**Decisões:**
- Ambiente: Windows 11 + WSL2 (Ubuntu) no desktop. Notebook com Linux Mint descartado por pouca memória.
- Stack: Python 3.12, FastAPI, PostgreSQL + SQLAlchemy, HTMX + Tailwind, Docker.
- Senado primeiro, Câmara depois. Cada API terá um adaptador que converte os dados para um modelo interno único de "Proposição".
- Repositório sem licença por enquanto (ideia de negócio); commits com o e-mail `noreply` do GitHub.

**Aprendi:**
- Endpoint = endereço da API que entrega um tipo de dado. Swagger/OpenAPI = documentação interativa que permite testar chamadas.
- O caminho do endpoint precisa do endereço base completo para funcionar.
- Na Câmara, a sigla do tipo se repete (REQ tem dezenas de subtipos); o identificador confiável é o código (`cod`).

**Problemas / pegadinhas:**
- Endpoint de referências "vazio" no Swagger: faltava clicar em *Try it out* → *Execute*.
- A lista de tipos da Câmara mistura cabeçalhos de agrupamento (sigla vazia) com os tipos reais.
- O serviço `/materia` do Senado está descontinuado; o substituto é `/processo`.
- Suspeitei que o `/processo` ignorava filtros, mas o problema estava na ferramenta usada no teste (corrigido em 04/10).

**Próximo passo:** instalar o ambiente no desktop.

---

## 2026-10-04 — Ambiente de desenvolvimento e primeira consulta ao Senado

**Feito:**
- Ambiente: WSL2 com Ubuntu 26.04, Git 2.53, uv 0.12, Python 3.12.15; VS Code conectado ao WSL.
- Chave SSH (ed25519) cadastrada no GitHub; repositório clonado em `~/projetos/radaris`.
- Projeto criado com `uv init` (estrutura `src/`) e dependência `httpx`.
- `senado_teste.py`: consulta PLs de 2026 no Senado → 496 processos, 0 fora do filtro.

**Decisões:**
- Projetos ficam no sistema de arquivos do Linux (`~/projetos`), editados pelo VS Code conectado ao WSL.
- Estrutura `src/radaris/` para o código do sistema; scripts de exploração ficam na raiz.
- Conexão com o Senado limitada a TLS 1.2, apenas nesse cliente. Nunca desligar a verificação de certificado (`verify=False`).

**Aprendi:**
- `sudo` = executar como administrador; só para mexer no sistema, nunca no projeto.
- PATH = pastas onde o terminal procura os programas.
- Pipe (`|`) = passa a saída de um comando para outro (ex.: `cat chave.pub | clip.exe`).
- Chave SSH: a pública vai para o GitHub; a privada nunca sai da máquina. O fingerprint do servidor fica salvo em `~/.ssh/known_hosts`.
- WSL = Linux numa máquina virtual leve; o Windows enxerga os arquivos dele como compartilhamento de rede local.
- Traceback: ler de baixo para cima e procurar a linha do próprio arquivo.
- `uv.lock` garante as mesmas versões de bibliotecas em qualquer máquina.

**Problemas / pegadinhas:**
- O Ubuntu já estava instalado, com usuário criado anteriormente.
- Os erros "Failed to connect to system scope bus" no `apt upgrade` são inofensivos no WSL.
- **Conexão com o Senado travava no handshake TLS** (timeout e `UNEXPECTED_EOF_WHILE_READING`). Diagnóstico por eliminação:

  | Teste | Resultado |
  |---|---|
  | Python no WSL → Senado | falha |
  | curl no WSL → Senado | falha |
  | curl no Windows → Senado | ok |
  | curl no WSL → Câmara | ok |
  | WSL forçando IPv4 | falha |
  | WSL com MTU 1350 | falha |
  | WSL com TLS 1.2 | **ok** |

  Causa: o OpenSSL do Ubuntu 26.04 envia, no TLS 1.3, uma saudação maior (com métodos pós-quânticos), e o servidor do Senado trava. Solução: limitar a TLS 1.2 com um `ssl.SSLContext` passado ao httpx.

**Dúvidas em aberto:**
- A API não ordena por número; definir a ordenação no Radaris.

**Próximo passo:** montar a tabela de correspondência de campos Senado × Câmara e a lista de tipos de proposição que um gabinete monitora (base do Módulo 2: modelagem).

---

## 2026-10-09 — Módulo 2: campos, tipos, histórias de usuário e modelo de dados

**Feito:**
- Documento de referência "Radaris — Campos e tipos: Senado × Câmara" (campos das duas APIs, equivalência de tipos, siglas ativas do Senado, modelo de dados).
- Scripts `exportar_tipos.py` (tipos de proposição das duas Casas em CSV) e `camara_campos.py` (campos da API da Câmara, com recursão para campos aninhados), este rodado na máquina do trabalho.
- Quatro histórias de usuário: projeto próprio, matéria de interesse (mensagem presidencial), relatoria e pauta semanal.
- Modelo de dados consolidado, com diagrama ER, tabelas por fase (MVP, v1.1, v2), regras de alerta e regras do coletor.

**Decisões:**
- Coletar todos os tipos e filtrar na exibição. 25 siglas monitoradas por padrão (DEN, DLG, INQ, INS, MCN, MPV, MSF, MSG, OFS, PDL, PDN, PEC, PL, PLP, PLV, PLN, PRS, QCN, QED, QSF, REQ, RQN, RQS, SUG, VET), editáveis pelo usuário.
- Duas camadas de dados: públicos (APIs, iguais para todos) e do gabinete (privados, isolados por gabinete).
- MVP: alertas, agenda/pautas, anotações com anexo. v1.1: emendas, versões do texto, prazos, boletim da pauta. v2: orientações, tarefas, pedidos à Consultoria, posicionamento.
- Incluídos no modelo: norma gerada, tema/classificação e monitoramento de emendas por projeto.
- Próxima etapa com SQLite e SQLAlchemy; PostgreSQL só quando o modelo estabilizar.

**Aprendi:**
- Parâmetro de consulta (o que se envia para filtrar) ≠ campo de resposta (o que volta). Ex.: `tramitacaoSenado` na Câmara é filtro, não campo.
- "Example Value" do Swagger ≠ "Response body": o exemplo é modelo da documentação; só a execução mostra o dado real.
- Aviso do editor (Pylance) ≠ erro de execução.
- A API omite campos sem valor: ler com `.get()`.
- Normalização: o que se repete (eventos, autores, temas, vínculos) vai para tabelas separadas.
- Modelo da fonte (como o Senado autua) ≠ modelo do produto (como o gabinete enxerga).

**Problemas / pegadinhas da API do Senado:**
- O detalhe do processo repete informes e apensados várias vezes (duplicatas pelo mesmo `id`).
- Vínculos assimétricos: o RQS 396/2026 (urgência) não aponta para o PL 1.126/2021, mas o PL aponta para o RQS. Os vínculos também são incompletos.
- `dataUltimaAtualizacao` muda sem mudança relevante (PL 21/2020: situação de 2024, atualização em 2026).
- Divergência entre Casas: PL 21/2020 prejudicado no Senado e `tramitando: Sim` na Câmara.
- A matéria muda de identidade: MSF 42/2026 virou PRS 36/2026 no dia seguinte à leitura.
- Achados úteis: o substitutivo traz `idProcessoCasaInicial` (vínculo com o original); a mensagem traz o número de origem (MSG 699/2026 da Presidência); o tipo do requerimento é estruturado (`URGENCIA_MATERIA`).

**Dúvidas em aberto (Módulo 3):**
- Confirmar no serviço novo (`/processo/{id}`) os vínculos vistos no serviço antigo.
- Endpoint da agenda/pauta das comissões.
- Como a API da Câmara liga emendas ao projeto principal.

**Próximo passo:** Módulo 4 — instalar o SQLAlchemy e criar as tabelas `sigla`, `proposicao` e `evento_tramitacao` em SQLite, gravando os PLs de 2026 coletados.
