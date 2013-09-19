# -*- coding: utf-8 -*-
"""


"""
import glob, json

import logging, os, re, sys
logging.basicConfig(
    level=logging.DEBUG)
log = logging.getLogger('b2b')

from ebetl.lib.etl import get_txn
from ebetl.model import *
from ebetl.model.dbretail import Inputb2b
from ebetl.model.zerobi import Factb2b, FACT_B2B, FACT_B2B_PRICE
import transaction 

from sqlalchemy import and_
from ebetl.lib.views import get_mov
from ebetl.lib.etl import Mapper
from ebetl.lib import strip_non_ascii

from itertools import groupby
from pprint import pprint

    

mapper = Mapper()

class B2bObj(object):
    """
    dbretail.path_input = %(here)s/archive/input/b2b
    dbretail.notfound = 1601000000    
    """

    def __init__(self, config,record='dbretail', *args, **kw):
        """
        """
        self.record = record
        self.config=config   
        self.movcode = config.get("%s.movcode"%(self.record))
        if self.movcode:
            self.movcode = [c.strip() for c in self.movcode.split(',')]
                          
        self.path = config.get(record+'.path_input')
        self.path_jsonmap = os.path.join(
                        self.path,
                        'mappers', "%s_target.json"%record
                        )
        jsonf = open(self.path_jsonmap , "r" )  
        self.jsonmap = json.load(jsonf)
        jsonf.close()      
        
        self.notfound=self.config.get("%s.notfound"%(self.record))    

    def _get_files(self, *args, **kw):
        orlist = []
        for c in self.movcode:
            orlist.append(Movimentit.codicemovimento==c) 
        ret = DBSession.query(Movimentit).filter(Movimentit.controllonote==10)
        ret = ret.filter(or_(*orlist))
        ret = ret.order_by(Movimentit.datadocumento)
        
        return ret.all()

    def _datagrid(self, query_lst , groupby, fltr):
        ret = DBSession.query(*query_lst)
        ret = ret.group_by(*groupby).filter(and_(*fltr))
        return ret.all()

    def export(self, *args, **kw):
        """
        Export inputb2b to dbretail
        
        Factb2b.b2b_id == Movimentir.instablog
        Factb2b.instablog == Movimentit.numeromovimento
        Factb2b.updtablog == Movimentir.numeromovimento
        
        """   
        # get files to process
        files = DBSession.query(Inputb2b).filter(
            and_(Inputb2b.export==1,or_(Inputb2b.exported==0, Inputb2b.exported==None))).all()
        vat = {}  
        log.info("export : found %s to process"%(len(files)))           
        for i in files:
            # STEP 1
        
            _logprefix1 = "export: %s "%(i.b2b_id)
            
            log.debug(_logprefix1+"- start processing")
            
            # fetch input_b2b.b2b_id
            groupby = [Provenienze, Factb2b.rec_num, Factb2b.rec_date]
            query_lst = groupby + FACT_B2B
            fltr = [Factb2b.inputb2b_id==i.b2b_id,
                    Factb2b.supplier_id==Provenienze.numeroprovenienza
                     ] 
            recs = self._datagrid(query_lst, groupby, fltr)
            
            log.debug(_logprefix1+ '- found %s recs to process'%(len(recs)))
            
            # fetch all recs from fact_b2b for b2b_id and supplier_id
            recsvat = []
            
            # STEP 2

            for rec in recs:
                
                rech =  DBSession.query(Movimentit)
                rech = rech.filter(and_(
                    Movimentit.numerodocumento == rec[1],
                    Movimentit.datadocumento == rec[2],
                    Movimentit.numeroprovenienza == rec[0].numeroprovenienza
                    )
                )
                try:
                    rechobj = rech.one() 
                except:
                    #raise
                    rechobj = Movimentit()
                    rechobj.numerodocumento = rec[1]
                    rechobj.datadocumento = rec[2]
                    rechobj.numeroprovenienza = rec[0].numeroprovenienza
                    rechobj.numerocodicemovimento = 7
                    rechobj.codicemovimento = 'CARICO'
                    rechobj.clifor = 'F'
                    rechobj.ingressouscita = 'I'
                    rechobj.tipodocumento = 'CAR'
                    rechobj.numeroazienda = 1
                    rechobj.datamovimento = rec[2]
                    rechobj.tipoprovenienza = 'FOR'

                rechobj.ragionesociale = rec[0].provenienza
                rechobj.partitaiva = rec[0].partitaiva
                rechobj.codicefiscale = rec[0].codicefiscale  
                rechobj.indirizzo = rec[0].indirizzo
                rechobj.cap = rec[0].cap
                rechobj.prov = rec[0].prov
                rechobj.citta = rec[0].citta               
                rechobj.totaleimponibile = rec[4]
                rechobj.totaleiva = rec[5]
                rechobj.totaledocumento = rec[6]
                rechobj.sincrofield = DBSession.execute(contasincrofield)
                
                DBSession.add(rechobj)
                DBSession.flush()
                
                _logprefix2 = _logprefix1 + "- rech %s (%s) "%(
                                    rechobj.numeromovimento,
                                    rechobj.numerodocumento)
                
                log.debug(_logprefix2+ "- created")
                
                if not rechobj.numeromovimento in recsvat:
                    # Vat
                    groupby = [Factb2b.rec_num, Factb2b.b2b_vat_code]
                    query_lst = groupby + FACT_B2B
                    fltr = fltr = [Factb2b.inputb2b_id==i.b2b_id,
                        Factb2b.supplier_id==Provenienze.numeroprovenienza,
                        Factb2b.rec_num == rec[1]
                         ] 
                
                    vat_movs = self._datagrid(query_lst, groupby, fltr) 
                    for v in vat_movs:
                        
                        if not v[1] in vat:
                            vcode = str(v[1]).zfill(2)
                            vobj = DBSession.query(Iva).filter_by(codiceiva=vcode).one()
                            
                            vat[v[1]] = vobj                                        
                        
                        try:
                            vatmovobj = DBSession.query(Movimentiiva).filter(and_(
                                Movimentiiva.numeromovimento == rechobj.numeromovimento,
                                Movimentiiva.numeroiva == vat[v[1]].numeroiva
                                        )).one()
                        except:
                            vatmovobj = Movimentiiva()
                            vatmovobj.numeromovimento = rechobj.numeromovimento
                            vatmovobj.numeroiva = vat[v[1]].numeroiva
                        vatmovobj.totaleimponibile = v[3]
                        vatmovobj.totaleiva = v[4]
                        vatmovobj.sincrofield = DBSession.execute(contasincrofield)
                        DBSession.add(vatmovobj)
                        
                        log.debug(_logprefix2+ "- added mov for vat id %s"%(
                                vatmovobj.numeroiva
                        ))
                        
                    recsvat.append(rechobj.numeromovimento)
                    
                    
                        
             
             
                rec_rows = DBSession.query(Factb2b).filter(
                            and_(
                                Factb2b.inputb2b_id==i.b2b_id,
                                Factb2b.supplier_id==rechobj.numeroprovenienza,
                                Factb2b.rec_date==rechobj.datadocumento,
                                Factb2b.rec_num==rechobj.numerodocumento,
                            
                            )
                                ).all()
                
                log.debug(_logprefix2+"- found %s rows to process"%(len(rec_rows)))
                
                # STEP 3                                               
                for r in rec_rows:
                    
                    _logprefix3 = _logprefix2
                    
                    try:
                        recrobj = DBSession.query(Movimentir).filter_by(
                                    instablog = r.b2b_id
                                        ).one()
                    except:
                        recrobj = Movimentir()
                        recrobj.instablog = r.b2b_id
                    recrobj.datamovimento = r.rec_date
                    recrobj.dataregistrazione = r.rec_date
                    recrobj.movqta = 1
                    recrobj.movval = 0
                    recrobj.tiporiga = 'P'
                    recrobj.codice = r.supplier_item_code  
                    recrobj.descrizione = r.b2b_desc
                    recrobj.tipoprodotto = 'PRD'
                    recrobj.idprodotto = r.item_id
                    recrobj.numeroeanprodotto = r.item_ean_id
                    recrobj.ean = r.item_ean
                    recrobj.percentualeiva = vat[r.b2b_vat_code].valoreiva
                    recrobj.numeroiva = vat[r.b2b_vat_code].numeroiva
                    recrobj.numeroreparto = r.fam_id
                    recrobj.numeroprodottoproduttore = r.supplier_item_id
                    recrobj.numerocontocontabilita = r.account_id
                    recrobj.codiceqta = 'CARICO'
                    recrobj.qtamovimento = r.b2b_uom_qty
                    recrobj.ordine = r.row
                    recrobj.tipoprovenienzaordine = 'FOR'
                    recrobj.totalenetto = r.b2b_net_total
                    recrobj.totale = recrobj.totalenetto * vat[r.b2b_vat_code].mult
                    recrobj.ivatotale = recrobj.totale - recrobj.totalenetto
                    recrobj.prezzonetto = r.b2b_net_total/r.b2b_uom_qty
                    recrobj.prezzo = recrobj.prezzonetto * vat[r.b2b_vat_code].mult
                    recrobj.ivaprezzo = recrobj.prezzo - recrobj.prezzonetto
                    recrobj.sincrofield = DBSession.execute(contasincrofield)
                    
                    cc = DBSession.query(Magazzini).filter_by(codicemagazzino=r.cost_center_code).one()
                    
                    recrobj.numeromagazzino = cc.numeromagazzino
                    
                    rechobj.movimentir.append(recrobj)
                    DBSession.add(recrobj)
                    DBSession.flush()
                    r.rec_id = rechobj.numeromovimento
                    r.rec_row = recrobj.numerorigamovimento
                    DBSession.add(r)
                    DBSession.flush()                    
                    
                    
                    
                    log.debug(_logprefix2+"- added recr id %s"%(recrobj.numerorigamovimento))
                    
                log.debug(_logprefix2 +"- completed %s (%s)" %(
                            rechobj.numeromovimento, rechobj.numerodocumento))
                
            i.exported = 1 
            log.debug(_logprefix1+"- set flag exported to 1")                
            DBSession.add(i)
            DBSession.flush()
        transaction.commit()
 
  
        #for fobj in files:


    def write_out(self, *args, **kw):
        """
        Process files from db and process docs and recs
        """   
        # get files to process
        files = self._get_files()
        
        log.info("movs : found %s to process"%(len(files)))  
  
        for fobj in files:
           
            results = get_mov(fobj.numeromovimento, self.movcode)         
            log.debug("")
            log.info("mov id: id %s with %s results"%(fobj.numeromovimento, len(results)))

            #row = 1
            for res in results:
                factb2b_dict = {}
                #factb2b_dict['supplier_id'] = prov.numeroprovenienza
                import pprint; pprint.pprint(results)
                for key, val in self.jsonmap.iteritems():
                    src, func = val
                    newval = getattr(mapper, func)(res[src])
                    factb2b_dict[key] = newval
                    log.debug("fact_b2b: %s | %s | %s | %s => %s"%(
                            src, func, key, 
                            unicode(str(res[src]), errors='replace'),
                            
                            [str(newval).decode("utf8")]
                ))
                     
              
                and_c = and_(
                                 Factb2b.supplier_id==factb2b_dict['supplier_id'],
                                 Factb2b.inputb2b_id==factb2b_dict['doc_id'],
                                 #Factb2b.header==factb2b_dict['header'],
                                 #Factb2b.doc_num==factb2b_dict['doc_num'],
                                 #Factb2b.rec_num==factb2b_dict['rec_num'],
                                 #Factb2b.b2b_sale_type==factb2b_dict['b2b_sale_type'],
                                 #Factb2b.b2b_code==factb2b_dict['b2b_code'],
                                 Factb2b.row==factb2b_dict['doc_row'],
                                 )  


                try:

                    fobjrow = DBSession.query(Factb2b).filter(*and_c).one()
                    log.debug("fact_b2b: found row id %s"%(fobjrow.b2b_id))
                                
                except:

                    fobjrow = Factb2b()  
                    log.debug("fact_b2b: row NOT found")                   


                setattr(fobjrow, "account_code", self.notfound )

                for key, val in factb2b_dict.iteritems():                        
                    setattr(fobjrow, key, val)

                DBSession.add(fobjrow) 
                
                #print fobjrow,fobjrow.doc_num                
                DBSession.flush()             
                log.debug("fact_b2b: processed doc #%s - ref #%s"%(fobjrow.doc_num,
                                                                    fobjrow.rec_num)) 
                #row += 1  
            #fobj.processed = 1
            fobj.controllonote = 20
            DBSession.add(fobj)  
            DBSession.flush()              
        transaction.commit()
    
       
    
          
            
            
        
    
