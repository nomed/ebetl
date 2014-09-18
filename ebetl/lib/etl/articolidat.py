# -*- coding: utf-8 -*-
import sys, os, traceback, optparse
import time
import re
import csv
#from pexpect import run, spawn


"""
GruppiPosST
codici Gruppi Pos separati da pipe es ;GruppiPosST=|1|3|;
 
FidelityST
codici Gruppi Fidelity separati da pipe es ;FidelityST=|0|1|3|;
|0| rappresenta i senza fidelity
 
CodicePromo
CodicePromozione di raggruppamento, alfanumerico di 20 car. es ;CodicePromo=P478;
 
QtaPezziMin
Pezzi minimi di acquisto es ;QtaPezziMin=3;
 
ScontoVal (2 decimali)
sconto 1,50 es  ;ScontoVal=150;
 
ScontoPer (2 decimali)
 
QtaPaghi
utile per mxn, 3x2 es ;QtaPaghi=2;
 
Punti
Punti extra erogati dalla promo es ;Punti=1;
 
Le promozioni saranno agganciate a promozioni già esistenti in base al CodicePromo
se non c'è un codice promo di raggruppamento, verifica se è già presente una Testata promozione non in corso con Date e TipoPromo uguali
Per i dati non valorizzati saranno presi quelli configurati di default sul “tipo promozione”
 
se servono altri parametri da gestire basta farmelo sapere
 
esempio di tracciato
 
T01SCOPER              2006073120060813Offerta Sconto 15%                             ScontoPer=15;CodicePromo=2006073115;
RP9000019180015       01
T01TGLPRZ              2006073120060813Offerta Taglio Prezzo                            
RP9000019400014       01000229
RP9000019410013       01000229
RP9000019450019       01000099
"""



from babel.numbers import format_currency
def _ensure_unicode(s):
    if isinstance(s, unicode):
        return s
    else:
        return unicode(s,'utf-8','replace')
record = [

	( 0,   13, 'ean'),
	( 13,  33, 'codice_interno'),
	( 33,  34, 'fisso01'),
	( 34,  74, 'descrizione'),
	( 74,  75, 'fisso02'),
	( 75,  79, 'codice_reparto'),
    ( 79,  81, 'codice_iva'),
    ( 81,  85, 'valore_iva'), #x100
    ( 85,  87, 'udm'), 
    ( 87,  94, 'qty_contenuto'), #x1000
    ( 94,  96, 'udm_visualizzazione'), 
    ( 96, 103, 'qty_conf'), #x1000
    (103, 110, 'qty_collo'), #x1000 (imballo)
    (110, 111, 'fisso03'),
    (111, 117, 'prezzo'), #x100
    (117, 123, 'prezzo_2'),
    (123, 129, 'prezzo_3'),
    (129, 135, 'prezzo_4'),
    (135, 143, 'data_variazione'), #AAAAMMGG
    (143, 153, 'codice_cat1'),
    (153, 163, 'codice_cat2'), 
    (163, 164, 'flag'), 
    (164, 171, 'uso_futuro'),
    (171, 172, 'fisso04'),
    (172, 180, 'costo'), #x1000 (netto iva)
    (180, 198, 'uso_futuro2'),
    (198, 203, 'codice_plu'),
    (203, 208, 'codice_bil'),
	]

record_dict = {}

for r in record:
    record_dict[r[2]]=r[1]-r[0]

	
	
# ;GruppiPosST=|3|
# ;FidelityST
# ;QtaPezziMin
# ;ScontoVal
# ;ScontoPer
# ;QtaPaghi
# ;Punti
 
record_offerte_t = [
    (0,1,'testata'),
    (1,2, 'set_molteplicita'),
    (2,23, 'codicepromozione'),
    (23,31, 'data_inizio'),
    (31,39, 'data_fine'),
    (39,89, 'descrizione'),
]

record_offerte_r = [
    (0,1,'testata'),
    (1,2, 'tipo_prodotto'), # E-P-R-T-A) 
    (2,22, 'codice'),#
    (23,24, 'set_molteplicita'),
    (24,30, 'valore'),# valore taglio prezzo x100
    (30,38, 'descrizione'),# x10000
]


