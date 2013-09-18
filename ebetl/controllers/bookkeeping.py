# -*- coding: utf-8 -*-
"""Main Controller"""
import pylons
from tg import expose, flash, require, url, lurl, request, redirect, tmpl_context
from tg.i18n import ugettext as _, lazy_ugettext as l_
from tg import predicates
from ebetl import model
from ebetl.controllers.secure import SecureController
from ebetl.model import DBSession, metadata
from tgext.admin.tgadminconfig import TGAdminConfig
from tgext.admin.controller import AdminController
from ebetl.lib.base import BaseController
from ebetl.controllers.error import ErrorController
from ebetl.model import *

from ebetl.model.zerobi import FACT_B2B,FACT_B2B_PRICE


from ebetl.lib import views
from ebetl.lib.views import get_latest_cogs as gcogs
from webhelpers import paginate
from babel.numbers import format_currency, format_decimal
from decimal import Decimal

from sqlalchemy.sql import label
from sqlalchemy import func

try:
    from collections import OrderedDict
except:
    from ordereddict import OrderedDict

    
__all__ = ['BookkeepingController']

       

class BookkeepingController(BaseController):
    """    
    Bookkeeping Controller
    
    http://en.wikipedia.org/wiki/Bookkeeping
    
    Bookkeeping in the context of a business is simply the recording of financial 
    transactions. Transactions include 
    
    * purchases
    * sales
    * receipts
    * payments 
    
    by an individual or organization. 
    Many individuals mistakenly consider bookkeeping and accounting to be the 
    same thing. 
    
    This confusion is understandable because the accounting process includes 
    the bookkeeping function, but is just one part of the accounting process. 
    
    The accountant creates reports from the recorded financial transactions 
    recorded by the bookkeeper and files forms with government agencies. 
    
    There are some common methods of bookkeeping such as the single-entry 
    bookkeeping system and the double-entry bookkeeping system. 
    
    But while these systems may be seen as "real" bookkeeping, any process that 
    involves the recording of financial transactions is a bookkeeping process.
    
    """
    
    def _datagrid(self, query_lst , groupby, fltr):
        ret = DBSession.query(*query_lst)
        #ret = ret.order_by(Factb2b.row)
        ret = ret.group_by(*groupby).filter(and_(*fltr))
        return ret.all()    
    
    @expose('ebetl.templates.bookkeeping')
    def index(self):
        """Handle the front-page."""
        groupby = [Factb2b.booked, Factb2b.closed, Provenienze, Factb2b.doc_id, Factb2b.doc_date, Factb2b.doc_num]
        query_lst = groupby + FACT_B2B
        fltr = [and_(
                    Provenienze.numeroprovenienza==Factb2b.supplier_id,
                    Factb2b.doc_id != None
                )
                ]            
        results = self._datagrid(query_lst, groupby, fltr)
        return dict(page='bookkeeping', results=results) 

    def create(self):
        """POST /backoffice: Create a new item"""
        # url('stocks')

    def new(self, format='html'):
        """GET /backoffice/new: Form to create a new item"""
        # url('new_stock')

    @expose()
    def update(self, id, *args, **kw):
        """PUT /backoffice/id: Update an existing item"""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="PUT" />
        # Or using helpers:
        #    h.form(url('stock', id=ID),
        #           method='put')
        # url('stock', id=ID)
        DBSession.query(Factb2b).filter_by(doc_id=id).update(dict(booked=1))
        redirect(url('/bookkeeping/show/%s'%id))

    def delete(self, id):
        """DELETE /backoffice/id: Delete an existing item"""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="DELETE" />
        # Or using helpers:
        #    h.form(url('stock', id=ID),
        #           method='delete')
        # url('stock', id=ID)

    @expose('ebetl.templates.bookkeeping_show')
    def show(self, id):
        """Handle the front-page."""
        """GET /bookkeeping/id: Show a specific item"""

        results = OrderedDict()
        for i in ['total' , 'account_code', 'vat_code', 
                    'recs', 'issues']:
            results[i]=None

        # Total                          
        groupby = [Factb2b.booked, Factb2b.closed, 
                    Provenienze, Factb2b.doc_id, Factb2b.doc_date, Factb2b.doc_num]
        query_lst = groupby + FACT_B2B
        fltr = [and_(Factb2b.doc_id==id,
                     Factb2b.supplier_id==Provenienze.numeroprovenienza)]              
        results['total'] = self._datagrid(query_lst, groupby, fltr)                                        
        # Account                            
        groupby = [Factb2b.doc_num,Factb2b.cost_center_code, Factb2b.account_code, Factb2b.b2b_vat_code]
        query_lst = groupby + FACT_B2B
        
        fltr = [Factb2b.doc_id==id ]            
        results['account_code'] = self._datagrid(query_lst, groupby, fltr)
                
        # Vat
        groupby = [Factb2b.doc_num, Factb2b.cost_center_code, Factb2b.b2b_vat_code]
        query_lst = groupby + FACT_B2B
        fltr = [Factb2b.doc_id==id]              
        results['vat_code'] = self._datagrid(query_lst, groupby, fltr) 

        # Receipts
        recs = [i[0] for i in DBSession.query(Factb2b.rec_num).filter(
                                Factb2b.doc_id==id).distinct().all()]
        results['recs'] = []
        for rec_num in recs:
            
            groupby = [Factb2b.doc_num, Factb2b.rec_num]
            query_lst = groupby + FACT_B2B
            fltr = [Factb2b.doc_id==id,
                Factb2b.rec_num==rec_num
                 ] 
            results['recs'].append(self._datagrid(query_lst, groupby, fltr)[0]) 

        # Issues
        fltr = [Factb2b.doc_id==id,
                Factb2b.account_id==None ]              
        results['issues'] = DBSession.query(Factb2b).filter(and_(*fltr)).all()
                 
        # Products
        groupby = [Factb2b.doc_num, Factb2b.account_code, 
                   Factb2b.b2b_code, Factb2b.b2b_desc]
        query_lst = groupby + FACT_B2B_PRICE
        fltr =   [Factb2b.doc_id==id]       
        results['products'] = self._datagrid(query_lst, groupby, fltr) 
        
        return dict(page='bookkeeping', results=results, id=id)   
