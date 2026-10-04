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
- O que significa o sufixo "(Substitutivo-CD)" na identificação, e o gabinete precisa distinguir esses casos?
- A API não ordena por número; definir a ordenação no Radaris.

**Próximo passo:** montar a tabela de correspondência de campos Senado × Câmara e a lista de tipos de proposição que um gabinete monitora (base do Módulo 2: modelagem).
