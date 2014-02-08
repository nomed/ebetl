# -*- coding: utf-8 -*-
"""Main Controller"""

from ebetl.model import *
from itertools import groupby
try:
    from collections import OrderedDict
except:
    from ordereddict import OrderedDict
"""

from ebetl.model import *

DBSession.query(Prodotti).join(Inventarir).join(Inventarirconta).filter(Inventarir.numeroinventario==11).all()

"""

import logging
import os
import re
import sys
# logging.basicConfig(
#    level=logging.DEBUG)
log = logging.getLogger('ebetl.views')
from sqlalchemy.orm import aliased


def get_stock(id, *args, **kw):
    """
    """
    def level1(item):
        return (item[1], item[2])

    def level2(item):
        return item[1].reparto
    ret = None
    ret = DBSession.query(Inventarir, Prodotti,
                          Inventarirconta
                          )
    ret = ret.join(
        Prodotti, Inventarir.numeroprodotto == Prodotti.numeroprodotto)
    ret = ret.outerjoin(
        Inventarirconta, and_(
            Prodotti.numeroprodotto == Inventarirconta.numeroprodotto,
            Inventarirconta.numeroinventario == id))
    # ret = ret.join(Reparti, Prodotti.numeroreparto == Reparti.numeroreparto)
    ret = ret.filter(Inventarir.numeroinventario == id)
    # print ret
    ret = ret.order_by(Prodotti.numeroreparto, Prodotti.prodotto).all()

    ret = groupby(ret, level2)
    results = OrderedDict()
    for cat, products in ret:
        # prods = [x for x in products]
        results[cat] = OrderedDict()
        for prod, values in groupby(products, level1):
            results[cat][prod] = values
    return results


def get_stock_cogs(id, *args, **kw):
    """
    """
    def level1(item):
        return (item[1], item[0])

    def level2(item):
        return item[1].reparto
    ret = None
    ret = DBSession.query(Inventarirconta, Prodotti).filter(
        Inventarirconta.numeroinventario == id)
    ret = ret.outerjoin(
        Prodotti, and_(Prodotti.numeroprodotto == Inventarirconta.numeroprodotto))
    ret = ret.order_by(Prodotti.numeroreparto, Prodotti.prodotto).all()

    ret = groupby(ret, level2)
    results = OrderedDict()
    for cat, products in ret:
        # prods = [x for x in products]
        results[cat] = []
        for inv, prod in products:
            #
            results[cat].append((prod, inv))

    return results


def get_stock_report(id, *args, **kw):
    """
    """
    def level1(item):
        return (item[1], item[0])

    def level2(item):
        return item[1].reparto
    ret = None
    ret = DBSession.query(Inventarirconta, Prodotti).filter(
        Inventarirconta.numeroinventario == id)
    ret = ret.outerjoin(
        Prodotti, and_(Prodotti.numeroprodotto == Inventarirconta.numeroprodotto))
    ret = ret.order_by(Prodotti.numeroreparto, Prodotti.prodotto).all()

    ret = groupby(ret, level2)
    results = OrderedDict()
    for cat, products in ret:
        # prods = [x for x in products]
        results[cat] = []
        for inv, prod in products:
            #
            results[cat].append((prod, inv))

    return results


def get_pricelist(id, date=None, *args, **kw):
    """
    """

    if not date:
        date = datetime.now()

    def level1(item):
        return (item[1], item[2])

    def level2(item):
        return item[1].reparto
    ret = None
    ret = DBSession.query(Prodottiprovenienze, Prodotti,
                          Listiniprovenienze
                          )
    ret = ret.join(
        Prodotti, Prodottiprovenienze.numeroprodotto == Prodotti.numeroprodotto)
    ret = ret.outerjoin(Listiniprovenienze, and_(
        Listiniprovenienze.validodal <= date,
        Listiniprovenienze.validoal > date,
        Listiniprovenienze.numeroprovenienza == id,
        Listiniprovenienze.numeroprodottoprovenienza == Prodottiprovenienze.numeroprodottoprovenienza))
    # ret = ret.join(Reparti, Prodotti.numeroreparto == Reparti.numeroreparto)
    ret = ret.filter(and_(Prodottiprovenienze.numeroprovenienza == id,
                          # Prodottiprovenienze.codiceprodottoprovenienza=='588626'
                          )
                     ).order_by(Prodottiprovenienze.codiceprodottoprovenienza)

    ret = ret.all()

    return ret


