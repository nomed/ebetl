# -*- coding: utf-8 -*-
"""
Acquisisce il file fatmicro dall'ftp e genera un csv aggiungendo data (ggmmaaaa)
e ean se presente in anagrafica prodotti interrogando per codice articolo.

Documenti Passivi:

* Fatt. Diff. Deposito: se presente ALGTPD genera il DTDEPF corrispondente
* Fatt. Diff. Diretti : se presente ALGTPD genera il DTDIRF corrispondente
* Fatt. Acco. Deposito: genera FACDEPF corrispondente

Codici Movimento:

* DTDEPF: Documento di trasporto per Deposito
* DTDIRF: Documento di trasporto per Diretti
* FACDEPF: Fattura accompagnatoria per Deposito

5001: m 
5002: 
5003:

"""
magmap = {'000297':'2', '000351':'1', '000352':'3'}

import logging, os, re, sys
logging.basicConfig(
    level=logging.DEBUG)
log = logging.getLogger('fatmicro')
from genshi.template import TemplateLoader              

from ebetl.lib.etl.records import fatmicro

from ebetl.model import *
import transaction 

movcode_labels =['magazzino','codice_riordino','descrizione', 'iva','grammatura',
                 'udm','costo','qty','costo_totale']

movcode = {'FACDEPF':fatmicro._COMMON,
           'DTDEPF':fatmicro._COMMON,
           'DTDIRF':fatmicro._COMMON
          }

def _ensure_unicode(s):
    if isinstance(s, unicode):
        return s
    else:
        return unicode(s,'latin-1','replace')

def strip_non_ascii(string):
    ''' Returns the string without non ASCII characters'''
    stripped = []
    for c in string:
        if 0 < ord(c) < 127:
            stripped.append(c)
        else:
            stripped.append(' ')
    ret=''.join(stripped)
    return ret

