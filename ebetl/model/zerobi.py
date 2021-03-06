# -*- coding: utf-8 -*-
"""
Fact* related model.
"""
import os, sys
from datetime import datetime
from hashlib import sha256
#__all__ = ['User', 'Group', 'Permission']

from sqlalchemy import Table, ForeignKey, Column, Sequence, and_, or_
from sqlalchemy.types import Unicode, Integer, Integer, DateTime, Float, String, Date
from sqlalchemy.orm import relation, synonym, backref
from sqlalchemy.sql import label
from sqlalchemy import func

from ebetl.model import DeclarativeBase, metadata, DBSession, contasincrofield

from sprox.fillerbase import TableFiller
from sprox.tablebase import TableBase

from ebetl.model import *

count_cogs = Sequence('count_cogs')
count_b2b = Sequence('count_b2b')
count_laborcost = Sequence('count_laborcost')


class GoogleAddress(DeclarativeBase):
    __tablename__ = 'dim_google_address'
    logicdelete = Column(DateTime)
    sincrofield = Column(Integer, contasincrofield , autoincrement=True, primary_key=True)
    sincroserverfield = Column(Integer)
    instablog = Column(Integer)
    updtablog = Column(Integer)
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
    sincrofield = Column(Integer, contasincrofield , autoincrement=True, primary_key=True)
    sincroserverfield = Column(Integer)
    instablog = Column(Integer)
    updtablog = Column(Integer)
    doc_id = Column(Integer)
    doc_date = Column(Date)
    revenue_account_code = Column(String(20))
    revenue_account_name = Column(String(50))
    expense_account_code = Column(String(20))
    expense_account_name = Column(String(50))
    revenue_center_id = Column(Integer)
    cost_center_id = Column(Integer)
    mov_id = Column(Integer, autoincrement=True, primary_key=True)
    mov_date = Column(DateTime)
    prod_id = Column(Integer)
    prod_code = Column(String(20))
    prod_name = Column(String(40))
    ean_id = Column(Integer)
    ean_name = Column(String(13))
    dep_id = Column(Integer)
    dep_code = Column(Integer)
    dep_name = Column(String(20))
    out_vat_id = Column(Integer)
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
    cogs_id = Column(Integer, count_cogs, autoincrement=True, primary_key=True)
    logicdelete = Column(DateTime)
    sincrofield = Column(Integer, contasincrofield , autoincrement=True, primary_key=True)
    sincroserverfield = Column(Integer)
    instablog = Column(Integer)
    updtablog = Column(Integer)
    doc_id = Column(Integer)
    doc_date = Column(DateTime)
    cost_center_id = Column(Integer)
    prov_id = Column(Integer)
    mov_id = Column(Integer, autoincrement=True, primary_key=True)
    mov_date = Column(DateTime)
    prod_id = Column(Integer)
    prod_code = Column(String(20))
    prod_name = Column(String(40))
    ean_id = Column(Integer)
    cost = Column(Float)

class Factlaborcost(DeclarativeBase):
    """
    http://en.wikipedia.org/wiki/Cost_of_goods_sold
    """
    __tablename__ = 'fact_laborcost'
    laborcost_id = Column(Integer, autoincrement=True, primary_key=True)
    logicdelete = Column(DateTime)
    sincrofield = Column(Integer,  autoincrement=True, primary_key=True)
    sincroserverfield = Column(Integer)
    instablog = Column(Integer)
    updtablog = Column(Integer)
    doc_date = Column(DateTime)
    revenue_account_code = Column(String(12))
    expense_account_code = Column(String(12))
    cost_center_id = Column(Integer)
    total = Column(Float)
    code01 = Column(String(2))
    code01_label = Column(Unicode(10))
    code02 = Column(String(4))
    code02_label = Column(Unicode(30))
    notes = Column(Unicode(20))
    fiscal_code = Column(String(16))
    code03 = Column(String(8))
    employee_code = Column(String(8))
    code04 = Column(String(2))
    code05 = Column(String(3))
    code06 = Column(String(30))


class Factb2b(DeclarativeBase):
    """
    http://en.wikipedia.org/wiki/Cost_of_goods_sold
    """
    __tablename__ = 'fact_b2b'
    b2b_id = Column(Integer, count_b2b, autoincrement=True, primary_key=True)
    inputb2b_id = Column(Integer, ForeignKey('input_b2b.b2b_id'))
    inputb2b = relation(Inputb2b, backref="facts")
    logicdelete = Column(DateTime)
    sincrofield = Column(Integer, contasincrofield , autoincrement=True)
    sincroserverfield = Column(Integer)
    instablog = Column(Integer)
    updtablog = Column(Integer)
    supplier_id = Column(Integer)#, ForeignKey('provenienze.numeroprovenienza'))
    @property
    def supplier(self):
        return DBSession.query(Provenienze).filter_by(numeroprovenienza=self.supplier_id).one()
    #supplier = relation(Provenienze)
    header = Column(String(20))
    row = Column(String(20))
    doc_date = Column(DateTime)
    doc_num = Column(String(20))
    doc_id = Column(Integer) # Invoice id
    doc_row = Column(Integer) # Invoice row id
    cost_center_code = Column(String(20))
    rec_date  = Column(DateTime)
    rec_num  = Column(String(20))
    rec_id = Column(Integer) # Receipt id
    rec_row = Column(Integer) # Receipt row id
    fam_id = Column(Integer)
    fam_code = Column(String(20))
    fam_desc = Column(String(250))
    account_id = Column(Integer)
    account_code = Column(String(50))
    account_desc = Column(String(50))
    item_id = Column(Integer)
    item_code = Column(String(20))
    item_desc = Column(String(250))
    item_plu = Column(String(20))
    item_ean_id = Column(Integer)
    item_ean = Column(String(13))
    item_conf = Column(Integer)
    supplier_item_id = Column(Integer)
    supplier_item_code = Column(String(20))
    supplier_item_unit_price = Column(Float)
    supplier_item_discount = Column(Float)
    b2b_cost_center = Column(String(20))
    b2b_code = Column(String(20))
    b2b_desc = Column(String(250))
    b2b_unit_price = Column(Float)
    b2b_disc = Column(Float, default=1)
    b2b_vat_code = Column(Integer)
    b2b_uom = Column(String(2))
    b2b_uom_qty = Column(Float)


    b2b_qty = Column(Float)
    b2b_net_total = Column(Float)
    b2b_sale_type = Column(Integer)
    b2b_mov_type = Column(Integer)
    booked = Column(Integer, default=0)
    closed = Column(Integer, default=0)
    # used only in b2b (helper status for bookkeeprt)
    validated = Column(Integer, default=0)

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
