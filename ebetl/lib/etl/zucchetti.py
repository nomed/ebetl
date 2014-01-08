# -*- coding: utf-8 -*-
"""
from ebetl.model import *
index = 0
movs=DBSession.query(Movimentir).filter(and_(Movimentir.numeromovimento==576182, Movimentir.tipoprodotto=='PRD')).all()
for i in movs:
    print i
    p = DBSession.query(Prodotti).filter_by(numeroprodotto=i.idprodotto).one()
    if not i.prezzonetto/4 > p.costonetto:
        i.costonetto = p.costonetto
        i.totalecostonetto = i.qtamovimento * i.costonetto
        index = index +1
        print index
        DBSession.add(i)
        DBSession.flush()


"""
import glob, json

import logging, os, re, sys
logging.basicConfig(
    level=logging.DEBUG)
log = logging.getLogger('zucchetti')

from ebetl.lib.etl import get_txn
from ebetl.model import *
#from ebetl.model.dbretail import Inputb2b
#from ebetl.model.zerobi import Factb2b
import transaction

from sqlalchemy import and_
#from ebetl.lib.views import get_pricelist, get_pricelist_todict
from ebetl.lib.etl import Mapper
from ebetl.lib import strip_non_ascii

from itertools import groupby
from pprint import pprint



mapper = Mapper()

