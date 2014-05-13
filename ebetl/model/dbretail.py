# -*- coding: utf-8 -*-
"""
DBRETAIL related model.

"""
import os, sys
from datetime import datetime
from hashlib import sha256
#__all__ = ['User', 'Group', 'Permission']

from sqlalchemy import Table, ForeignKey, Column, Sequence, and_, or_
from sqlalchemy.types import Unicode, Integer, BigInteger, DateTime, Float, String, Date, BLOB
from sqlalchemy.orm import relation, synonym, backref
from sqlalchemy.sql import label
from sqlalchemy import func
from ebetl.model import DeclarativeBase, metadata, DBSession

from sprox.fillerbase import TableFiller
from sprox.tablebase import TableBase

from ebetl.lib.etl import get_margin, get_price_discount

contasincrofield = Sequence('contasincrofield')
contaclientefid = Sequence('contaclientefid')
contamovimentofid = Sequence('contamovimentofid')
contaprovenienza = Sequence('contaprovenienza')
contaprodottoprovenienza = Sequence('contaprodottoprovenienza')
contaunitamisura = Sequence('contaunitamisura')
containventario = Sequence('containventario')
contarigainventario = Sequence('contarigainventario')
contarigainventarioconta = Sequence('contarigainventarioconta')
contaautoean = Sequence('contaautoean')
contab2b = Sequence('contab2b')
contamovimento = Sequence('contamovimento')
contarigamovimento = Sequence('contarigamovimento')
count_b2b = Sequence('count_b2b')
contaalias = Sequence('contaalias')


class Magazzini(DeclarativeBase):
    __tablename__ = 'magazzini'
    sincrofield = Column(Integer, contasincrofield , autoincrement=True, primary_key=True)
    numeromagazzino = Column(Integer, autoincrement=True, primary_key=True)
    codicemagazzino = Column(String(16), unique=True, nullable=False)
    magazzino = Column(String(255))

class Provenienze(DeclarativeBase):
    __tablename__ = 'provenienze'
    sincrofield = Column(Integer, contasincrofield , autoincrement=True)    
    tipoprovenienza = Column(String(3))#FOR,CLI
    numeroprovenienza= Column(Integer, contaprovenienza, 
                            autoincrement=True, primary_key=True)    
    codiceprovenienza = Column(String(20), unique=True, nullable=False)  
    provenienza =  Column(String(100))
    partitaiva = Column(String(16))
    codicefiscale = Column(String(16))
    indirizzo = Column(String(100))
    cap = Column(String(5))
    citta = Column(String(50))
    prov = Column(String(2))
    telefono1 = Column(String(30))
    telefono2 = Column(String(30))
    cellulare = Column(String(30))
    fax = Column(String(30))
    email=Column(String(30))
    prodottiprovenienza = Column(Integer)

class Listini(DeclarativeBase):
    __tablename__ = 'listini'
    sincrofield = Column(Integer, contasincrofield , autoincrement=True, primary_key=True)    
    numerolistino = Column(Integer,autoincrement=True, primary_key=True)
    codice=Column(String(4))
    
class Listiniprodotti(DeclarativeBase):
    __tablename__ = 'listiniprodotti'
    sincrofield = Column(Integer, contasincrofield , autoincrement=True, primary_key=True)
    numeroprodotto = Column(Integer)
    numerolistino = Column(Integer,ForeignKey('listini.numerolistino'))
    listino = relation('Listini', backref='prezzi')
    prezzo = Column(Float)
    numeroprodotto = Column(Integer, ForeignKey('prodotti.numeroprodotto'))
    prodotto = relation('Prodotti', backref='listini')     

