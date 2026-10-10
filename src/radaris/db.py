"""Conexão com o banco de dados."""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

URL_BANCO = "sqlite:///radaris.db"

engine = create_engine(URL_BANCO)
Sessao = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    """Classe-mãe de todas as tabelas do Radaris."""