def get_pricelist_todict(plist_obj, prov):
    """
    Get pricelist by supplier_code
    """

    pricelist = {}
    for p in plist_obj:
        ret_tmp = {}
        ret_tmp[
            'prodottiprovenienze.numeroprovenienza'] = prov.numeroprovenienza

        for obj in p:
            newobjs = [obj]
            if hasattr(obj, '__tablename__'):
                if obj.__tablename__ == 'prodotti':
                    if obj.reparto:
                        newobjs.append(obj.reparto)
                    if obj.iva:
                        newobjs.append(obj.iva)
                    if obj.reparto.contocosto:
                        newobjs.append(obj.reparto.contocosto)
                elif obj.__tablename__ == 'prodottiprovenienze':
                    if obj.ean:
                        newobjs.append(obj.ean)
                for pobj in newobjs:
                    prefix = pobj.__tablename__
                    for key, val in pobj.__dict__.iteritems():
                        if not key.startswith('_'):
                            ret_tmp["%s.%s" % (prefix, key)] = val

        pricelist[
            ret_tmp['prodottiprovenienze.codiceprodottoprovenienza']] = ret_tmp
        # sys.exit()
    return pricelist


def get_latest_cogs(prod_id, cost_center_id=None, date=None):
    if not date:
        date = datetime.now()

    if cost_center_id:
        andclause = [
            Movimentir.numeromagazzino == cost_center_id
        ]
    else:
        andclause = []
    andclause = andclause + [
        Movimentir.codiceqta == 'CARICO',
        Movimentit.datadocumento <= date,
        # Movimentir.idprodotto==prod_id,
        Movimentir.idprodotto == prod_id,
        Movimentit.numeromovimento >= 0,
        Movimentit.numeroazienda >= 0,
        Movimentit.tipodocumento == 'CAR',
        Movimentir.numerorigamovimento >= 0,
        Movimentir.numeromovimento >= 0]
    ret_query = DBSession.query(
        Movimentir, Movimentit).order_by(Movimentit.datadocumento.desc()).filter(and_(**andclause)).join(Movimentit,
                                                                                                         Movimentir.numeromovimento == Movimentit.numeromovimento
                                                                                                         ).limit(1)

    ret = ret_query.first()
    if ret:
        mov, doc = ret
    else:
        mov = None
    latest_cost = 0
    cost_date = None
    if mov:
        if mov.prezzo:
            latest_cost = mov.prezzo
            cost_date = mov.movimento.datadocumento

    if latest_cost == 0:
        if mov:
            if mov.prodotto:
                latest_cost = mov.prodotto.costonetto
                cost_date = mov.prodotto.dataultimocosto
    return latest_cost, cost_date


def get_latest_fact_cogs(DBSession, prod_id, cost_center_id, date=None):
    if not date:
        date = datetime.now()

    ret_query = DBSession.query(Factcogs).filter(and_(
        Factcogs.cost_center_id == cost_center_id,
        Factcogs.doc_date <= date,
        Factcogs.prod_id == prod_id,
    )).order_by(Factcogs.doc_date.desc())
    cost = ret_query.first()
    if cost:
        return float(0) or cost.cost
    else:
        return float(0)