class Listiniprovenienze(DeclarativeBase):
    __tablename__ = 'listiniprovenienze'
    sincrofield = Column(Integer, contasincrofield , autoincrement=True, primary_key=True)
    numerolistinoprovenienza = Column(Integer,primary_key=True)
    numeroprodottoprovenienza = Column(Integer, ForeignKey(
                        'prodottiprovenienze.numeroprodottoprovenienza'))
    prodottoprovenienza = relation('Prodottiprovenienze', backref='listini')  
    numeroeanprodotto = Column(Integer, ForeignKey(
                        'eanprodotti.numeroeanprodotto'))
    eanprodotto = relation('Eanprodotti', backref='listiniean')      
    numeroprovenienza = Column(Integer, ForeignKey(
                        'provenienze.numeroprovenienza'))
    proveninenza = relation('Provenienze', backref='listini')
    validodal = Column(DateTime)      
    validoal = Column(DateTime)
    prezzonetto = Column(Float)
    stvariazionenetto = Column(String(50))

    @property
    def disc(self):
        """"""
        
        return get_price_discount(self.prezzonetto,self.stvariazionenetto)     

class Sottoscorta(DeclarativeBase):
    __tablename__ = 'sottoscorta'
    sincrofield = Column(Integer, contasincrofield , autoincrement=True, primary_key=True)
    numeroazienda = Column(Integer)
    numeromagazzino = Column(Integer,ForeignKey('magazzini.numeromagazzino'))    
    numeroprodotto = Column(Integer, ForeignKey('prodotti.numeroprodotto'))
    numeroeanprodotto = Column(Integer, ForeignKey('eanprodotti.numeroeanprodotto'))
    qtascorta = Column(Float)
    qtariordino = Column(Float)  
   
class Prodotti(DeclarativeBase):
    __tablename__ = 'prodotti'
    sincrofield = Column(Integer, contasincrofield , autoincrement=True)
    numeroprodotto = Column(Integer, Sequence('contaprodotto'),autoincrement=True, primary_key=True)
    codiceprodotto = Column(String(20))
    prodottobreve = Column(String(20))
    prodotto = Column(String(40))
    numerotipologiaprodotto = Column(Integer)
    numeroproduttore = Column(Integer)    
    datainserimento = Column(DateTime)
    varprezzocon = Column(Integer)
    numeroreparto = Column(Integer,ForeignKey('reparti.numeroreparto'))
    reparto = relation('Reparti', backref=backref('prodotti', order_by=codiceprodotto))          
    numeroiva = Column(Integer, ForeignKey('iva.numeroiva'))
    iva = relation('Iva', backref=backref('prodotti', order_by=codiceprodotto))  
    numerounitamisura = Column(Integer, ForeignKey('unitamisure.numerounitamisura'))
    unitamisura = relation('Unitamisure', backref='prodotti')         
    costonetto = Column(Float)
    dataultimocosto = Column(DateTime)
    pezzixcollo=Column(Float)
    qtacontenuto = Column(Float)
    numeroumvisualizzazione = Column(Integer)
    
    numerocontocontabilitai = Column(Integer, ForeignKey('conticontabilita.numerocontocontabilita'))
    numerocontocontabilitau = Column(Integer, ForeignKey('conticontabilita.numerocontocontabilita'))

    @property
    def udm_view(self):
        return DBSession.query(Unitamisure).filter_by(
                          numerounitamisura=str(self.numeroumvisualizzazione)).one()
    
    @property
    def listini(self):
        return DBSession.query(Listiniprodotti).filter_by(
                          numeroprodotto=str(self.numeroprodotto)).all()
        
 
    
    @property
    def prezzo(self):
        try:
            l=DBSession.query(Listiniprodotti).filter(and_(
            Listiniprodotti.numeroprodotto=="%s"%self.numeroprodotto,
            Listiniprodotti.numerolistino==0
                )).one()
            return l.prezzo
        except:
            return 0
                
    @property
    def valoreiva(self):
        if self.iva:
            return self.iva.valoreiva
        else:
            return self.reparto.iva.valoreiva
  
    @classmethod
    def margin(cls, price, cost):
        """"""
        
        return get_margin(price,cost)

    @classmethod
    def disc(cls, price, disc):
        """"""
        
        return get_price_discount(price,disc)        
              
