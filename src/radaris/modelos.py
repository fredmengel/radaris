"""Tabelas do Radaris: núcleo da camada pública."""

from datetime import date, datetime

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from radaris.db import Base


class Sigla(Base):
    __tablename__ = "sigla"
    __table_args__ = (UniqueConstraint("casa", "sigla"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    casa: Mapped[str] = mapped_column(String(2))
    sigla: Mapped[str] = mapped_column(String(20))
    descricao: Mapped[str | None] = mapped_column(String(300))
    ativa: Mapped[bool] = mapped_column(default=True)
    padrao: Mapped[bool] = mapped_column(default=False)


class Proposicao(Base):
    __tablename__ = "proposicao"
    __table_args__ = (UniqueConstraint("casa", "id_origem"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    casa: Mapped[str] = mapped_column(String(2))
    id_origem: Mapped[int]
    sigla_id: Mapped[int] = mapped_column(ForeignKey("sigla.id"))
    numero: Mapped[str] = mapped_column(String(10))
    ano: Mapped[int]
    identificacao: Mapped[str] = mapped_column(String(100))
    ementa: Mapped[str] = mapped_column(Text)
    autoria_resumo: Mapped[str | None] = mapped_column(String(300))
    data_apresentacao: Mapped[date | None]
    situacao: Mapped[str | None] = mapped_column(String(200))
    data_situacao: Mapped[date | None]
    tramitando: Mapped[bool | None]
    atualizado_na_origem: Mapped[datetime | None]
    coletado_em: Mapped[datetime] = mapped_column(default=datetime.now)

    sigla: Mapped["Sigla"] = relationship()
    eventos: Mapped[list["EventoTramitacao"]] = relationship(back_populates="proposicao")


class EventoTramitacao(Base):
    __tablename__ = "evento_tramitacao"
    __table_args__ = (UniqueConstraint("proposicao_id", "id_origem"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    proposicao_id: Mapped[int] = mapped_column(ForeignKey("proposicao.id"))
    id_origem: Mapped[int | None]
    data: Mapped[datetime]
    colegiado: Mapped[str | None] = mapped_column(String(20))
    situacao: Mapped[str | None] = mapped_column(String(200))
    descricao: Mapped[str] = mapped_column(Text)

    proposicao: Mapped["Proposicao"] = relationship(back_populates="eventos")