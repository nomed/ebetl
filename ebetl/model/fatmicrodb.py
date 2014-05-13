# -*- coding: utf-8 -*-
"""
Auth* related model.

This is where the models used by the authentication stack are defined.

It's perfectly fine to re-use this definition in the ebetl application,
though.

"""
import os, sys
from datetime import datetime
from hashlib import sha256
#__all__ = ['User', 'Group', 'Permission']

from sqlalchemy import Table, ForeignKey, Column, Sequence
from sqlalchemy.types import Unicode, Integer, DateTime, Boolean
from sqlalchemy.orm import relation, synonym

from ebetl.model import DeclarativeBase, metadata, DBSession

class Fatmicro(DeclarativeBase):
    """

    """

    __tablename__ = 'input_fatmicro'

    numeromagazzino = Column(Integer, autoincrement=True, primary_key=True)
    codicemagazzino = Column(Unicode(16), unique=True, nullable=False)
    magazzino = Column(Unicode(255))
    #created = Column(DateTime, default=datetime.now)
    #users = relation('User', secondary=user_group_table, backref='groups')



class Cli00(DeclarativeBase):
    """
    """
    __tablename__ = 'input_cli00'
    
    class __sprox__(object):
        #__limit_fields__ = ['display_name', 'email_address']
        omit_fields = ['cli00_id']
    
    cli00_id = Column(Integer,Sequence('cli00_id'), autoincrement=True, primary_key=True)
    codice_articolo = Column(Unicode(8), unique=True, nullable=False)
    descrizione_articolo = Column(Unicode(30))
    confezionamento = Column(Unicode(2))
    tipo_grammatura = Column(Unicode(2))
    grammatura = Column(Integer)
    multiplo = Column(Integer)
    pezzatura = Column(Integer)
    merceologia = Column(Unicode(12))
    reparto_pos = Column(Integer)
    prezzo = Column(Integer)
    prezzo_cessione = Column(Integer)    
    ultimo_costo = Column(Integer)
    udm = Column(Integer)
    ean = Column(Unicode(13))
    codice_iva = Column(Integer)
    active = Column(Boolean)
    new = Column(Boolean)
    aggiornato = Column(DateTime)
 
 
class Cli00sede(DeclarativeBase):
    """
    """
    __tablename__ = 'input_cli00sede'
    cli00_id = Column(Integer,Sequence('cli00_id'), autoincrement=True, primary_key=True)
    codice_articolo = Column(Unicode(8), unique=True, nullable=False)
    descrizione_articolo = Column(Unicode(30))
    confezionamento = Column(Unicode(2))
    tipo_grammatura = Column(Unicode(2))
    grammatura = Column(Integer)
    multiplo = Column(Integer)
    pezzatura = Column(Integer)
    merceologia = Column(Unicode(12))
    reparto_pos = Column(Integer)
    prezzo = Column(Integer)
    prezzo_cessione = Column(Integer)    
    ultimo_costo = Column(Integer)
    udm = Column(Integer)
    ean = Column(Unicode(13))
    codice_iva = Column(Integer)
    active = Column(Boolean)
    new = Column(Boolean)
    aggiornato = Column(DateTime)   
    