class FatmicroObj(object):
    """
    Processa `fatmicro.path_input/fatmicro.path_input`
    
    Aggiorna la tabella `input_cli00` usata per divulgare le variazioni
    
    
    >>> from tg import config
    >>> record='fatmicro'
    >>> fat=fatmicro.FatmicroObj(config,record)
    >>> f = open(fat.path_file)
    >>> lines=f.readlines()           

    """
    record = fatmicro.record
    def __init__(self, config,record, *args, **kw):
        """
        """
        self.config=config   
        self.path_genshi=  config.get(record+'.path_genshi') 
        self.loader_genshi = TemplateLoader([self.path_genshi],
                        auto_reload=True)                           
        self.path = config.get(record+'.path_input')
        self.filename = config.get(record+'.filename')
        
        self.path_output = config.get(record+'.path_output')
        self.filename_out = config.get(record+'.filename_out')

        self.path_file = os.path.join(self.path, self.filename)
        self.html = kw.get('html')
        self.path_root = self.path_output
        self.record_index = []
        for r in self.record:
            self.record_index.append(r[2])

    def get_row_dict(self, row, *args, **kw):
        """Trasforma la riga del file fatmicro in un dizionario.

		:param row: 
		    riga del file fatmicro
		
		:returns:
			dict : dizionario con chiavi da header 

 		>>> row
		'0003520433107122012 0690891000120000000001170000000149 000000000212100 RIC.SGRASS.MARS.CHANT FPML062500100121F90105001NM              00000000'
   		>>> fat.get_row_dict(row)
		{'ALGCES': '0000000117', 'ALGSCO': '000000000', 'ALGTPD': 'F', 'ALGDEM': '5001', 'ALGAIV': '2100', 'ALGTPA': '1', 'ALGMDC': '12', 'ALGFL3': '', 'ALGMBO': '00', 'confezionamento': 'FP', 'pezzatura': '0012', 'ALGNBO': '', 'codice_iva': '21', 'codice_articolo': '0690891', 'ALGGBO': '00', 'tipo_grammatura': 'ML', 'ALGGDC': '07', 'ALGQTA': '0001200', 'multiplo': '001', 'ALGSEM': '9010', 'ALGFL2': '', 'ALGLIB': '', 'ALGFL1': 'M', 'descrizione_articolo': 'RIC.SGRASS.MARS.CHANT', 'grammatura': '0625', 'ALGADC': '2012', 'ALGTIR': 'N', 'ALGABO': '0000', 'ALGNDC': '04331', 'ALGVEN': '0000000149', 'ALGCLI': '000352', 'ALGOFF': ''}
        """    
        ret = {}
        for r in self.record:
            ret[r[2]]=row[r[0]:r[1]].strip()
            if r[2] == 'codice_articolo':
                ret[r[2]]='0'+row[r[0]:r[1]].strip() 
        ret['data']="%s%s%s"%(ret['ALGGDC'], ret['ALGMDC'], ret['ALGADC'])
        try:
            prod = DBSession.query(Prodotti).filter_by(
                              codiceprodotto=str(ret['codice_articolo'])).one()
            ret['ean']=prod.eans[0].ean
        except:
            print ret['codice_articolo'],  ret['descrizione_articolo']
            ret['ean']=''
        if not ret['ean']:
            ret['ean']=''
        return ret
    
    def get_dict(self, *args, **kw):
        """
        Processa il file 'fatmicro' e divide i documenti contenuti per tipologia.
        
        * se ALGNBO non nullo e ALGTPD=B => DTDIRF (Fattura Differita Diretta).
        * se ALGNBO non nullo e ALGTPD=B => DTDEPD (Fattura Differita Deposito)
        * se ALGNBO nullo e ALGTPD=F => FACDEPF(Fattura Accompagnatoria Deposito)
        
        :return:
            dict: dizionario con {'<CODICE_MOVIMENTO>':{'<NUMDOC'>:[<get_row_dict>]}}
        
        """
        
        
        ret = {}
        for k,v in movcode.iteritems():
            #{'DTDIRF':{},'DTDEPF':{},'FACDEPF':{}}
            ret[k] = {}
        f = open(self.path_file)
        for r in f: 
            #r=_ensure_unicode(r)
            r=strip_non_ascii(r)
            r_dict=self.get_row_dict(r)
            # numero ddt   
            ddt_n=r_dict['ALGNBO'].strip()
            ddt_n=ddt_n+r_dict['ALGFL2']
            
            
            
            if ddt_n:
                ddt_n="%(ALGABO)s%(ALGMBO)s%(ALGGBO)s_%(ALGCLI)s_"%r_dict+ddt_n
            
            # numero fattura
            f_n=r_dict['ALGNDC'].strip()
            f_n=f_n+r_dict['ALGFL1']
            # data 
            f_data = "%(ALGADC)s%(ALGMDC)s%(ALGGDC)s_%(ALGCLI)s_"%r_dict
            
            # genera il nome file            
            f_n=f_data+f_n
            
            ddt_n=ddt_n.replace('/','_')
            f_n = f_n.replace('/','_')
            s_row=' '
            r_dict['NUMMAG']=magmap.get(r_dict['ALGCLI'])
            if ddt_n:
                s_row="%(ALGCLI)s %(ALGTPD)s Bolla numero "
                s_row=s_row+"%(ALGFL1)s%(ALGNBO)s del "
                s_row=s_row+"%(ALGABO)s%(ALGMBO)s%(ALGGBO)s" 
                r_dict['NUMDOC']  = r_dict['ALGNBO'].strip()+r_dict['ALGFL2']                                  
                if r_dict['ALGTPD'] == 'B':
                    s_row=f_data+" (Fatt. Diff. Diretti  N %(ALGNDC)s)  "+s_row
                    if not ddt_n in ret['DTDIRF']:
                        ret['DTDIRF'][ddt_n]=[]
                        #print s_row%r_dict
                    ret['DTDIRF'][ddt_n].append(r_dict)
                    
                elif r_dict['ALGTPD'] == 'F':
                    
                    s_row=f_data+" (Fatt. Diff. Deposito N %(ALGNDC)s)  "+s_row
                    if not ddt_n in ret['DTDEPF']:
                        ret['DTDEPF'][ddt_n]=[]  
                        #print s_row%r_dict 
                    ret['DTDEPF'][ddt_n].append(r_dict)

                                   
            else:
                r_dict['NUMDOC']  = r_dict['ALGNDC'].strip()+r_dict['ALGFL1']             
                if r_dict['ALGTPD'] == 'F':
                    s_row=f_data+\
                          " (Fatt. Acco. Deposito N %(ALGNDC)s)  %(ALGCLI)s"+s_row
                    if not f_n in ret['FACDEPF']:
                        ret['FACDEPF'][f_n]=[]                       
                    ret['FACDEPF'][f_n].append(r_dict)
        return ret
        
    def get_headers(self, *args, **kw):
        """
        :return: 
            list: intestazione colonne file csv
        """
        ret = ['data']
        ret.append('NUMDOC')
        ret.append('NUMMAG')
        for r in self.record:
            ret.append(r[2])
        ret.append('ean')
        return ret
        
    def get_string(self, headers, *args, **kw): 
        """
        :return:
            str: usato per generare le righe del file csv da dict (get_row_dict)
        """
        ret = ''
        for r in headers:
            ret = ret + '%('+r+')s;'
        return ret

    def write_out(self, *args, **kw):
        tmpl = self.loader_genshi.load('index.html')
        out_dict = self.get_dict()
        headers = self.get_headers()
        string_line = self.get_string(headers)

        
        for d in out_dict.keys():
        
            onefile=os.path.join(self.path_root,d, 'single','fatmicro.csv')
            onefile_obj = open(onefile,'wb')        
            path_out = os.path.join(self.path_root, d)

            if not os.path.exists(path_out):
                os.makedirs(path_out)
            
            index = out_dict[d].keys()
            index.sort()
            for numdoc in index:
                path_out_file=os.path.join(path_out, numdoc)
                if self.html:
                    values = []
                    vat={}
                    totals=[0,0,0]
                    for r in out_dict[d][numdoc]:
                        #print r
                        val = {}
                        index = 0
                        for m in movcode[d]:
                            try:
                                val[movcode_labels[index]]=m[1](r.get(m[0]))
                            except:
                                print r, movcode_labels[index], m[0]
                                raise
                            index = index +1
                        val['costo_totale']=val['qty']*val['costo']
                        if not val['iva'] in vat.keys():
                            vat[val['iva']] = [0,0,0]
                        costo=val['costo_totale']
                        lordo=costo*(1+float(val['iva'])/100)
                        iva=lordo-costo
                        vat[val['iva']][0]=vat[val['iva']][0]+costo
                        vat[val['iva']][2]=vat[val['iva']][2]+lordo
                        vat[val['iva']][1]=vat[val['iva']][1]+iva
                        values.append(val)
                        codice_articolo = r.get('codice_articolo')

                        try:
                            cli00obj = DBSession.query(Cli00).filter_by(
                              codice_articolo=str(codice_articolo)).one()

                        except:
                            cli00obj=Cli00(codice_articolo=codice_articolo)
                            
                        for key in ['descrizione_articolo', 'tipo_grammatura',
                                        'grammatura', 'multiplo', 'pezzatura',
                                        'codice_iva','confezionamento']:
                            setattr(cli00obj, key, r.get(key))
                        cli00obj.active = True
                        cli00obj.new = False
                        cli00obj.ultimo_costo = r.get('ALGCES') 
                        DBSession.add(cli00obj)
                        DBSession.flush()  
                    for key in vat.keys():
                        for i in range(len(vat[key])):
                            #print "="*10, numdoc, key, i , totals[i],vat[key][i]
                            totals[i]=totals[i]+vat[key][i]
                    
                    stream = tmpl.generate(headers=headers, 
                                       d=d, 
                                       numdoc=numdoc, 
                                       values=values,#out_dict[d][numdoc],
                                       movcode_labels=movcode_labels,
                                       movcode=movcode,
                                       vat=vat,totals=totals)
                     
                    s = stream.render('html', doctype='html', encoding='utf-8')
                    output_html = open(path_out_file+'.html', 'w')
                    #print dir(s)
                    output_html.write(s)
                transaction.commit()                     
                output = open(path_out_file+'.csv', 'wb')                                       

                for r in out_dict[d][numdoc]:
                    line = string_line%r
                    line = line.encode('latin-1', 'replace')
                    print >>output, line
                    print >>onefile_obj, line
            onefile_obj.close()
        num = 0
        fout = os.path.join(self.path, 'acquisiti', 'fatmicro.'+str(num))
        while os.path.exists(fout):         
            num = num +1
            fout = os.path.join(self.path, 'acquisiti', 'fatmicro.'+str(num))
        os.rename(self.path_file, fout)

            
        return out_dict   
    
       
          
            
            
        
    