class Conticontabilita(DeclarativeBase):
    __tablename__ = 'conticontabilita'
    #logicdelete
    sincrofield = Column(Integer, contasincrofield , autoincrement=True)
    #sincroserverfield
    #instablog
    #updtablog
    #numerogruppcontocontabilita = Column(Integer)    
    numerocontocontabilita = Column(Integer, autoincrement=True, primary_key=True) 
    codicecontocontabilita = Column(String(20))
    contocontabilita = Column(String(50))
    ordine = Column(Integer) 


class Gruppireparti(DeclarativeBase):
    __tablename__ = 'gruppireparti'
    sincrofield = Column(Integer, contasincrofield , autoincrement=True)
    numerogrupporeparto = Column(Integer,Sequence('contagrupporeparto'), autoincrement=True, primary_key=True)
    grupporeparto = Column(String(40))

class Reparti(DeclarativeBase):
    __tablename__ = 'reparti'
    sincrofield = Column(Integer, contasincrofield , autoincrement=True)
    numeroreparto = Column(Integer,Sequence('contareparto'), autoincrement=True, primary_key=True)
    codicereparto = Column(Integer)
    reparto = Column(String(40))
    numerocontocontabilitai = Column(Integer, ForeignKey('conticontabilita.numerocontocontabilita'))
    contocosto = relation('Conticontabilita',
                            primaryjoin="Reparti.numerocontocontabilitai\
                            ==Conticontabilita.numerocontocontabilita ")
    numerocontocontabilitau = Column(Integer, ForeignKey('conticontabilita.numerocontocontabilita'))
    numeroiva = Column(Integer, ForeignKey('iva.numeroiva'))
    iva = relation('Iva', backref=backref('reparti', order_by=codicereparto)) 
    numerogrupporeparto =  Column(Integer, ForeignKey('gruppireparti.numerogrupporeparto'))
    grupporeparto = relation('Gruppireparti', backref=backref('reparti'))  


        
class Iva(DeclarativeBase):
    __tablename__ = 'iva'
    sincrofield = Column(Integer, contasincrofield , autoincrement=True, primary_key=True)
    numeroiva = Column(Integer,Sequence('contaiva'), autoincrement=True, primary_key=True)
    codiceiva = Column(String(10))
    descrizioneiva = Column(String(100))
    valoreiva = Column(Float)
    numeroivaecr = Column(Integer)
    
    @property
    def mult(self):
        return float(1) + float(self.valoreiva)/float(100)

class Gruppounitamisure(DeclarativeBase):
    __tablename__ = 'gruppounitamisure'
    sincrofield = Column(Integer, contasincrofield , autoincrement=True)
    numerogruppounitamisura = Column(Integer,Sequence('contaunitamisura'), autoincrement=True, primary_key=True)

class Unitamisure(DeclarativeBase):
    __tablename__ = 'unitamisure'
    sincrofield = Column(Integer, contasincrofield , autoincrement=True)
    numerounitamisura = Column(Integer,Sequence('contaunitamisura'), autoincrement=True, primary_key=True)
    codiceunitamisura = Column(String(10))
    unitamisura = Column(String(50))
    numerogruppounitamisure = Column(Integer)
    moltiplicatoreunita = Column(Integer)
    #numerogruppounitamisura = Column(Integer)
    #gruppounitamisura = relation('Gruppounitamisure', backref='udms')   


    @property
    def udm(self):
        return pow(10, self.moltiplicatoreunita)

class Eanprodotti(DeclarativeBase):
    __tablename__ = 'eanprodotti'
    numeroeanprodotto = Column(Integer,Sequence('contaeanprodotto'), autoincrement=True, primary_key=True)
    sincrofield = Column(Integer, contasincrofield , autoincrement=True, primary_key=True)
    ean = Column(String(13), unique=True, nullable=False)
    codicetasto=Column(Integer)    
    codicebilancia=Column(Integer)
    numerogruppobilancia=Column(Integer)
    #varprezzocon = Column(Integer) 
    numeroprodotto = Column(Integer, ForeignKey('prodotti.numeroprodotto'))
    prodotto = relation('Prodotti', backref='eans')   
    eancorpopeso =   Column(String(1))   
    giorniscadenzabilancia = Column(Integer) 
    prodottoean=Column(String(300))
    prezzovariabilebilancia=Column(Integer)
    qtaxconf = Column(Integer)
    
