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

import logging, os, re, sys
#logging.basicConfig(
#    level=logging.DEBUG)
log = logging.getLogger('ebetl.views')
from sqlalchemy.orm import aliased

def get_stock(id, *args, **kw):
    """
    """
    def level1( item ):
        return (item[1], item[2])
    def level2( item ):
        return item[1].reparto
    ret = None
    ret = DBSession.query(Inventarir, Prodotti,
                            Inventarirconta
                            )
    ret = ret.join(Prodotti, Inventarir.numeroprodotto == Prodotti.numeroprodotto)
    ret = ret.outerjoin(Inventarirconta, and_(Prodotti.numeroprodotto == Inventarirconta.numeroprodotto,
                                        Inventarirconta.numeroinventario==id) )
    #ret = ret.join(Reparti, Prodotti.numeroreparto == Reparti.numeroreparto)
    ret = ret.filter(Inventarir.numeroinventario==id)
    #print ret
    ret = ret.order_by(Prodotti.numeroreparto, Prodotti.prodotto).all()

    ret = groupby(ret, level2)
    results = OrderedDict()
    for cat, products in ret:
        #prods = [x for x in products]
        results[cat] = OrderedDict()
        for prod, values in groupby(products, level1):
            results[cat][prod] = values
    return results



def get_stock_cogs(id, *args, **kw):
    """
    """
    def level1( item ):
        return (item[1], item[0])
    def level2( item ):
        return item[1].reparto
    ret = None
    ret = DBSession.query(Inventarirconta, Prodotti).filter(Inventarirconta.numeroinventario==id)
    ret = ret.outerjoin(Prodotti, and_(Prodotti.numeroprodotto == Inventarirconta.numeroprodotto))
    ret = ret.order_by(Prodotti.numeroreparto, Prodotti.prodotto).all()

    ret = groupby(ret, level2)
    results = OrderedDict()
    for cat, products in ret:
        #prods = [x for x in products]
        results[cat] = []
        for inv,prod in products:
            #
            results[cat].append((prod,inv))

    return results

def get_stock_report(id, *args, **kw):
    """
    """
    def level1( item ):
        return (item[1], item[0])
    def level2( item ):
        return item[1].reparto
    ret = None
    ret = DBSession.query(Inventarirconta, Prodotti).filter(Inventarirconta.numeroinventario==id)
    ret = ret.outerjoin(Prodotti, and_(Prodotti.numeroprodotto == Inventarirconta.numeroprodotto))
    ret = ret.order_by(Prodotti.numeroreparto, Prodotti.prodotto).all()

    ret = groupby(ret, level2)
    results = OrderedDict()
    for cat, products in ret:
        #prods = [x for x in products]
        results[cat] = []
        for inv,prod in products:
            #
            results[cat].append((prod,inv))

    return results

