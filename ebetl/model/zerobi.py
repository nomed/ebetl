# -*- coding: utf-8 -*-
"""
Fact* related model.
"""
import os, sys
from datetime import datetime
from hashlib import sha256
#__all__ = ['User', 'Group', 'Permission']

from sqlalchemy import Table, ForeignKey, Column, Sequence, and_, or_
from sqlalchemy.types import Unicode, Integer, BigInteger, DateTime, Float, String, Date
from sqlalchemy.orm import relation, synonym, backref
from sqlalchemy.sql import label
from sqlalchemy import func

from ebetl.model import DeclarativeBase, metadata, DBSession, contasincrofield 

from sprox.fillerbase import TableFiller
from sprox.tablebase import TableBase

from ebetl.model import *

count_cogs = Sequence('count_cogs')
count_b2b = Sequence('count_b2b')


class GoogleAddress(DeclarativeBase):
    __tablename__ = 'dim_google_address'
    logicdelete = Column(DateTime)
    sincrofield = Column(BigInteger, contasincrofield , autoincrement=True, primary_key=True)
    sincroserverfield = Column(BigInteger)  
    instablog = Column(BigInteger)  
    updtablog = Column(BigInteger)     
    google_address_id = Column(Integer, primary_key=True)
    accuracy = Column(Integer, nullable=False)
    google_lat = Column(Float, nullable=False)
    google_lng = Column(Float, nullable=False)
    country_name_code = Column(Unicode(2))
    country_name = Column(Unicode(255))
    administrative_area_name = Column(Unicode(255))
    sub_administrative_area_name = Column(Unicode(255))
    locality_name = Column(Unicode(255))
    dependent_locality_name =  Column(Unicode(255))
    thoroughfare_name = Column(Unicode(255))
    google_address = Column(Unicode(255))
    postal_code_number = Column(Unicode(255))

class FactMovs(DeclarativeBase):
    __tablename__ = 'fact_movs'
    logicdelete = Column(DateTime)
    sincrofield = Column(BigInteger, contasincrofield , autoincrement=True, primary_key=True)
    sincroserverfield = Column(BigInteger)  
    instablog = Column(BigInteger)  
    updtablog = Column(BigInteger)      
    doc_id = Column(BigInteger)     
    doc_date = Column(Date)
    revenue_account_code = Column(String(20))
    revenue_account_name = Column(String(50))    
    expense_account_code = Column(String(20))
    expense_account_name = Column(String(50))       
    revenue_center_id = Column(BigInteger)  
    cost_center_id = Column(BigInteger)  
    mov_id = Column(BigInteger, autoincrement=True, primary_key=True)  
    mov_date = Column(DateTime)
    prod_id = Column(BigInteger) 
    prod_code = Column(String(20))
    prod_name = Column(String(40))
    ean_id = Column(BigInteger) 
    ean_name = Column(String(13))
    dep_id = Column(BigInteger) 
    dep_code = Column(BigInteger) 
    dep_name = Column(String(20))
    out_vat_id = Column(BigInteger) 
    out_qty = Column(Float)
    out_vat_perc = Column(Float)
    out_net_cos = Column(Float)
    out_vat_cos = Column(Float)
    out_gross_cos = Column(Float)
    out_net_total_cos = Column(Float)
    out_vat_totalcos = Column(Float)
    out_gross_total_cos = Column(Float)
    out_net_start_price = Column(Float)
    out_vat_start_price = Column(Float)    
    out_gross_start_price = Column(Float)
    out_net_price = Column(Float)
    out_vat_price = Column(Float)
    out_gross_price = Column(Float)
    out_net_total = Column(Float)
    out_vat_total = Column(Float)
    out_gross_total = Column(Float)
    in_vat_id = Column(Float)
    in_qty = Column(Float)
    in_vat_perc = Column(Float)
    in_net_cos = Column(Float)
    in_vat_cos = Column(Float)
    in_gross_cos = Column(Float)
    in_net_total_cos = Column(Float)
    in_vat_totalcos = Column(Float)
    in_gross_total_cos = Column(Float)
    in_net_start_price = Column(Float)
    in_vat_start_price = Column(Float)
    in_gross_start_price = Column(Float)
    in_net_price = Column(Float)
    in_vat_price = Column(Float)
    in_gross_price = Column(Float)
    in_net_total = Column(Float)
    in_vat_total = Column(Float)
    in_gross_total = Column(Float)
    cancel_date = Column(DateTime)