class Prodottiprovenienze(DeclarativeBase):
    __tablename__ = 'prodottiprovenienze'
    sincrofield = Column(Integer, contasincrofield , autoincrement=True, primary_key=True)
    numeroprodottoprovenienza = Column(Integer, contaprodottoprovenienza, autoincrement=True, primary_key=True)
    tipoprovenienza = Column(String(3))
    numeroprovenienza = Column(Integer, ForeignKey('provenienze.numeroprovenienza')) 
 
    numeroprodotto = Column(Integer, ForeignKey('prodotti.numeroprodotto'))
    prodotto = relation('Prodotti')     
    numeroeanprodotto = Column(Integer, ForeignKey('eanprodotti.numeroeanprodotto'))
    ean = relation('Eanprodotti', backref=backref('prodottiprovenienze'))         
    codiceprodottoprovenienza =  Column(String(30))
    prodottoprovenienza =  Column(String(100))  
    ordine = Column(Integer)
    provenienza = relation('Provenienze', backref=backref('referenze', 
                                          order_by=codiceprodottoprovenienza))        
        
class Movimentit(DeclarativeBase):
    __tablename__='movimentit'
    #logicdelete
    sincrofield = Column(Integer, contasincrofield , autoincrement=True, primary_key=True)
    sincroserverfield = Column(Integer)
    #instablog
    #updtablog
    numeromovimento = Column(Integer, contamovimento, autoincrement=True, primary_key=True)
    tipodocumento = Column(String(3))
    numeroazienda = Column(Integer)
    numerosedeazienda = Column(Integer)
    #tipoagente
    #numeroagente
    numerocodicemovimento = Column(Integer)
    codicemovimento = Column(String(10))
    clifor = Column(String(1))
    ingressouscita = Column(String(1))
    #documentoacconto
    datamovimento = Column(DateTime)
    anno = Column(Integer)
    mese = Column(Integer)
    settimana = Column(Integer)
    numdoc = Column(Integer)
    numdoclocale = Column(Integer)
    numerodocumento = Column(String(100))
    datadocumento = Column(DateTime)
    #proforma
    #numeroproforma
    #dataproforma
    numeromovimentocontabile = Column(Integer)
    #numeromodellostampa
    #variante
    tipoprovenienza = Column(String(3))
    numeroprovenienza = Column(Integer, ForeignKey('provenienze.numeroprovenienza')) 
    provenienza= relation('Provenienze')       
    numerosedeprovenienza = Column(Integer)
    #intestazione
    ragionesociale=Column('provenienza', String(250))
    codicefiscale = Column(String(16))
    partitaiva = Column(String(16))    
    #
    indirizzo = Column(String(100))  
    cap = Column(String(5))  
    citta = Column(String(50))  
    prov = Column(String(2))  
    #telefono
    #fax
    #destinazione
    #indirizzodestinazione
    #capdestinazione
    #cittadestinazione
    #provdestinazione
    #telefonodestinazione
    #faxdestinazione
    #numeromagazzinoda
    #numeroclienteda
    #numerosedeclienteda
    #consegnainiziotrasporto
    #amezzo
    #dataorainizio
    #dataoraritiro
    #vettore
    #dativettore
    #dataoraritirovettore
    #pesokg
    #colli
    #porto
    #aspettoesteriore
    #causaletrasporto
    #bancale
    #bancaliprecedenti
    #bancaliconsegnati
    #bancaliresi
    #bancalimancanti
    #modelloautoveicolo
    #targaautoveicolo
    #conducenteautoveicolo
    totaleimponibile = Column(Float)
    totaleiva = Column(Float)
    totaledocumento = Column(Float)
    numeroformapagamento = Column(Integer)
    numerotipopagamento = Column(Integer)
    #contocorrente
    #note
    controllonote=Column(Integer)
    #documentoannullato = 
    #pk
    #numeronazione
    #prefissopartitaiva
    #oggettomovimento
    #dataaccettazione
    #datainiziolavori
    #datafinelavori
    #numerocontratto
    #ordinecliente
    #dataordinecliente
    numerostatolavoro=Column(Integer)
    #percsal
    #numerolistino
    protocollo=Column(String(20))
    elaborato = Column(Integer)

