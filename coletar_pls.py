"""Coleta os PLs de 2026 do Senado e grava no banco."""

import re
import ssl
from datetime import date, datetime

import certifi
import httpx
from sqlalchemy import func, select

from radaris.db import Sessao
from radaris.modelos import Proposicao, Sigla

URL = "https://legis.senado.leg.br/dadosabertos/processo"
PARAMETROS = {"sigla": "PL", "ano": 2026}
CABECALHOS = {"Accept": "application/json"}
PADRAO_IDENTIFICACAO = re.compile(r"^(\S+) (\d+)/(\d{4})")

contexto_tls = ssl.create_default_context(cafile=certifi.where())
contexto_tls.maximum_version = ssl.TLSVersion.TLSv1_2  # ver DIARIO.md (04/10)


def para_data(texto):
    return date.fromisoformat(texto) if texto else None


def para_data_hora(texto):
    return datetime.fromisoformat(texto) if texto else None


def obter_sigla(sessao, casa, sigla):
    """Busca a sigla no banco; se não existir, cria."""
    existente = sessao.scalar(
        select(Sigla).where(Sigla.casa == casa, Sigla.sigla == sigla)
    )
    if existente:
        return existente
    nova = Sigla(casa=casa, sigla=sigla)
    sessao.add(nova)
    return nova


resposta = httpx.get(
    URL, params=PARAMETROS, headers=CABECALHOS, timeout=60, verify=contexto_tls
)
resposta.raise_for_status()
processos = resposta.json()

novas = atualizadas = 0
with Sessao() as sessao:
    for p in processos:
        casamento = PADRAO_IDENTIFICACAO.match(p["identificacao"])
        if not casamento:
            print(f"Identificação fora do padrão, ignorada: {p['identificacao']}")
            continue
        sigla, numero, ano = casamento.groups()
        casa = p["casaIdentificadora"]
        sigla_registro = obter_sigla(sessao, casa, sigla)

        proposicao = sessao.scalar(
            select(Proposicao).where(
                Proposicao.casa == casa, Proposicao.id_origem == p["id"]
            )
        )
        if proposicao is None:
            proposicao = Proposicao(casa=casa, id_origem=p["id"])
            novas += 1
        else:
            atualizadas += 1

        proposicao.sigla = sigla_registro
        proposicao.numero = numero
        proposicao.ano = int(ano)
        proposicao.identificacao = p["identificacao"]
        proposicao.ementa = p.get("ementa", "").strip()
        proposicao.autoria_resumo = p.get("autoria")
        proposicao.data_apresentacao = para_data(p.get("dataApresentacao"))
        proposicao.situacao = p.get("situacaoAtual")
        proposicao.data_situacao = para_data(p.get("dataSituacaoAtual"))
        proposicao.tramitando = p.get("tramitando") == "Sim"
        proposicao.atualizado_na_origem = para_data_hora(p.get("dataUltimaAtualizacao"))
        proposicao.coletado_em = datetime.now()
        sessao.add(proposicao)

    sessao.commit()

    total = sessao.scalar(select(func.count()).select_from(Proposicao))
    da_camara = sessao.scalar(
        select(func.count())
        .select_from(Proposicao)
        .where(Proposicao.autoria_resumo == "Câmara dos Deputados")
    )

print(f"Novas: {novas} | Atualizadas: {atualizadas} | Total no banco: {total}")
print(f"Vindas da Câmara: {da_camara}")