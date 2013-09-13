# -*- coding: utf-8 -*-
"""


"""
import glob, json

import logging, os, re, sys
logging.basicConfig(
    level=logging.DEBUG)
log = logging.getLogger('filconad')

from ebetl.lib.etl import get_txn
from ebetl.model import *
from ebetl.model.dbretail import Inputb2b
from ebetl.model.zerobi import Factb2b
import transaction 

from sqlalchemy import and_
from ebetl.lib.views import get_pricelist, get_pricelist_todict
from ebetl.lib.etl import Mapper
from ebetl.lib import strip_non_ascii

from itertools import groupby


    

mapper = Mapper()

class FilconadObj(object):
    """
    filconad_big.path_input = %(here)s/archive/input/filconad/big
    filconad_big.filename = *.txt
    filconad_big.filename_out = filconad.csv
    filconad_big.path_output = %(here)s/archive/output/filconad/big
    filconad_big.codice = 000720
    filconad_big.notfound = 1601000000    
    """

    def __init__(self, config,record, *args, **kw):
        """
        """
        self.record = record
        self.config=config   
        self.prov=config.get(record+'.codice')
                          
        self.path = config.get(record+'.path_input')
        self.filename = config.get(record+'.filename')
        
        self.path_output = config.get(record+'.path_output')
        #self.filename_out = os.path.join(self.path_output,
        #                      config.get(record+'.filename_out'))

        self.path_file = os.path.join(self.path, self.filename)
        print self.path
        self.path_json = os.path.join(
                        os.path.dirname(os.path.realpath(self.path)),
                        'mappers', "%s.json"%record
                        )
        jsonf = open(self.path_json , "r" )  
        self.json = json.load(jsonf)
        jsonf.close()  

        self.path_jsonmap = os.path.join(
                        os.path.dirname(os.path.realpath(self.path)),
                        'mappers', "filconad.json"
                        )
        jsonf = open(self.path_jsonmap , "r" )  
        self.jsonmap = json.load(jsonf)
        jsonf.close()          

    def _get_files(self, *args, **kw):
        ret = []
        dir_all = glob.glob(self.path_file)
        print self.path_file
        dir_all.sort()
        
        return dir_all

    def get_data(self,pricelist, b2b_id, lines, *args, **kw):
        """
        
                
        """   
        ret = []
        for r in lines:             
            r=strip_non_ascii(r)
            if not r.startswith(' '):

                if r[0:2] == '01':
                    keys, body = self.json['header']
                    h_txn = get_txn(keys, body, r) 
                    h_txn['inputb2b_id'] = b2b_id
                elif r[0:2] == '02':
                    "join header and body"
                    keys, body = self.json['body']
                    txn = get_txn(keys, body, r)
                    txn.update(h_txn)
                    b_ref_code = txn.get('b_ref_code')
                    b_ref_code = b_ref_code.strip()

                    if  b_ref_code in pricelist.keys():
                        txn.update(pricelist[b_ref_code])

                    ret.append(txn) 
                             
        return ret
        
        

    def store_files(self, *args, **kw):
        files = self._get_files()
        p = DBSession.query(Provenienze).filter(
                Provenienze.codiceprovenienza==self.prov).one()         
        for fpath in files:

            fname = os.path.basename(fpath)
            try:
                fobj = DBSession.query(Inputb2b).filter(
                    and_(Inputb2b.filename==fname,
                        Inputb2b.supplier_id==p.numeroprovenienza)
                ).one()
            except:
                fobj = Inputb2b()                
                fobj.supplier_id=p.numeroprovenienza
            fobj.supplier_code=self.prov    
            fobj.filename = fname
            fobj.record = self.record
            content = open(fpath).read()
            fobj.content = content
            DBSession.add(fobj)
            DBSession.flush()
        transaction.commit()
    
    def get_dict(self, *args, **kw):
        """
        
        """
        
        
        ret = {}
        f = open(self.path_file)
        for r in f:             
            row = []
            r=strip_non_ascii(r)
            cod_in_row = self.get_row_dict(r)
            code = None
            if cod_in_row:
                code, index, rowdata = cod_in_row
            if code == '01':
                if not index in ret:
                    ret[index]=[]
                    numdoc=rowdata['numdoc']
                    data=rowdata['data']
                    mag=rowdata['mag']
            elif code == '02':
                row = [numdoc,data,mag]
                for k in ['codfor','refpos','rep','desc','unitprice','qty','codiva','codqty','ean']:
                    row.append(rowdata[k])
                ret[index].append(row)            
        return ret
        
        

    def write_out(self, *args, **kw):
        """
        Process files from db and process docs and recs
        """
        # get prov obj
        prov = DBSession.query(Provenienze).filter(
                Provenienze.codiceprovenienza==self.prov).one()     
        # get files to process
        files = DBSession.query(Inputb2b).filter(
                    and_(Inputb2b.supplier_id==prov.numeroprovenienza,
                         Inputb2b.processed == 0)
                ).order_by(Inputb2b.acquired).all()
        # get current procelist linked to supplier
        pricelist_tmp = get_pricelist(prov.numeroprovenienza)
        # create a dict indexed by supplier_code
        pricelist = get_pricelist_todict(pricelist_tmp, prov)
        
        log.info("input_b2b: found %s to process"%(len(files)))  
            
        for fobj in files:
        
            
            results = self.get_data(pricelist, fobj.b2b_id, fobj.content.splitlines())
            
            log.debug("")
            log.info("input_b2b: id %s with %s results"%(fobj.b2b_id, len(results)))
            
            for res in results:
                factb2b_dict = {}

                for key, val in self.jsonmap.iteritems():
                    src, func = val
                    if res.has_key(src): 
                        newval = getattr(mapper, func)(res[src])
                        factb2b_dict[key] = newval
                        log.debug("fact_b2b: %s | %s | %s | %s => %s"%(
                                    src, func, key, res[src], newval       
                        ))
                try:
                    # probably skip if doc exists
                    and_c = and_(
                                     Factb2b.supplier_id==factb2b_dict['supplier_id'],
                                     Factb2b.inputb2b_id==factb2b_dict['inputb2b_id'],
                                     Factb2b.header==factb2b_dict['header'],
                                     Factb2b.doc_num==factb2b_dict['doc_num'],
                                     Factb2b.rec_num==factb2b_dict['rec_num'],
                                     )
                    fobjrow = DBSession.query(Factb2b).filter(*and_c).one()
                    log.debug("fact_b2b: found row id"%(fobjrow.b2b_id))
                                
                except:
                    fobjrow = Factb2b()           
                    log.debug("fact_b2b: row NOT found")
                    from pprint import pprint
                    #log.debug(pprint(factb2b_dict))
                    #sys.exit()

                setattr(fobjrow, "account_code", self.config.get("%s.notfound"%(self.record)) )

                for key, val in factb2b_dict.iteritems():                        
                    setattr(fobjrow, key, val)
                    
                DBSession.add(fobjrow) 
                
                #print fobjrow,fobjrow.doc_num                
                DBSession.flush()             
                log.debug("fact_b2b: processed doc #%s - ref #%s"%(fobjrow.doc_num,
                                                                    fobjrow.rec_num))   
        transaction.commit()
        #sys.exit()
        #index = out_dict.keys()
        #index.sort()
        
        #file_obj = open(self.filename_out,'ab')                         
        #for i in index:
        #    for row in out_dict[i]:
        #        print >> file_obj, ';'.join(row)
        #    
        #file_obj.close()
    
       
    
          
            
            
        
    
