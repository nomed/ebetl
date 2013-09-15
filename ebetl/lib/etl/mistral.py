# -*- coding: utf-8 -*-
from genshi.template import TemplateLoader 
"""

TRACCIATO MR2MISTRAL

       TESTATA 

       Tipo Record [T]                    1       1 -   1
   (A) Codice Documento                  10       2 -  11 
       Data                               8      12 -  19
       Codice Fornitore                  16      20 -  35
       Numero Documento                  12      36 -  47
       Blank                             16      48 -  63
       Totale Lordo [x10000]             16      64 -  79
       Blank                            176      80 - 255
       Terminatore Record (*)             1     256 - 256
       
       RIGHE TOTALI NETTI X CONTI  

       Tipo Record [R]                    1       1 -   1
   (A) Codice Documento                  10       2 -  11 
       Data                               8      12 -  19
       Codice Fornitore                  16      20 -  35
       Numero Documento                  12      36 -  47
       Conto Contabilita                 16      48 -  63
       Totale Netto [x10000]             16      64 -  79
   (B) Centro di costo                    8      80 -  87
       Codice IVA                        16      88 - 103
       Blank                            152     104 - 255
       Terminatore Record (*)             1     256 - 256              
       
       RIGHE IVA   

       Tipo Record [I]                    1       1 -   1
   (A) Codice Documento                  10       2 -  11 
       Data                               8      12 -  19
       Codice Fornitore                  16      20 -  35
       Numero Documento                  12      36 -  47
       Codice IVA                        16      48 -  63
       Totale Netto [x10000]             16      64 -  79
       Totale IVA   [x10000]             16      80 -  95       
       Totale Lordo [x10000]             16      96 - 111       
       Blank                            144     112 - 255
       Terminatore Record (*)             1     256 - 256  

   (A) FACFOR: Fattura Accompagnatoria
       FATFOR: Fattura 
   (B) Centro di costo: 000297 Gavi, 000351 Arquata. 000352 Novi Via Turati
"""
import logging, os, re, sys
logging.basicConfig(
    level=logging.DEBUG)
log = logging.getLogger('mistral')
#from ebtl.lib.etl.config import *
from ebetl.lib.etl.config import _ensure_unicode
from ebetl.lib.etl.config import movcode_labels
from ebetl.model import *
from sqlalchemy import and_, or_
import transaction 
from pprint import PrettyPrinter
import csv




def get_data(data):
    d=str(data.day)
    d="0"*(2-len(d))+d
    m=str(data.month)
    m="0"*(2-len(m))+m
    y=str(data.year)
    return y+m+d #YYYYMMDD (20130611)

def get_fixedwidth(data,l=12):
    return " "*(l-len(data))+data # L 12

def get_fixednumdoc(data,l=12):
    
    if data.strip():
        numdoc = "".join([str(int(s)) for s in list(data) if s.isdigit()])
    else:
        numdoc=data
    #print [data], [numdoc]
    return get_fixedwidth(numdoc, l)

def get_fixednum(data,l=20):
    data=str(int(data*10000))
    return "0"*(l-len(data))+data # L 12

def set_account_from_rep():
    m=DBSession.query(Movimentit).filter(
        			and_(Movimentit.ingressouscita=='I')).order_by(Movimentit.datamovimento).all()
    for mr in m:
        print len(mr.movimentir)
        for r in mr.movimentir:
            
            if r.numerocontocontabilita < 1:
                if r.prodotto.numerocontocontabilitai > 1:
                    r.numerocontocontabilita = r.prodotto.numerocontocontabilitai  
                    print r.prodotto.numerocontocontabilitai,r.contocontabilita 
                elif r.reparto.numerocontocontabilitai > 1:
                    r.numerocontocontabilita = r.reparto.numerocontocontabilitai
                    r.prodotto.numerocontocontabilitai = r.reparto.numerocontocontabilitai
                else:
                    print '=',r.numeromovimento
    transaction.commit()
                     

