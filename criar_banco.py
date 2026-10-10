"""Cria as tabelas do Radaris no banco."""

from radaris import modelos  # noqa: F401  (registra as tabelas na Base)
from radaris.db import Base, engine

Base.metadata.create_all(engine)
print("Tabelas criadas:", ", ".join(Base.metadata.tables))