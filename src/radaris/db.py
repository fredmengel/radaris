"""Conexão com o banco de dados."""

import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

RAIZ_PROJETO = Path(__file__).resolve().parents[2]
URL_BANCO = os.environ.get(
    "RADARIS_DB_URL", f"sqlite:///{RAIZ_PROJETO / 'radaris.db'}"
)

engine = create_engine(URL_BANCO)
Sessao = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    """Classe-mãe de todas as tabelas do Radaris."""