def set_account_from_rep2():
    
    #m=DBSession.query(Movimentir).filter(and_(Movimentir.numerocontocontabilita<2,
    #                                          Movimentir.codiceqta=='CARICO',
    #                                          Movimentir.movval==-1)).all()
    m = DBSession.query(Movimentir).filter(
        			and_(Movimentit.codicemovimento=='FATFOR',
        			     #Movimentit.ingressouscita=='I',
        			     #Movimentit.elaborato!=2,
        			     #Movimentir.numeromovimento==Movimentit.numeromovimento,
        			     #Movimentir.numerocontocontabilita==0,
        			     #Movimentir.tiporiga!='D'
        			     )).order_by(Movimentit.datamovimento).all()
        			                        
    print len(m)
    for r in m:
        #print len(mr.movimentir)
        #print mr.numeromovimento, mr.numerodocumento
        #if r.movimento.ingressouscita=='I'  :      
        #for r in mr.movimentir:
        if r:
            #print "======= START", r
            conto_mov=r.numerocontocontabilita
            conto_prod=0
            conto_rep=0
            try:
               conto_prod=r.prodotto.numerocontocontabilitai
            except:
               pass
            try:
               conto_rep=r.reparto.numerocontocontabilitai
            except:
                pass
            if conto_mov < 1:
                if conto_prod > 0:
                    r.numerocontocontabilita = conto_prod  
                    print conto_prod
                    #print "From Prod",r.prodotto.numerocontocontabilitai,r.conto 
                elif conto_rep > 0:
                    r.numerocontocontabilita = conto_rep
                    print conto_rep
                    #if r.prodotto:
                    #    r.prodotto.numerocontocontabilitai = r.reparto.numerocontocontabilitai
                    #    print "From Rep",r.prodotto.numerocontocontabilitai,r.conto
                else:
                    print '=',r.numerorigamovimento, r.descrizione
                DBSession.add(r)
                #DBSession.flush()
            #print "======= END", r
            #print "\n\n\n"
    transaction.commit()