class ZucchettiObj(object):
    """
    zucchetti.path_input = %(here)s/archive/input/filconad/big
    zucchetti.filename = *.txt
    zucchetti.filename_out = filconad.csv
    zucchetti.path_output = %(here)s/archive/output/filconad/big
    zucchetti.codice = 000720
    zucchetti.notfound = 1601000000
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

        self.path_json = os.path.join(
                        os.path.dirname(os.path.realpath(self.path)),
                        'mappers', "%s.json"%record
                        )
        jsonf = open(self.path_json , "r" )
        self.json = json.load(jsonf)
        jsonf.close()

        self.path_jsonmap = os.path.join(
                        os.path.dirname(os.path.realpath(self.path)),
                        'mappers', "%s_target.json"%record
                        )
        jsonf = open(self.path_jsonmap , "r" )
        self.jsonmap = json.load(jsonf)
        jsonf.close()

        self.path_rosetta =  config.get(record+'.rosetta')
        self.rosetta = {}
        if os.path.exists(self.path_rosetta):
            rosettaf = open(self.path_rosetta , "r" )
            self.rosetta = json.load(rosettaf)
            rosettaf.close()

    def _get_files(self, *args, **kw):
        ret = []
        dir_all = glob.glob(self.path_file)
        print dir_all
        print self.path_file
        dir_all.sort()

        return dir_all

    def get_data(self,lines, *args, **kw):
        """


        """
        ret = []
        for r in lines:
            r=strip_non_ascii(r)
            if not r.startswith(' '):
                keys, body = self.json['header']
                txn = get_txn(keys, body, r)
                ret.append(txn)
        return ret

    def get_hash(self, fpath ):

        import md5

        my_f = open(fpath)
        my_s = my_f.read()
        my_f.close()

        my_hash = md5.new(my_s).hexdigest()

        return my_hash

    def store_files(self, *args, **kw):
        pass

        files = self._get_files()


        for fpath in files:
            log.debug(fpath)
            fname = os.path.basename(fpath)
            fname = self.get_hash(fpath)
            #print fname
            #print fpath
            #print self.json
            content = open(fpath).read()
            content = content.splitlines()
            results = self.get_data(content)
            #columns = self.json['header'][0]
            #print ";".join(columns)
            #for r in results:
                #row = []
                #for c in columns:
                #    row.append(i.get(c))
                #print ";".join(row)

            row = 1
            for res in results:
                factlaborcost_dict = {}


                for key, val in self.jsonmap.iteritems():
                    src, func = val
                    if res.has_key(src):
                        newval = getattr(mapper, func)(res[src])
                        factlaborcost_dict[key] = newval
                        log.debug("fact_b2b: %s | %s | %s | %s => %s"%(
                                    src, func, key, res[src], [unicode(newval).encode('utf-8')]
                        ))
                    else:
                        #log.debug("%s"%(pprint(pricelist)))
                        log.debug("not found: %s [%s]"%(src, key))

                fobjrow = Factlaborcost()

                #setattr(fobjrow, "account_code", self.config.get("%s.notfound"%(self.record)) )

                for key, val in factlaborcost_dict.iteritems():
                    if key in self.rosetta.keys():
                        val = self.rosetta[key][val]

                    setattr(fobjrow, key, val)
                DBSession.add(fobjrow)


            """
            try:
                fobj = DBSession.query(Inputb2b).filter(
                    and_(Inputb2b.filename==fname,
                        Inputb2b.supplier_id==prov.numeroprovenienza)
                ).one()
            except:
                fobj = Inputb2b()
                fobj.supplier_id=prov.numeroprovenienza
            fobj.supplier_code=self.prov
            fobj.filename = fname
            fobj.record = self.record
            content = open(fpath).read()
            fobj.content = content
            DBSession.add(fobj)
            DBSession.flush()
            bkpath = os.path.join(self.path_output,
                                        str(fobj.b2b_id).zfill(8)+'.txt')
            log.debug("path_output: " + self.path_output)
            log.debug("bkpath: " + bkpath)
            os.rename(fpath, bkpath)
            """
        transaction.commit()

    def write_out(self, inputb2b_id=None, *args, **kw):
        """
        Process files from db and process docs and recs
        """
        pass
        """
        # get prov obj
        prov = DBSession.query(Provenienze).filter(
                Provenienze.codiceprovenienza==self.prov,
                Provenienze.tipoprovenienza=="FOR").one()
        # get files to process
        if not inputb2b_id:
            files = DBSession.query(Inputb2b).filter(
                    and_(Inputb2b.supplier_id==prov.numeroprovenienza,
                         Inputb2b.processed == 0)
                ).order_by(Inputb2b.acquired).all()
        else:
            files = DBSession.query(Inputb2b).filter(
                    and_(Inputb2b.supplier_id==prov.numeroprovenienza,
                         Inputb2b.b2b_id == inputb2b_id)
                ).order_by(Inputb2b.acquired).all()

        log.info("input_b2b: found %s to process"%(len(files)))
        pricelist_tmp = None
        pricelist = None
        for fobj in files:

            # get current pricelist linked to supplier
            if not pricelist_tmp:
                pricelist_tmp = get_pricelist(prov.numeroprovenienza)
            # create a dict indexed by supplier_code
            if not pricelist:
                pricelist = get_pricelist_todict(pricelist_tmp, prov)

            results = self.get_data(pricelist, fobj.b2b_id, fobj.content.splitlines())
            log.debug("")
            log.info("input_b2b: id %s with %s results"%(fobj.b2b_id, len(results)))

            row = 1
            for res in results:
                factb2b_dict = {}
                factb2b_dict['supplier_id'] = prov.numeroprovenienza

                for key, val in self.jsonmap.iteritems():
                    src, func = val
                    if res.has_key(src):
                        newval = getattr(mapper, func)(res[src])
                        factb2b_dict[key] = newval
                        #log.debug("fact_b2b: %s | %s | %s | %s => %s"%(
                        #            src, func, key, res[src], [unicode(newval).encode('utf-8')]
                        #))
                    else:
                        #log.debug("%s"%(pprint(pricelist)))
                        log.debug("not found: %s [%s]"%(src, key))
                #log.debug(res)
                #sys.exit()

                # probably skip if doc exists
                factb2b_dict['row']=row
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
                    #raise
                    #fobjrows = DBSession.query(Factb2b).filter(*and_c).all()
                    #for fobj in fobjrows:
                    #    log.debug("Error on b2b_code: %s rec_num %s sale_type %s"%(
                    #                fobj.b2b_code, fobj.rec_num, fobj.b2b_sale_type) )
                    #raise
                    fobjrow = Factb2b()
                    log.debug("fact_b2b: row NOT found")
                    #from pprint import pprint
                    #log.debug(pprint(factb2b_dict))
                    #sys.exit()

                setattr(fobjrow, "account_code", self.config.get("%s.notfound"%(self.record)) )

                for key, val in factb2b_dict.iteritems():
                    if key in self.rosetta.keys():
                        val = self.rosetta[key][val]

                    setattr(fobjrow, key, val)
                DBSession.add(fobjrow)

                #print fobjrow,fobjrow.doc_num
                DBSession.flush()
                log.debug("fact_b2b: processed doc #%s - ref #%s"%(fobjrow.doc_num,
                                                                    fobjrow.rec_num))
                row += 1
            fobj.processed = 1
            DBSession.add(fobj)
            DBSession.flush()
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
        """







