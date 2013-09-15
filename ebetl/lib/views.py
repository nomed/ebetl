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
logging.basicConfig(
    level=logging.DEBUG)
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
    print ret
    ret = ret.order_by(Prodotti.numeroreparto, Prodotti.prodotto).all() 
    
    ret = groupby(ret, level2) 
    results = OrderedDict()
    for cat, products in ret:
        #prods = [x for x in products]
        results[cat] = OrderedDict()
        for prod, values in groupby(products, level1):
            results[cat][prod] = values
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
    ret = ret.filter(Prodottiprovenienze.numeroprovenienza==id)
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
                    print pobj
                    prefix = pobj.__tablename__                    
                    for key, val in pobj.__dict__.iteritems():
                        if not key.startswith('_'):
                            ret_tmp["%s.%s"%(prefix, key)] = val               
 
        pricelist[ret_tmp['prodottiprovenienze.codiceprodottoprovenienza']]=ret_tmp
        #sys.exit() 
    return pricelist
    
def get_latest_cogs(prod_id, cost_center_id, date=None):
    if not date:
        date=datetime.now()
        
    ret_query = DBSession.query(Movimentir,Movimentit).filter(and_(
        Movimentir.numeromagazzino==cost_center_id,
        Movimentir.codiceqta=='CARICO',
        Movimentit.datadocumento<=date,  
        Movimentir.idprodotto==prod_id,             
        )).join(Movimentit, 
            Movimentir.numeromovimento == Movimentit.numeromovimento
         ).order_by(Movimentit.datadocumento)
    print ret_query
    
    ret = ret_query.first()
    if ret:
        mov, doc = ret
    else:
        mov = None
    if mov:
        return float(0) or mov.prezzo
    else:
        return float(0)

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

