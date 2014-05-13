# -*- coding: utf-8 -*-
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
    (180, 198, 'uso_futuro'),
    (198, 203, 'codice_plu'),
    (203, 208, 'codice_bil'),
	]
	
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



"""
import csv
tracciato= csv.reader(open('fatmicro.csv'), delimiter=';', quoting=csv.QUOTE_ALL)
for i in tracciato:
    print  "(%s,%s,'%s'),"%(int(i[3])-1,int(i[4]),i[0] )
"""