def get_mov(id, *args, **kw):
    """
    >>> codmov=['FACFOR', 'FATFOR']

    """

    from pprint import pprint

    # contiricavo = aliased(Conticontabilita)

    tables = (
        Movimentit,
        Movimentir,
        Magazzini,
        Conticontabilita,
        Iva,
        Reparti,
        Prodotti,
        Eanprodotti,
        Prodottiprovenienze,
        Listiniprovenienze
    )
    columns = []
    query_args = []
    for m in tables:
        for c in m.__table__.columns:
                if not c in columns:
                    columns.append("%s" % (c))
                    query_args.append(c)

    movst = DBSession.query(*query_args)  # , Prodotti, Eanprodotti, )
    movst = movst.filter(Movimentit.numeromovimento == id)

    # movimentir
    movst = movst.join(Movimentir, and_(
        Movimentit.numeromovimento == Movimentir.numeromovimento,
        Movimentir.tipoprodotto != "NIL")
    )

    # magazzini
    movst = movst.outerjoin(
        Magazzini, Magazzini.numeromagazzino == Movimentir.numeromagazzino)

    # conticosto
    movst = movst.outerjoin(Conticontabilita,
                            Conticontabilita.numerocontocontabilita == Movimentir.numerocontocontabilita)
    # iva
    movst = movst.outerjoin(Iva,
                            Iva.numeroiva == Movimentir.numeroiva)
    # reparti
    movst = movst.outerjoin(
        Reparti, Reparti.numeroreparto == Movimentir.numeroreparto)
    # prodotti
    movst = movst.outerjoin(
        Prodotti, Prodotti.numeroprodotto == Movimentir.idprodotto)
    # eanprodotti
    movst = movst.outerjoin(Eanprodotti,
                            Eanprodotti.numeroeanprodotto == Movimentir.numeroeanprodotto)
    # prodottiprovenienza
    movst = movst.outerjoin(Prodottiprovenienze,
                            and_(
                            Prodottiprovenienze.numeroeanprodotto == Movimentir.numeroeanprodotto,

                            Prodottiprovenienze.numeroprovenienza == Movimentit.numeroprovenienza,
                            Prodottiprovenienze.codiceprodottoprovenienza == Movimentir.codice)
                            )
    # listiniprovenienza

    movst = movst.outerjoin(Listiniprovenienze,
                            and_(
                            Listiniprovenienze.validodal <= Movimentit.datadocumento,
                            Listiniprovenienze.validoal > Movimentit.datadocumento,
                            Listiniprovenienze.numeroprovenienza == Movimentit.numeroprovenienza,
                            Listiniprovenienze.numeroprodottoprovenienza == Prodottiprovenienze.numeroprodottoprovenienza,
                            )
                            )

    movst = movst.order_by(Movimentit.datadocumento)

    movst = movst.all()

    ret = [dict(zip(columns, i)) for i in movst]
    return ret

import transaction
from prettytable import PrettyTable
from prettytable import NONE
from tg import config
from sqlalchemy import create_engine, MetaData, Table, and_, Float, select, func
from sqlalchemy.orm import sessionmaker, relationship , joinedload
from sqlalchemy.ext.declarative import declarative_base

class Syncobj(object):

    def __init__(self, config):
        self.config = config
        self.dest = config.get('lilliput.dburl')

        #log.debug("^^^^^^   END_SMETA.REFLECT")
        #log.debug("^^^^^^ START_SMETA.DEST")
        self.destination, self.dengine = self.make_session(self.dest)
        self.dmeta = MetaData(bind=self.dengine)
        self.dmeta.reflect(self.dengine)

    def make_session(self,connection_string):

        #log.debug('')
        #log.debug('^^^^^^ START_MAKE_SESSION')

        if connection_string.startswith('firebird'):
            engine = create_engine(connection_string, echo=False,
                                   convert_unicode=False)
        else:
            engine = create_engine(connection_string, echo=False,
                                   convert_unicode=True)
        Session = sessionmaker(bind=engine)
        #log.debug('')
        #log.debug('^^^^^^ END_MAKE_SESSION')
        return Session(), engine

    def quick_mapper(self,table):
        #log.debug('')
        #log.debug('^^^^^^ START_QUICK_MAPPER')
        Base = declarative_base()
        class GenericMapper(Base):
            __table__ = table
        #log.debug('')
        #log.debug('^^^^^^ END_QUICK_MAPPER')
        return GenericMapper