def get_pricelist(id, date=None, *args, **kw):
    """
    """

    if not date:
        date=datetime.now()
    def level1( item ):
        return (item[1], item[2])
    def level2( item ):
        return item[1].reparto
    ret = None
    ret = DBSession.query(Prodottiprovenienze, Prodotti,
                            Listiniprovenienze
                            )
    ret = ret.join(Prodotti, Prodottiprovenienze.numeroprodotto == Prodotti.numeroprodotto)
    ret = ret.outerjoin(Listiniprovenienze, and_(
                    Listiniprovenienze.validodal <= date,
                    Listiniprovenienze.validoal > date,
                    Listiniprovenienze.numeroprovenienza == id,
                    Listiniprovenienze.numeroprodottoprovenienza == Prodottiprovenienze.numeroprodottoprovenienza) )
    #ret = ret.join(Reparti, Prodotti.numeroreparto == Reparti.numeroreparto)
    ret = ret.filter(and_(Prodottiprovenienze.numeroprovenienza==id,
                            #Prodottiprovenienze.codiceprodottoprovenienza=='588626'
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
        ret_tmp['prodottiprovenienze.numeroprovenienza'] = prov.numeroprovenienza

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
                            ret_tmp["%s.%s"%(prefix, key)] = val

        pricelist[ret_tmp['prodottiprovenienze.codiceprodottoprovenienza']]=ret_tmp
        #sys.exit()
    return pricelist

def get_latest_cogs(prod_id, cost_center_id=None, date=None):
    if not date:
        date=datetime.now()

    if cost_center_id:
        andclause = [
        Movimentir.numeromagazzino==cost_center_id
        ]
    else:
        andclause = []
    andclause = andclause + [
        Movimentir.codiceqta=='CARICO',
        Movimentit.datadocumento<=date,
        #Movimentir.idprodotto==prod_id,
        Movimentir.idprodotto==prod_id,
        Movimentit.numeromovimento>=0,
        Movimentit.numeroazienda>=0,
        Movimentit.tipodocumento=='CAR',
        Movimentir.numerorigamovimento>=0,
        Movimentir.numeromovimento>=0]
    ret_query = DBSession.query(Movimentir,Movimentit).order_by(Movimentit.datadocumento.desc()).filter(and_(*andclause)).join(Movimentit,
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
        date=datetime.now()

    ret_query = DBSession.query(Factcogs).filter(and_(
        Factcogs.cost_center_id==cost_center_id,
        Factcogs.doc_date<=date,
        Factcogs.prod_id==prod_id,
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

    #contiricavo = aliased(Conticontabilita)

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
                    columns.append("%s"%(c))
                    query_args.append(c)


    movst = DBSession.query(*query_args)#, Prodotti, Eanprodotti, )
    movst = movst.filter(Movimentit.numeromovimento==id)


    # movimentir
    movst = movst.join(Movimentir,and_(
                Movimentit.numeromovimento == Movimentir.numeromovimento,
                Movimentir.tipoprodotto!="NIL")
                )

    # magazzini
    movst = movst.outerjoin(Magazzini, Magazzini.numeromagazzino == Movimentir.numeromagazzino)

    # conticosto
    movst = movst.outerjoin(Conticontabilita,
            Conticontabilita.numerocontocontabilita==Movimentir.numerocontocontabilita)
    # iva
    movst = movst.outerjoin(Iva,
            Iva.numeroiva==Movimentir.numeroiva)
    # reparti
    movst = movst.outerjoin(Reparti, Reparti.numeroreparto==Movimentir.numeroreparto)
    # prodotti
    movst = movst.outerjoin(Prodotti, Prodotti.numeroprodotto==Movimentir.idprodotto)
    # eanprodotti
    movst = movst.outerjoin(Eanprodotti,
            Eanprodotti.numeroeanprodotto==Movimentir.numeroeanprodotto)
    # prodottiprovenienza
    movst = movst.outerjoin(Prodottiprovenienze,
            and_(Prodottiprovenienze.numeroeanprodotto==Movimentir.numeroeanprodotto,

                 Prodottiprovenienze.numeroprovenienza==Movimentit.numeroprovenienza,
                 Prodottiprovenienze.codiceprodottoprovenienza==Movimentir.codice )
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


<<<<<<< HEAD
def sync_do(lines, *args, **kw):
    syncobj = Syncobj(config)
    Base = declarative_base()
    Base.metadata.reflect(syncobj.dengine)
    class Report(Base):
        __tablename__ = 'fact_do'
        __table_args__ = (
            {'autoload':True}
            )
    class Location(Base):
        __tablename__ = 'dim_location'
        __table_args__ = (
            {'autoload':True}
            )
    class FiscalReport(Base):
        __tablename__ = 'micros_report'
        __table_args__ = (
            {'autoload':True}
            )
    class CashReport(Base):
        __tablename__ = 'micros_cash_report'
        __table_args__ = (
            {'autoload':True}
            )
    class VatReport(Base):
        __tablename__ = 'micros_vatfee'
        __table_args__ = (
            {'autoload':True}
            )            
    for r in lines:
        jdict = dict(zip(DOKEYS_ALL, r))
        #000352|2014|2|6|214|11,7844392523|2303,0197|218,8503|2521,87|159|14,0885534591|2053,9432|186,1368|2240,08
        location_code = jdict.get('location_code')
        
        locobj = syncobj.destination.query(Location).filter_by(
                      location_code=location_code).one()
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
        except:
            report = Report(
                      team_id=team_id,
                      year=year,
                      month=month,
                      day=day,
                      date=datetime(year,month,day),
                      #acquired=0,
                      #validated=0,
                      #published=0,
                      budget=0
                      )
        
             
        if not report.report_id:
            fltr = [
                FiscalReport.team_id == team_id,
                FiscalReport.year == year,
                FiscalReport.month == month,
                FiscalReport.day == day,
                FiscalReport.acquired == 1,
                ]
            groupby = [
                FiscalReport.report_id,               
                FiscalReport.team_id,
                FiscalReport.year,
                FiscalReport.month,
                FiscalReport.day,
                ] 
            query_lst = groupby + [
                func.sum(VatReport.amount),#'total',
                func.sum(VatReport.amount/(1+VatReport.vat_amount/100)),#'net_total',
                func.sum(VatReport.amount-VatReport.amount/(1+VatReport.vat_amount/100)),#'vat_total',
            ]    

            ret_fisc = syncobj.destination.query(*query_lst)
            ret_fisc = ret_fisc.group_by(*groupby)
            ret_fisc = ret_fisc.join(CashReport, CashReport.report_id == FiscalReport.report_id)
            ret_fisc = ret_fisc.join(VatReport, VatReport.cash_report_id == CashReport.cash_report_id)
            ret_fisc = ret_fisc.filter(and_(*fltr))   
     
            ret_fisc = ret_fisc.all()

            if ret_fisc:
                jdict['report_id']=ret_fisc[0][0]                
                jdict['fisc_total']=ret_fisc[0][5]
                jdict['fisc_net_total']=ret_fisc[0][6]                            
                jdict['fisc_vat_total']=ret_fisc[0][7]  
            for k,v in jdict.iteritems():
                if hasattr(report, k):
                    setattr(report,k,v)                  
            syncobj.destination.add(report)
            syncobj.destination.flush()
    transaction.commit()
    #x.float_format = "8.2"
    #x.align = "r"
    #x.align['location_stock'] = "l"
    #x.header=False
    #x.hrules = NONE
    #print x

def sync_lilliput(*args, **kw):
    syncobj = Syncobj(config)
    Base = declarative_base()
    Base.metadata.reflect(syncobj.dengine)
    class Report(Base):
        __tablename__ = 'fact_do'
        __table_args__ = (
            {'autoload':True}
            )
    class Location(Base):
        __tablename__ = 'dim_location'
        __table_args__ = (
            {'autoload':True}
            )
    class FiscalReport(Base):
        __tablename__ = 'micros_report'
        __table_args__ = (
            {'autoload':True}
            )
    class CashReport(Base):
        __tablename__ = 'micros_cash_report'
        __table_args__ = (
            {'autoload':True}
            )
    class VatReport(Base):
        __tablename__ = 'micros_vatfee'
        __table_args__ = (
            {'autoload':True}
            )

    reports = syncobj.destination.query(Report).filter(and_(Report.report_id==None)).all()
    for report in reports:
        if not report.report_id:
            fltr = [
                FiscalReport.team_id == report.team_id,
                FiscalReport.year == report.year,
                FiscalReport.month == report.month,
                FiscalReport.day == report.day,
                FiscalReport.acquired == 1,
                ]
            groupby = [
                FiscalReport.report_id,               
                FiscalReport.team_id,
                FiscalReport.year,
                FiscalReport.month,
                FiscalReport.day,
                ] 
            query_lst = groupby + [
                func.sum(VatReport.amount),#'total',
                func.sum(VatReport.amount/(1+VatReport.vat_amount/100)),#'net_total',
                func.sum(VatReport.amount-VatReport.amount/(1+VatReport.vat_amount/100)),#'vat_total',
            ]    

            ret_fisc = syncobj.destination.query(*query_lst)
            ret_fisc = ret_fisc.group_by(*groupby)
            ret_fisc = ret_fisc.join(CashReport, CashReport.report_id == FiscalReport.report_id)
            ret_fisc = ret_fisc.join(VatReport, VatReport.cash_report_id == CashReport.cash_report_id)
            ret_fisc = ret_fisc.filter(and_(*fltr))   
     
            ret_fisc = ret_fisc.all()
            jdict = {}
            if ret_fisc:
                jdict['report_id']=ret_fisc[0][0]                
                jdict['fisc_total']=ret_fisc[0][5]
                jdict['fisc_net_total']=ret_fisc[0][6]                            
                jdict['fisc_vat_total']=ret_fisc[0][7]  
            for k,v in jdict.iteritems():
                if hasattr(report, k):
                    setattr(report,k,v)                  
            syncobj.destination.add(report)
            syncobj.destination.flush()
    transaction.commit()


def print_fact_dmi(location_code, fromd, tod, *args, **kw):
    syncobj = Syncobj(config)
    Base = declarative_base()
    Base.metadata.reflect(syncobj.dengine)
    class Report(Base):
        __tablename__ = 'fact_dmi'
        __table_args__ = (
            {'autoload':True}
            )
    class Location(Base):
        __tablename__ = 'dim_location'
        __table_args__ = (
            {'autoload':True}
            )
    print fromd, tod
    fltr = [

        Report.date >= fromd,
        Report.date < tod,
        Report.location_code==location_code,

    ]
    groupby = [
        
    Report.major_group_label    
    ]
    query_lst = groupby + [
        func.sum(Report.total),
        func.sum(Report.total_ly),        
        func.sum(Report.total-Report.total_ly),
    ]
    ret = syncobj.destination.query(*query_lst)
    ret = ret.group_by(*groupby)
    ret = ret.filter(and_(*fltr))   
 
    ret = ret.all()    

    fltr = [

        Report.date >= fromd,
        Report.date < tod,
        Report.location_code==location_code,

    ]
    groupby = [ 
    ]
    query_lst = groupby + [
        func.sum(Report.total),
        func.sum(Report.total_ly),        
        func.sum(Report.total-Report.total_ly),
    ]
    ret2 = syncobj.destination.query(*query_lst)
    ret2 = ret2.group_by(*groupby)
    ret2 = ret2.filter(and_(*fltr))   
 
    ret2 = ret2.all()       

    return ret , ret2                      
=======
>>>>>>> 46f9b2704206f6931d790dd63c60764e3c391bf7