class Movimentir(DeclarativeBase):
    __tablename__='movimentir'
    #logicdelete
    sincrofield = Column(Integer, contasincrofield , autoincrement=True)
    #sincroserverfield
    instablog = Column(Integer)
    #updtablog
    numeromovimento = Column(Integer, ForeignKey('movimentit.numeromovimento'))
    movimento = relation('Movimentit',  backref='movimentir')     
    numerorigamovimento = Column(Integer, contarigamovimento, autoincrement=True, primary_key=True)
    datamovimento = Column(DateTime)
    dataregistrazione = Column(DateTime)
    movqta = Column(Integer )
    movval = Column(Integer )
    modalitainserimento = Column(String(1))
    tiporiga = Column(String(1))
    codice = Column(String(30))
    descrizione = Column(String(500))    
    tipoprodotto = Column(String(3)) 
    # == prodotto
    idprodotto = Column(Integer, ForeignKey('prodotti.numeroprodotto') )
    prodotto = relation('Prodotti') 
    
    # == eanprodotto
    numeroeanprodotto = Column(Integer, ForeignKey('eanprodotti.numeroeanprodotto')  )
    eanprodotto=relation('Eanprodotti')
    
    ean = Column(String(13))
    
    idalias = Column(Integer ) 
    alias = Column(String(30))
    numerounitamisura = Column(Integer ) 
    codiceunitamisura = Column(String(10))
    cifresignificative = Column(Integer ) 
    lotto = Column(String(50))
    pesokg = Column(Float)
    pezzixcollo = Column(Float)
    
    # == reparti
    numeroreparto = Column(Integer, ForeignKey('reparti.numeroreparto')  )
    reparto = relation('Reparti')
    
    numeroproduttore = Column(Integer)
    numeroprodottoproduttore = Column(Integer)
    numerolistino = Column(Integer)
    numeroiva = Column(Integer, ForeignKey('iva.numeroiva'))
    iva = relation('Iva', backref='movimenti') 
    tipoprovenienzaordine = Column(String(3))
    #numeroordine = Column(Integer)
    #numerorigaordine = Column(Integer)
    #numeropreventivo = Column(Integer)
    #numerorigapreventivo = Column(Integer)
    #numeromovimentoorigine
    #numerorigamovimentoorigine
    #numerofogliolavoro
    #numerorigafogliolavoro
    
    # == magazzini
    numeromagazzino = Column(Integer,ForeignKey('magazzini.numeromagazzino'),     
                                    nullable=True)
    magazzino = relation('Magazzini')
    #tipoprovenienzalavorazione
    #numeroprovenienzalavorazione
    #datalavorazione
    
    # == contocontabilita
    numerocontocontabilita = Column(Integer,ForeignKey('conticontabilita.numerocontocontabilita'), 
                                    nullable=True)        
    conto = relation('Conticontabilita')        
    
    
    codiceqta = Column(String(15))
    qtamovimento = Column(Float)
    qtascarico = Column(Float)
    percentualeiva = Column(Float)
    qtacalcolocosto = Column(Float)
    costonetto = Column(Float)
    ivacosto = Column(Float)
    costo = Column(Float)
    totalecostonetto = Column(Float)
    ivatotalecosto = Column(Float)
    totalecosto = Column(Float)
    prezzonettolistino = Column(Float)
    ivaprezzolistino = Column(Float)
    prezzolistino = Column(Float)
    prezzonetto = Column(Float)
    ivaprezzo = Column(Float) 
    prezzo = Column(Float)
    stvariazionenetto = Column(String(50))
    variazionepercnetto = Column(Float)
    stvariazione = Column(String(50))
    variazioneperc = Column(Float)
    totalenetto = Column(Float)
    ivatotale = Column(Float)
    totale = Column(Float)
    dafatturare = Column(Integer)
    qtafatturata = Column(Float)
    #deposito
    #numerocausalescarto
    #rigaannullata
    chiusura = Column(DateTime)
    #dataconfezionamento
    #datascadenza
    #misure
    #note
    #stileriga
    ordine = Column(Integer)
    #pk
 

