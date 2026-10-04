"""Primeira consulta à API de Dados Abertos do Senado."""

import ssl

import certifi
import httpx

URL = "https://legis.senado.leg.br/dadosabertos/processo"
PARAMETROS = {"sigla": "PL", "ano": 2026}
CABECALHOS = {"Accept": "application/json"}

# O servidor do Senado trava no handshake TLS 1.3 com o OpenSSL recente
# (saudação maior, com métodos pós-quânticos). Limitamos a TLS 1.2,
# apenas nesta conexão. Ver DIARIO.md (04/10/2026).
contexto_tls = ssl.create_default_context(cafile=certifi.where())
contexto_tls.maximum_version = ssl.TLSVersion.TLSv1_2

resposta = httpx.get(
    URL,
    params=PARAMETROS,
    headers=CABECALHOS,
    timeout=60,
    verify=contexto_tls,
)
resposta.raise_for_status()

processos = resposta.json()
print(f"URL chamada: {resposta.url}")
print(f"Processos recebidos: {len(processos)}")

fora_do_filtro = [
    p for p in processos
    if not p["identificacao"].startswith("PL ") or "/2026" not in p["identificacao"]
]
print(f"Fora do filtro: {len(fora_do_filtro)}")

for processo in processos[:5]:
    ementa = processo.get("ementa", "").strip()
    print(f"- {processo['identificacao']}: {ementa[:90]}")