class Db2Mistral(object):
    """
    """
    def __init__(self, config, *args, **kw):
        self.config=config 
        self.codmov = config.get("mistral.write.codmov").split(',')   
        self.path_genshi=  config.get('mistral.path_genshi') 
        self.loader_genshi = TemplateLoader([self.path_genshi],
                        auto_reload=True)   
        log.debug("codmov: %s"%self.codmov)                                
        log.debug("path_genshi: %s"%self.path_genshi)
        #sys.exit()
        
    def get_h(self,data):
        """{
        'gross': 181.61, 
        'doccode': 'FACFOR',  [10]
        'data': '20130204', 
        'net': 165.1, 
        'numdoc': '       47862', 
        'codfor': '      000003'
        }
        """
        h = data['h']
        ret='T'
        ret=ret+get_fixedwidth(h['doccode'],10)
        ret=ret+get_fixedwidth(h['data'],8)
        ret=ret+get_fixedwidth(h['codfor'],16)
        ret=ret+get_fixednumdoc(h['numdoc'],12)
        ret=ret+get_fixedwidth(' ',16)
        ret=ret+get_fixednum(h['gross'],16)
        ret=ret+" "*(255-len(ret))+'*'
        return ret

    def get_r(self,data):
        """{
        'gross': 181.61, 
        'doccode': 'FACFOR',  [10]
        'data': '20130204', 
        'net': 165.1, 
        'numdoc': '       47862', 
        'codfor': '      000003'
        }
        """
        h = data['h']
        ret='R'
        ret=ret+get_fixedwidth(h['doccode'],10)
        ret=ret+get_fixedwidth(h['data'],8)
        ret=ret+get_fixedwidth(h['codfor'],16)
        ret=ret+get_fixednumdoc(h['numdoc'],12)
        ret_rows=[]
        for k,v in data['r'].iteritems():
            for mag, ivadict in v.iteritems():
                for iva, tot in ivadict.iteritems():
                    r=ret
                    r=r+get_fixedwidth(k,16)  
                    r=r+get_fixednum(tot,16)
                    r=r+get_fixedwidth(mag,8) 
                    r=r+get_fixedwidth(iva,16) 
                    r=r+" "*(255-len(r))+'*'
                    ret_rows.append(r)
        return ret_rows

    def get_f(self,data):
        """{
        'gross': 181.61, 
        'doccode': 'FACFOR',  [10]
        'data': '20130204', 
        'net': 165.1, 
        'numdoc': '       47862', 
        'codfor': '      000003'
        }
        """
        h = data['h']
        ret='I'
        ret=ret+get_fixedwidth(h['doccode'],10)
        ret=ret+get_fixedwidth(h['data'],8)
        ret=ret+get_fixedwidth(h['codfor'],16)
        ret=ret+get_fixednumdoc(h['numdoc'],12)
        ret_rows=[]
        for k,v in data['f'].iteritems():
            r=ret
            r=r+get_fixedwidth(k,16)  
            r=r+get_fixednum(v[0],16)
            r=r+get_fixednum(v[1],16)            
            r=r+get_fixednum(v[2],16)            
            r=r+" "*(255-len(r))+'*'
            ret_rows.append(r)
        return ret_rows

        
    def get_mov(self,codmov, *args, **kw):
        orlist = []
        log.debug("get_mov: %s"%codmov)
        for c in codmov:
            orlist.append(Movimentit.codicemovimento==c)  
        from pprint import pprint
        tables = (Movimentit, Movimentir, Reparti, Prodotti)
        columns = []
        for m in tables:
            for c in m.__table__.columns:
                    if not c in columns:
                        columns.append(c._label)
        pprint(columns)
        movst = DBSession.query(*tables)#, Prodotti, Eanprodotti, )
        movst = movst.join(Movimentir, Movimentit.numeromovimento == Movimentir.numeromovimento)
        movst = movst.filter(and_(or_(*orlist),
                                  Movimentit.numerotipopagamento==1,)).order_by(
                                                    Movimentit.datadocumento).all() 

        sys.exit()

        
    def get_mov2(self,codmov, *args, **kw):
        orlist = []
        log.debug("get_mov: %s"%codmov)
        sys.exit()
        for c in codmov:
            orlist.append(Movimentit.codicemovimento==c)
        movst = DBSession.query(Movimentit).filter(
        			and_(
        			     or_(*orlist),#Movimentit.codicemovimento==codmov,
        			     #Movimentit.ingressouscita=='I',
        			     #Movimentit.numeroprovenienza==748,
        			     #Movimentit.elaborato!=2
                                     #Movimentit.datadocumento>datadoc_in,
                                     #Movimentit.datadocumento<datadoc_out,
                                     Movimentit.numerotipopagamento==1,
        			     )).order_by(Movimentit.datadocumento).all()
        			     
        ret = []
        #movst = [movst[0]]
        for m in movst:
            toadd = True
            doc_dict = {}
            h = {}
            h['data']=get_data(m.datadocumento) # AAAAMMDD | ['20130611'] | l8
            h['codfor']=m.provenienza.codiceprovenienza # ['      000795'] | l12
            h['numdoc']=m.numerodocumento # ['        257R'] | l12
            h['gross']=m.totaledocumento
            h['net']=m.totaleimponibile
            h['doccode']=m.codicemovimento
            docr={}
            for r in m.movimentir:
                #print r.numerorigamovimento, r.numerocontocontabilita
                r_total = r.totalenetto
                try:
                    numconto=r.prodotto.numerocontocontabilitai
                    contoobj=DBSession.query(Conticontabilita).filter_by(
                    		numerocontocontabilita=numconto).one()
                    r_conto=contoobj.codicecontocontabilita
                    print r_conto
                except:
                    #raise
                    r_conto='1601000001'
                """
                if r.numerocontocontabilita>1:
                    try:
                        r_conto=r.conto.codicecontocontabilita
                        #r_conto = r.prodotto.numerocontocontabilitai
                    except:
                        r_conto=" "
                else:
                    r_conto=" "
                """
                if toadd and r_conto and (r.totalenetto>0):
                    print m.numeromovimento
                    codmag=r.magazzino.codicemagazzino
                    try:
                        codiva = r.iva.codiceiva
                    except:
                        codiva = 'ERR'
                    if not r_conto in docr.keys():
                        docr[r_conto]={}
                    if not codmag in docr[r_conto].keys():
                        docr[r_conto][codmag]={}
                    if not codiva in docr[r_conto][codmag].keys():
                        docr[r_conto][codmag][codiva]=0
                    
                    docr[r_conto][codmag][codiva]=docr[r_conto][codmag][codiva]+r.totalenetto
            moviva={}
 
            if docr:
                for miva in m.movimentiiva:
                    #[totaleimponibile, totaleiva, totale]
                    codiva=miva.iva.codiceiva
                    if not miva.iva.codiceiva in moviva:
                        moviva[codiva]=[0,0,0]
                    moviva[codiva][0]= moviva[codiva][0]+ miva.totaleimponibile  
                    moviva[codiva][1]= moviva[codiva][1]+ miva.totaleiva
                    moviva[codiva][2]= round(moviva[codiva][0]+moviva[codiva][1],3)
                for i,magdic in docr.iteritems():
                    for mval,k in magdic.iteritems():
                        for civa, val in k.iteritems():
                            #print m, civa, val
                            docr[i][mval][civa]=round(val,2)
            
    
            else:
                print m.numeromovimento, m.numerodocumento
            doc_dict=dict(h=h,r=docr,f=moviva)
            ret.append(doc_dict)
            m.numerotipopagamento=3
            DBSession.add(m)
        return ret
               
    def write_out(self,*args, **kw):
        opath=self.config.get('mistral.path_output') 
        log.debug("opath: %s"%(opath))
        fname=self.config.get('mistral.filename')
        log.debug("fname: %s"%(fname))
        fout=os.path.join(opath,fname)
        log.debug("fout: %s"%fout)
        
        fobj=open(fout,'wr')
        ret = self.get_mov(self.codmov)
        #tmpl = self.loader_genshi.load('index.html')
        if True:
            for d in ret:
                h=self.get_h(d)
                r=self.get_r(d)
                f = self.get_f(d)
                #print d
                print>>fobj, h
                for i in r:
                    print>>fobj, i
                
                for i in f:
                    print>>fobj, i
        fobj.close()
        #stream = tmpl.generate(ret=ret)
                     
        #s = stream.render('html', doctype='html', encoding='utf-8')
        #output_html = open(opath+'MOVFAT.html', 'w')
        
        #output_html.write(s)
        transaction.commit()

