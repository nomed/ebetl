# -*- coding: utf-8 -*-
"""
Auth* related model.

This is where the models used by the authentication stack are defined.

It's perfectly fine to re-use this definition in the ebetl application,
though.

"""
import os, sys
from datetime import datetime, time
from hashlib import sha256
from struct import unpack
from collections import namedtuple
from sqlalchemy import Table, ForeignKey, Column, Sequence, and_, or_
from sqlalchemy.types import Unicode, Integer, BigInteger, DateTime, Float, String
from sqlalchemy.orm import relation, synonym, backref

from sqlalchemy import create_engine, MetaData, Table, and_, Float, select, func
from ebetl.model import * 
from ebetl.lib import get_discount_from_string
from ebetl.lib import strip_non_ascii

class Mapper(object):
    def get_obj(self, value):
        return value
    def get_strip(self, value):       
        if not type(value) in [int, float]:
            value = strip_non_ascii(value)
            value = value.decode("utf-8")
        return str(value).strip()
    def get_zfill6(self,value):
        ret = self.get_strip(value)
        return ret.zfill(6)
    def get_x1000(self,value):
        return float(value)/1000
    def get_x10000(self,value):
        return float(value)/10000        
    def get_x100(self,value):
        return float(value)/100        
    def get_int(self, value):
        try:
            return int(value)
        except:
            return 0
    def get_float(self, value):
        try:
            return float(value)       
        except:
            return 0
    def get_discount(self, value):
        return get_discount_from_string(value)       
    def get_cost_center(self, value)  :
        return  value.strip()
    def get_aammdd(self, value)  :
        d = datetime.strptime(value, "%y%m%d").date()
        return  datetime.combine(d, time())
    def get_vat(self, value)  :
        try:
            return  int(value)
        except:
            return 0
        

class DBSession2(object):

    def __init__(self, config):
        self.config = config
        self.src = config.get('sqlalchemy.url')  
        self.source, self.sengine = self.make_session(self.src)
        print 'done'        
        self.smeta = MetaData(bind=self.sengine)     
        print 'done'              
        #self.smeta.reflect(self.sengine)
        print 'done'

    def make_session(self,connection_string):    
        if connection_string.startswith('firebird'):
            engine = create_engine(connection_string, echo=False,
                                   convert_unicode=False)
        else:
            engine = create_engine(connection_string, echo=False,
                                   convert_unicode=True)                                      
        Session = sessionmaker(bind=engine)         
        return Session(), engine
        
    def quick_mapper(self,table):       
        Base = declarative_base()
        class GenericMapper(Base):
            __table__ = table             
        return GenericMapper  

def get_price_discount(price, disc):
    d=disc.split('+')
    ret = price
    for i in d:
        if i:
            ret = float(ret)/(1+(float(i)/100))
    return ret  
      
def get_margin(price, cost):
    return ((price-cost)/cost)*100


"""        
from ebetl.lib.etl import get_latest_cogs, get_latest_fact_cogs
#get_latest_cogs(7080, 1)
get_latest_fact_cogs(28161, 1)
"""

def get_txn(keys, body, line):
    Transaction = namedtuple('Transaction', keys)
    str_format = "<"
    for i in body:
        str_format = str_format + str(i) + 's'
    #txn = Transaction._make(unpack(str_format, line))
    txn = dict(zip(keys,unpack(str_format, line)))
    return txn