"""
class Ind(object):

    ean_file_name = 'LEG_EAN.csv'
    plu_file_name = 'ART_ANAG.csv'
    
    def __init__(self, path_input=None, *args, **kw):
        self.path_input = os.path.join(path_input, 'anag', 'ind')
    
    def _get_plu_file_path(self):
        return os.path.join(self.path_input, plu_file_name)
    
    plu_file_path = property(_get_plu_file_path)
    
    def _get_ean_file_path(self):
        return os.path.join(self.path_input, ean_file_name)
        
    ean_file_path = property(_get_ean_file_path)
    
    def get_div100(self, s):
        return round(float(s)/100,2)
    def get_int(self,s):
        return round(int(s),2)
        
    def _get_ean(self):
        
    ean = property(_get_ean, _set_ean)
    
    def export(self, *args, **kw):
        pass

"""
class ToDat(object):
    ean_file_name = 'LEG_EAN.csv'
    plu_file_name = 'TEan.csv'
    prefix = '_todat'
        
    def __init__(self, path_input=None, *args, **kw):
        self.path_input = os.path.join(path_input, 'input', self.prefix)
    
    def _get_plu_file_path(self):
        return os.path.join(self.path_input, self.plu_file_name)
    
    plu_file_path = property(_get_plu_file_path)

    def _out_plu_file_path(self):
        return os.path.join(self.path_input, 'Articoli.dat')
    
    out_file_path = property(_out_plu_file_path)
    
    def _get_ean_file_path(self):
        return os.path.join(self.path_input, self.ean_file_name)
        
    ean_file_path = property(_get_ean_file_path)
    
    def get_div100(self, s):
        return round(float(s)/100,2)
    def get_int(self,s):
        return round(int(s),2)

    def read(self):
        spamreader = csv.reader(open(self.plu_file_path), delimiter=';', quotechar='"')  
        ret = [r for r in spamreader] 
        return ret

    def convert_row(self, row):
        pass

    def write(self):
        pass       

class Gamba(ToDat):
    ean_file_name = 'LEG_EAN.csv'
    plu_file_name = 'TEan.csv'
    prefix = 'gamba'
    codice_interno = 1
    ean = 4
    descrizione = 3
    prezzo = 15
    codice_iva = 6
    codice_reparto = 5
    def convert_item(self, key, val):
        if key == 'prezzo':
            val = int(float(val)*100)
        return str(val)
    
    def convert_row(self, row):
        ret = {}
        for key, rec in record_dict.iteritems():
            ch = ' '*rec
            if key in ['fisso01', 'fisso02']:
                ch = '-'
            elif key in ['fisso03','fisso04']:
                ch = '*'  
            if hasattr(self, key):
                ch = self.convert_item(key, row[getattr(self, key)-1])                             
                if len(ch) < rec:
                    ch = ' '*(rec-len(ch))+ch                    
            ret[key]=ch[0:rec]

        return ret
        
    def write(self):
        lines = self.read()
        f = open(self.out_file_path,'ab')
        
        for line in lines[1:]:
            row = self.convert_row(line)
            art = ''
            for i in record:
                #print art
                art = art + row.get(i[2])
                #print i , [row.get(i[2])]               
            print >> f, art
        f.close()
        
        



def main ():

    global options, args
    # TODO: Do something more interesting here...
    print 'Hello world!'

if __name__ == '__main__':
    try:
        start_time = time.time()
        parser = optparse.OptionParser(formatter=optparse.TitledHelpFormatter(), usage=globals()['__doc__'], version='$Id$')
        parser.add_option ('-v', '--verbose', action='store_true', default=False, help='verbose output')
        parser.add_option ('-g', '--gamba', action='store_true', default=False, help='gamba')
        (options, args) = parser.parse_args()
        print args
        if len(args) < 1:
            parser.error ('missing argument')
        source = args[0]
            
        if options.verbose: print time.asctime()
        main()
        if options.gamba:
            obj = Gamba(source)
            print obj.write()

        if options.verbose: print time.asctime()
        if options.verbose: print 'TOTAL TIME IN MINUTES:',
        if options.verbose: print (time.time() - start_time) / 60.0
        sys.exit(0)
    except KeyboardInterrupt, e: # Ctrl-C
        raise e
    except SystemExit, e: # sys.exit()
        raise e
    except Exception, e:
        print 'ERROR, UNEXPECTED EXCEPTION'
        print str(e)
        traceback.print_exc()
        os._exit(1)

"""
import csv
tracciato= csv.reader(open('fatmicro.csv'), delimiter=';', quoting=csv.QUOTE_ALL)
for i in tracciato:
    print  "(%s,%s,'%s'),"%(int(i[3])-1,int(i[4]),i[0] )
"""