class Ricevutet(DeclarativeBase):
    __tablename__='ricevutet'
    #logicdelete
    sincrofield = Column(Integer, contasincrofield , autoincrement=True, primary_key=True)
    #sincroserverfield
    #instablog
    #updtablog
    numeromovimento = Column(Integer, autoincrement=True, primary_key=True)
    numerogiorno = Column(Integer)
    numerogiornopos = Column(Integer)
    numeropos = Column(Integer)
    numerooperatore = Column(Integer)
    numerodipendente = Column(Integer)
    numeroclientefid = Column(Integer)
    puntiricevuta = Column(Integer)
    tiporicevuta = Column(String(1))
    ricevutasospesa = Column(Integer)
    numerosala = Column(Integer)
    numerotavolo = Column(Integer)
    numerocoperti = Column(Integer)
    camerieri = Column(String(150))
    qtaunicariga = Column(Float)
    descrizioneunicariga = Column(String(150))
       
class Movimentiiva(DeclarativeBase):
    __tablename__ = 'movimentiiva'
    sincrofield = Column(Integer, contasincrofield , autoincrement=True, primary_key=True)    
    numeromovimento = Column(Integer,ForeignKey('movimentit.numeromovimento')) 
    movimentot=relation('Movimentit', backref='movimentiiva')
    numeroiva = Column(Integer, ForeignKey('iva.numeroiva'))
    iva = relation('Iva', backref='movimentiiva')     
    totaleimponibile = Column(Float)        
    totaleiva=Column(Float)
    
class Pagamenti(DeclarativeBase):
    __tablename__ = 'pagamenti'
    #logicdelete
    sincrofield = Column(Integer, contasincrofield , autoincrement=True, primary_key=True)
    #sincroserverfield
    #instablog
    #updtablog
    numeropagamento = Column(Integer, autoincrement=True, primary_key=True)
    numeromovimento = Column(Integer,ForeignKey('movimentit.numeromovimento'))        
    movimentot = relation('Movimentit', backref='pagamenti')    
    numeroformapagamento = Column(Integer)
    importo = Column(Float)
    #pk  
    
class Movimentifid(DeclarativeBase):
    __tablename__ = 'movimentifid'
    #logicdelete
    sincrofield = Column(Integer, contasincrofield , autoincrement=True)
    #sincroserverfield
    #instablog
    #updtablog   
    numeromovimentofid = Column(Integer, contamovimentofid, autoincrement=True, primary_key=True) 
    elaborato = Column(Integer, default = 1)
    numeroazienda = Column(Integer)
    numerocampagnapremi = Column(Integer)
    numeroclientefid = Column(Integer, ForeignKey('clientifid.numeroclientefid'))
    clientefid = relation('Clientifid', backref='movimentifid') 
    codiceclientefid = Column(String(20))
    tipomovimentofid = Column(String(20))
    tipopunti = Column(String(1))
    datamovimento = Column(DateTime)
    dataregistrazione = Column(DateTime)
    movfid = Column(Integer)
    punti = Column(Integer)
    valore = Column(Float)
    numeromovimento = Column(Integer, default = 0)
    numeropuntipremio = Column(Integer, default = 0)
    numeroclientefidnew = Column(Integer, default = 0)
    codicecausalepunti = Column(String(4))

