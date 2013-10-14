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

from tg.predicates import has_permission

from tgext.asyncjob import asyncjob_perform

def testme(arg):
    print "====================== TESTME"
    
__all__ = ['B2bController']

class B2bController(BaseController):
    """
    """

    # The predicate that must be met for all the actions in this controller:
    #allow_only = has_permission('manage',
    #                            msg=l_('Only for people with the "manage" permission'))

    @expose('ebetl.templates.b2b')
    def index(self):
        """Handle the front-page."""
        results = DBSession.query(Inputb2b).order_by(Inputb2b.processed, Inputb2b.updated).all()
        return dict(page='b2b', results=results) 

    def create(self):
        """POST /stocks: Create a new item"""
        # url('stocks')

    def new(self, format='html'):
        """GET /stocks/new: Form to create a new item"""
        # url('new_stock')

    @expose()
    def export(self, id, *args, **kw):
        """PUT /stocks/id: Update an existing item"""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="PUT" />
        # Or using helpers:
        #    h.form(url('stock', id=ID),
        #           method='put')
        # url('stock', id=ID)
        #DBSession.query(Inputb2b).filter(
        #                            Inputb2b.b2b_id==id).update(dict(exported=1))
        from ebetl.lib.etl.b2b import B2bObj                                    
        b2bobj=B2bObj(config)                  
        #b2bobj.write_out()
        #if self.options.export:
        
        print asyncjob_perform(testme, 2)
        return redirect(url('/b2b/show/%s'%id))


    @expose()
    def book(self, id, *args, **kw):
        """PUT /stocks/id: Update an existing item"""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="PUT" />
        # Or using helpers:
        #    h.form(url('stock', id=ID),
        #           method='put')
        # url('stock', id=ID)
        DBSession.query(Inputb2b).filter(
                                    Inputb2b.b2b_id==id).update(dict(booked=1))
        DBSession.query(Factb2b).filter_by(inputb2b_id=id).update(dict(booked=1))

        return redirect(url('/b2b/show/%s'%id))

    @expose()
    def update(self, id):
        """PUT /stocks/id: Update an existing item"""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="PUT" />
        # Or using helpers:
        #    h.form(url('stock', id=ID),
        #           method='put')
        # url('stock', id=ID)
        ret = DBSession.query(Inputb2b).filter(
                                    Inputb2b.b2b_id==id).one()   
        from ebetl.lib.etl.filconad import FilconadObj
        fobj = FilconadObj(config, ret.record)  
        fobj.write_out(inputb2b_id=id)   
        return redirect(url('/b2b/show/%s'%id))

    @expose()
    def updatedoc(self, id, doc_num, *args, **kw):
        """PUT /stocks/id: Update an existing item"""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="PUT" />
        # Or using helpers:
        #    h.form(url('stock', id=ID),
        #           method='put')
        # url('stock', id=ID)
        print [args]
        print [kw]
        DBSession.query(Factb2b).filter_by(inputb2b_id=id,doc_num=doc_num ).update(dict(validated=1))
        redirect(url('/b2b/showdoc/%s/%s'%(id,doc_num))) 

    def delete(self, id):
        """DELETE /stocks/id: Delete an existing item"""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="DELETE" />
        # Or using helpers:
        #    h.form(url('stock', id=ID),
        #           method='delete')
        # url('stock', id=ID)


    def _datagrid(self, query_lst , groupby, fltr):
        ret = DBSession.query(*query_lst)
        #ret = ret.order_by(Factb2b.row)
        ret = ret.group_by(*groupby).filter(and_(*fltr))
        return ret.all()
 
 
    @expose('ebetl.templates.b2b_show')
    def show(self, id):
        """GET /b2b/id: Show a specific item"""
        inputb2b = DBSession.query(Inputb2b).filter(Inputb2b.b2b_id==id).one()
        groupby = [Factb2b.booked, Factb2b.validated, Provenienze, Factb2b.doc_date, Factb2b.doc_num]
        query_lst = groupby + FACT_B2B
        fltr = [and_(
                    Provenienze.numeroprovenienza==Factb2b.supplier_id,
                    Factb2b.inputb2b_id == id
                )
                ]            
        results = self._datagrid(query_lst, groupby, fltr)
        return dict(page='b2b', id=id, inputb2b=inputb2b, results=results) 

 
    @expose('ebetl.templates.b2b_showdoc')
    def showdoc(self, id, doc_num):
        """Handle the front-page."""
        """GET /shodoc/id: Show a specific item"""

        results = OrderedDict()
        for i in ['total' , 'account_code', 'vat_code', 
                    'recs', 'issues']:
            results[i]=None

        # Total                          
        groupby = [Factb2b.validated, Factb2b.closed, 
                    Provenienze, Factb2b.inputb2b_id, Factb2b.doc_date, Factb2b.doc_num]
        query_lst = groupby + FACT_B2B
        fltr = [and_(Factb2b.inputb2b_id==id,
                     Factb2b.doc_num == doc_num,
                     Factb2b.supplier_id==Provenienze.numeroprovenienza)]              
        results['total'] = self._datagrid(query_lst, groupby, fltr)                                        
        # Account                            
        groupby = [Factb2b.doc_num,Factb2b.cost_center_code, Factb2b.account_code, Factb2b.b2b_vat_code]
        query_lst = groupby + FACT_B2B
        
        fltr = [and_(Factb2b.inputb2b_id==id,
                     Factb2b.doc_num == doc_num,
                     Factb2b.supplier_id==Provenienze.numeroprovenienza)]            
        results['account_code'] = self._datagrid(query_lst, groupby, fltr)
                
        # Vat
        groupby = [Factb2b.doc_num, Factb2b.cost_center_code, Factb2b.b2b_vat_code]
        query_lst = groupby + FACT_B2B
        fltr = [and_(Factb2b.inputb2b_id==id,
                     Factb2b.doc_num == doc_num,
                     Factb2b.supplier_id==Provenienze.numeroprovenienza)]              
        results['vat_code'] = self._datagrid(query_lst, groupby, fltr) 

        # Receipts
        recs = [i[0] for i in DBSession.query(Factb2b.rec_num).filter(
                                and_(Factb2b.doc_num==doc_num,
                                    Factb2b.inputb2b_id==id)).distinct().all()]
        results['recs'] = []
        for rec_num in recs:
            
            groupby = [Factb2b.doc_num, Factb2b.rec_num]
            query_lst = groupby + FACT_B2B
            fltr = [Factb2b.doc_num==doc_num,Factb2b.inputb2b_id==id,
                Factb2b.rec_num==rec_num
                 ] 
            results['recs'].append(self._datagrid(query_lst, groupby, fltr)[0]) 

        # Issues
        fltr = [Factb2b.inputb2b_id==id,
                Factb2b.doc_num == doc_num,
                Factb2b.account_id==None ]              
        results['issues'] = DBSession.query(Factb2b).filter(and_(*fltr)).all()
                 
        # Products
        groupby = [Factb2b.doc_num, Factb2b.account_code, 
                   Factb2b.b2b_code, Factb2b.b2b_desc]
        query_lst = groupby + FACT_B2B_PRICE
        fltr =   [Factb2b.inputb2b_id==id,
                     Factb2b.doc_num == doc_num,]       
        results['products'] = self._datagrid(query_lst, groupby, fltr) 
        
        return dict(page='b2b', results=results, id=id, doc_num=doc_num)   

        


    def edit(self, id, format='html'):
        """GET /stocks/id/edit: Form to edit an existing item"""
        # url('edit_stock', id=ID)     