class MistralObj(object):

    def __init__(self, config,pc=False, *args, **kw):
        self.config=config             
        self.pc = pc
        self.pcfile = config.get('mistral.pc')
    
    def _parse_pc(self):
        f=open(self.pcfile)
        csvreader = csv.reader(f, delimiter=',')
        csvreader.next()
        for row in csvreader:
            natura = row[3]
            conto1=row[0][0:2]
            desc_conto1=row[0][2:]
            try:
                c1=DBSession.query(Account).filter_by(account_number=conto1).one()
            except:
                c1=Account(conto1)
                
            c1.account_description=desc_conto1
            c1.account_type_id = natura
            
            DBSession.add(c1)
            
            conto2=conto1+row[1][0:2]
            desc_conto2=row[1][2:]
            
            try:
                c2=DBSession.query(Account).filter_by(account_number=conto2).one()
            except:
                c2=Account(conto2)
                
            c2.account_description=desc_conto2
            c2.account_type_id = natura
            c2.parent = c1
            DBSession.add(c2)            
            
            conto3=conto2+row[2][0:6]
            desc_conto3=row[2][6:] 
            
            try:
                c3=DBSession.query(Account).filter_by(account_number=conto3).one()
            except:
                c3=Account(conto3)
                
            c3.account_description=desc_conto3
            c3.account_type_id = natura
            c3.parent = c2
            DBSession.add(c3)
            
            
       
    def write_out(self):
        if self.pc:
            pc_dict = self._parse_pc()
        transaction.commit()