def get_dailytotals(fromd, tod, *args, **kw):

    # document final price
    # vat_total = Factb2b.b2b_net_total * Factb2b.b2b_vat_code/100
    # gross_total = Factb2b.b2b_net_total + vat_total
    # pricelist final price
    # lis_fp =  Factb2b.supplier_item_discount*Factb2b.supplier_item_unit_price
    # contract total
    # lis_ct = lis_fp * Factb2b.b2b_uom_qty
    # b2b_fp = Factb2b.b2b_unit_price*Factb2b.b2b_di
    syncobj = Syncobj(config)
    Base = declarative_base()
    Base.metadata.reflect(syncobj.dengine)
    class Report(Base):
        __tablename__ = 'micros_report'
        __table_args__ = (
            {'autoload':True}
            )
    class Location(Base):
        __tablename__ = 'dim_location'
        __table_args__ = (
            {'autoload':True}
            )


    fltr = [

        Movimentit.tipoprovenienza == 'POS',
        Movimentit.codicemovimento == 'VENDITA',
        Movimentit.tipodocumento == 'VEN',
        Movimentit.datamovimento >= fromd,
        Movimentit.datamovimento < tod,


    ]
    """
    groupby = [Gruppipos.numerogruppopos, Gruppipos.gruppopos,
               Movimentir.numeroreparto, Reparti.reparto]
    query_lst = groupby + [
        # func.count(distinct(Movimentit.numeromovimento)),
        # func.sum(Movimentir.totale)/func.count(distinct(Movimentit.numeromovimento)),
        func.sum(Movimentir.totalenetto),
        func.sum(Movimentir.ivatotale),
        func.sum(Movimentir.totale),
    ]


    ret = DBSession.query(*query_lst)
    ret = ret.group_by(*groupby)
    ret = ret.join(Pos, Gruppipos.numerogruppopos == Pos.numerogruppopos)
    ret = ret.join(Pos, Gruppipos.numeromagazzino == Magazzini.numeromagazzino)
    ret = ret.join(Ricevutet, Pos.numeropos == Ricevutet.numeropos)
    ret = ret.join(
        Movimentit, Ricevutet.numeromovimento == Movimentit.numeromovimento)
    ret = ret.join(
        Movimentir, Movimentir.numeromovimento == Movimentit.numeromovimento)
    ret = ret.outerjoin(
        Reparti, Movimentir.numeroreparto == Reparti.numeroreparto)
    ret = ret.filter(and_(*fltr))
    #ret = ret.all()
    x = PrettyTable(
        ["pos_num", "pdv", "rep_num", "rep", "net_total", "vat_total", "gross_total"])

    #for r in ret:
    #    x.add_row(r)
    #print x
    """
    groupby = [

        Magazzini.codicemagazzino,
        func.extract('year',Movimentit.datamovimento),
        func.extract('month',Movimentit.datamovimento),
        func.extract('day', Movimentit.datamovimento),
        ]
    query_lst = groupby + [

        func.count(distinct(Movimentit.numeromovimento)),
        func.sum(Movimentir.totale) / func.count(
            distinct(Movimentit.numeromovimento)),
        func.sum(Movimentir.totalenetto),
        func.sum(Movimentir.ivatotale),
        func.sum(Movimentir.totale)
    ]

    ret = DBSession.query(*query_lst)
    ret = ret.group_by(*groupby)
    ret = ret.join(Gruppipos, Gruppipos.numeromagazzino == Magazzini.numeromagazzino)
    ret = ret.join(Pos, Gruppipos.numerogruppopos == Pos.numerogruppopos)
    ret = ret.join(Ricevutet, Pos.numeropos == Ricevutet.numeropos)
    ret = ret.join(
        Movimentit, Ricevutet.numeromovimento == Movimentit.numeromovimento)
    ret = ret.join(
        Movimentir, Movimentir.numeromovimento == Movimentit.numeromovimento)

    ret = ret.filter(and_(*fltr))
    ret = ret.all()
    headers = ["location_stock","year","month","day", "checks", "sph", "net_total", "vat_total", "gross_total"]

    x = PrettyTable(
        ["location_stock","year","month","day", "checks", "sph", "net_total", "vat_total", "gross_total"])
    results = []
    for r in ret:
        jdict = dict(zip(headers, r))
        location_stock = jdict.get('location_stock')
        locobj = syncobj.destination.query(Location).filter_by(
                      location_stock=location_stock).one()
        team_id = locobj.location_id
        year = jdict.get('year')
        month = jdict.get('month')
        day = jdict.get('day')
        try:
            report = syncobj.destination.query(Report).filter(and_(
                      Report.team_id==team_id,
                      Report.year==year,
                      Report.month==month,
                      Report.day==day)).one()
            print report
            for k,v in jdict.iteritems():
                if hasattr(report, k):
                    setattr(report,k,v)
            syncobj.destination.add(report)
            syncobj.destination.flush()
        except:
            pass
        x.add_row(r)
    transaction.commit()
    x.float_format = "8.2"
    x.align = "r"
    x.align['location_stock'] = "l"
    x.header=False
    x.hrules = NONE
    print x

    return ret
