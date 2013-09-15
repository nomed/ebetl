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
from ebetl.model.zerobi import Factb2b
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
        ret = DBSession.query(Movimentit).filter(Movimentit.numerotipopagamento==1)
        ret = ret.filter(or_(*orlist))
        ret = ret.order_by(Movimentit.datadocumento)
        
        return ret.all()




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
                                 Factb2b.inputb2b_id==factb2b_dict['inputb2b_id'],
                                 Factb2b.header==factb2b_dict['header'],
                                 Factb2b.doc_num==factb2b_dict['doc_num'],
                                 Factb2b.rec_num==factb2b_dict['rec_num'],
                                 Factb2b.b2b_sale_type==factb2b_dict['b2b_sale_type'],
                                 Factb2b.b2b_code==factb2b_dict['b2b_code'],
                                 Factb2b.row==factb2b_dict['row'],
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
            DBSession.add(fobj)  
            DBSession.flush()              
        transaction.commit()
    
       
    
          
            
            
        
    