class Clientifid(DeclarativeBase):
    __tablename__ = 'clientifid'
    #logicdelete
    sincrofield = Column(Integer, contasincrofield , autoincrement=True, primary_key=True)
    #sincroserverfield
    #instablog
    #updtablog   
    numeroclientefid = Column(Integer, contaclientefid, autoincrement=True, primary_key=True) 
    numeroazienda = Column(Integer, default=1)
    numerogruppoclientefid = Column(Integer, default=1)
    codiceclientefid = Column(String(20), unique=True)
    cognome = Column(String(50))
    nome = Column(String(50))
    sesso = Column(String(1))
    indirizzo = Column(String(100))
    cap = Column(String(5))
    citta = Column(String(35))
    prov = Column(String(2))
    cfpiva = Column(String(16))
    cittanascita = Column(String(50))
    provnascita = Column(String(2))
    datanascita = Column(DateTime)
    tel = Column(String(30))
    cell = Column(String(30))
    email = Column(String(100))
    note = Column(String(500))
    #saldopunti
    attivo = Column(Integer, default=1)
    blacklist = Column(Integer)
    assegnato = Column(Integer, default=1)
    nucleofamiliare = Column(Integer)
    
    @property
    def punti(self):
        ret = 0
        for m in self.movimentifid:

            ret = ret + m.punti
        return ret

class Inventarit(DeclarativeBase):
    __tablename__='inventarit'
    sincrofield = Column(Integer, contasincrofield , autoincrement=True, primary_key=True)
    sincroserverfield = Column(Integer)
    numeroinventario = Column(Integer, containventario, autoincrement=True, primary_key=True)
    numeroazienda = Column(Integer, ForeignKey('provenienze.numeroprovenienza'))  
    azienda = relation('Provenienze')
    datainventario = Column(DateTime)
    numerodocumento = Column(Integer)
    anno = Column(Integer)
    numeromagazzino = Column(Integer,ForeignKey('magazzini.numeromagazzino'),     
                                    nullable=True)
    magazzino = relation('Magazzini') 
    descrizione = Column(String(255))   

    @classmethod
    def qta(cls, doc_id, prod_id):
        """"""
        try:
            ret = DBSession.query(Inventarirconta).filter(
                Inventarirconta.numeroinventario==doc_id,
                Inventarirconta.numeroprodotto==prod_id,                
                ).one()  
        except:
            ret = Inventarirconta()
            ret.numeroinventario=doc_id
            ret.numeroprodotto=prod_id
            ret.qta=0
            DBSession.add(ret)
        DBSession.flush()
        return ret

class Inventarir(DeclarativeBase):
    """
i=DBSession.query(Inventarit).filter_by(numeroinventario=14).one()

for p in ps:
    try:
        inv= DBSession.query(Inventarir).filter(and_(
            Inventarir.numeroinventario==14,
            Inventarir.numeroprodotto==p.numeroprodotto,
            Inventarir.numeroeanprodotto==p.numeroeanprodotto
            )).one()
    except:
        inv = Inventarir()
        inv.numeroinventario = 14
        inv.numeroprodotto=p.numeroprodotto
        inv.numeroeanprodotto=p.numeroeanprodotto
        DBSession.add(inv)
        DBSession.flush()
    """
    __tablename__='inventarir'
    sincrofield = Column(Integer, contasincrofield , autoincrement=True, primary_key=True)
    sincroserverfield = Column(Integer)
    numeroinventario = Column(Integer, ForeignKey('inventarit.numeroinventario')) 
    inventario = relation('Inventarit', backref='inventarir')
    numerorigainventario = Column(Integer, contarigainventario, autoincrement=True, primary_key=True)    
    
    numeroprodotto = Column(Integer, ForeignKey('prodotti.numeroprodotto'))    
    prodotto = relation('Prodotti')

    numeroeanprodotto = Column(Integer, ForeignKey('eanprodotti.numeroeanprodotto'))    
    eanprodotto = relation('Eanprodotti')    
    qta = Column(Float)    
    prezzo = Column(Float)
    """
    @property
    def cost(self):
        
        perms = set()
        for g in self.groups:
            perms = perms | set(g.permissions)
        return perms  
    """      



