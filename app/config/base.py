from sqlalchemy import ForeignKey, Table, Column, Integer
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

Usuario_Evento = Table(
    "Usuario_Evento",
    Base.metadata,
    Column("idUsuario", Integer, ForeignKey("usuarios.idUsuario"), primary_key=True),
    Column("idEvento", Integer, ForeignKey("eventos.idEvento"), primary_key=True)
)