class Factcogs(DeclarativeBase):
    """
    http://en.wikipedia.org/wiki/Cost_of_goods_sold
    """
    __tablename__ = 'fact_cogs'
    cogs_id = Column(BigInteger, count_cogs, autoincrement=True, primary_key=True)
    logicdelete = Column(DateTime)
    sincrofield = Column(BigInteger, contasincrofield , autoincrement=True, primary_key=True)
    sincroserverfield = Column(BigInteger)  
    instablog = Column(BigInteger)  
    updtablog = Column(BigInteger)      
    doc_id = Column(BigInteger)     
    doc_date = Column(DateTime)       
    cost_center_id = Column(BigInteger)  
    prov_id = Column(BigInteger)  
    mov_id = Column(BigInteger, autoincrement=True, primary_key=True)  
    mov_date = Column(DateTime)
    prod_id = Column(BigInteger) 
    prod_code = Column(String(20))
    prod_name = Column(String(40))
    ean_id = Column(BigInteger)  
    cost = Column(Float)


class Factb2b(DeclarativeBase):
    """
    http://en.wikipedia.org/wiki/Cost_of_goods_sold
    """
    __tablename__ = 'fact_b2b'
    b2b_id = Column(BigInteger, count_b2b, autoincrement=True, primary_key=True)
    inputb2b_id = Column(Integer, ForeignKey('input_b2b.b2b_id'))   
    inputb2b = relation(Inputb2b)
    logicdelete = Column(DateTime)
    sincrofield = Column(BigInteger, contasincrofield , autoincrement=True)
    sincroserverfield = Column(BigInteger)  
    instablog = Column(BigInteger, ForeignKey('movimentit.numeromovimento'))  
    source = relation(Movimentit)
    updtablog = Column(BigInteger)      
    supplier_id = Column(BigInteger, ForeignKey('provenienze.numeroprovenienza')) 
    supplier = relation(Provenienze)   
    header = Column(String(20))
    row = Column(String(20))
    doc_num = Column(String(20))
    doc_date = Column(DateTime)
    cost_center_code = Column(String(20))
    rec_date  = Column(DateTime)
    rec_num  = Column(String(20))
    fam_id = Column(BigInteger)  
    fam_code = Column(String(20))
    fam_desc = Column(String(50))
    account_id = Column(BigInteger) 
    account_code = Column(String(50))
    account_desc = Column(String(50))
    item_id = Column(BigInteger)
    item_code = Column(String(20))
    item_desc = Column(String(50))
    item_plu = Column(String(20))
    item_ean = Column(String(13))
    item_conf = Column(BigInteger)
    supplier_item_code = Column(String(20))
    supplier_item_unit_price = Column(Float)
    supplier_item_discount = Column(Float)
    b2b_code = Column(String(20))
    b2b_desc = Column(String(50))   
    b2b_unit_price = Column(Float)
    b2b_disc = Column(Float, default=1)     
    b2b_vat_code = Column(Integer)
    b2b_uom = Column(String(2))
    b2b_uom_qty = Column(Float)    
    b2b_qty = Column(Float)    
    b2b_net_total = Column(Float)
    b2b_sale_type = Column(Integer)
    b2b_mov_type = Column(Integer)    
 


# document final price
vat_total = Factb2b.b2b_net_total * Factb2b.b2b_vat_code/100
gross_total = Factb2b.b2b_net_total + vat_total
# pricelist final price
lis_fp =  Factb2b.supplier_item_discount*Factb2b.supplier_item_unit_price
# contract total
lis_ct = lis_fp * Factb2b.b2b_uom_qty
b2b_fp = Factb2b.b2b_unit_price*Factb2b.b2b_disc
#measures
FACT_B2B = [
        label('lines', func.count(Factb2b.b2b_id)),
        label('net_total', func.sum(Factb2b.b2b_net_total)),
        label('vat_total', func.sum(vat_total)),        
        label('gross_total', func.sum(gross_total)),         
        label('lis_ct', func.sum(lis_ct)),
        label('disc', func.sum(
            Factb2b.b2b_net_total  - lis_ct
            
        ))                                   
        ]
        
FACT_B2B_PRICE =  [
        label('unit_price', func.avg(b2b_fp )),
        label('unit_price_contract', func.avg(lis_fp)),                
        label('diff_unit_price',  func.avg(
            b2b_fp - lis_fp )),
        label('b2b_uom_qty', func.sum(Factb2b.b2b_uom_qty)),            
        label('net_total',  func.sum(
            Factb2b.b2b_net_total ))            
        ]      