class Inventarirconta(DeclarativeBase):
    __tablename__='inventarirconta'
    sincrofield = Column(Integer, contasincrofield , autoincrement=True, primary_key=True)
    sincroserverfield = Column(Integer)
    numeroinventario = Column(Integer, ForeignKey('inventarit.numeroinventario')) 
    inventario = relation('Inventarit', backref='inventarirconta')
    numerorigainventarioconta = Column(Integer, contarigainventarioconta, autoincrement=True, primary_key=True)    
    
    numeroprodotto = Column(Integer, ForeignKey('prodotti.numeroprodotto'))    
    prodotto = relation('Prodotti')

    qta = Column(Float, default=0)  
    qtaconf = Column(Float, default=0)   
    conf = Column(Float, default=0) 
    costo = Column(Float, default=0)
    costo2 = Column(Float, default=0) 
    totale_qta = Column(Float, default=0)       
    totale_costo = Column(Float, default=0) 
    datacosto = Column(DateTime)    
    """
    @property
    def cost(self):
        
        perms = set()
        for g in self.groups:
            perms = perms | set(g.permissions)
        return perms  
    """  
    
class Aggiornaic(DeclarativeBase):
    __tablename__='aggiornaic'
    sincrofield = Column(Integer, contasincrofield , autoincrement=True, primary_key=True)
    sincroserverfield = Column(Integer)
    numeroinventario = Column(Integer, ForeignKey('inventarit.numeroinventario')) 
    inventario = relation('Inventarit', backref='aggiornaic')
    status = Column(Integer)         
    email = Column(Unicode(50))
    richiesta = Column(DateTime)
    fine = Column(DateTime)

# document final price
totale_costo = Inventarirconta.costo * Inventarirconta.totale_qta
totale_costo2 = Inventarirconta.costo2 * Inventarirconta.totale_qta

COSTI = [
        label('totale_costo', func.sum(totale_costo)),
        label('totale_costo2', func.sum(totale_costo2)),
        ]

class Alias(DeclarativeBase):
    __tablename__='alias'
    sincrofield = Column(Integer, contasincrofield , autoincrement=True)
    sincroserverfield = Column(Integer)
    numeroalias = Column(Integer, contaalias,  autoincrement=True,primary_key=True)    
    tipoprodotto = Column(Unicode(3), default=u'PRD') 
    numeroprodotto = Column(Integer, ForeignKey('prodotti.numeroprodotto'))
    prodotto = relation('Prodotti', backref='aliases')    
    numeroeanprodotto=Column(Integer, ForeignKey('eanprodotti.numeroeanprodotto'))
    eanprodotto = relation('Eanprodotti', backref='aliases')      
    alias = Column(Unicode(30))
       
class Inputb2b(DeclarativeBase):
    __tablename__='input_b2b'
    sincrofield = Column(Integer, contasincrofield , autoincrement=True)
    sincroserverfield = Column(Integer)
    b2b_id = Column(Integer, contab2b,  autoincrement=True,primary_key=True) 
    supplier_id = Column(Integer, ForeignKey(Provenienze.numeroprovenienza))  
    supplier = relation(Provenienze)
    supplier_code = Column(String(50))
    record = Column(String(50))    
    filename = Column(String(50))
    content = Column(BLOB)
    processed = Column(Integer, default = 0)
    booked = Column(Integer, default = 0) # to financial system
    exported = Column(Integer, default = 0) # to dbretail
    closed = Column(Integer, default=0)     
    acquired = Column(DateTime, default=datetime.now())
    updated = Column(DateTime, default = datetime.now())
    
class Tipologieprodotti(DeclarativeBase):
    __tablename__='tipologieprodotti'
    sincrofield = Column(Integer, contasincrofield , autoincrement=True)
    sincroserverfield = Column(Integer)
    numerotipologiaprodotto = Column(Integer, autoincrement=True,primary_key=True)        
    codicetipologiaprodotto = Column(Integer)    
    tipologiaprodotto = Column(Unicode(50)) 


class Produttori(DeclarativeBase):
    __tablename__='produttori'
    sincrofield = Column(Integer, contasincrofield , autoincrement=True)
    sincroserverfield = Column(Integer)
    numeroproduttore = Column(Integer, autoincrement=True,primary_key=True)           
    produttore = Column(Unicode(50))     
  



   
         
