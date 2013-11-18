# -*- coding: utf-8 -*-
"""Main Controller"""
import pylons
from tg import expose, flash, require, url, lurl, request, redirect, tmpl_context, config
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

from ebetl.controllers.bookkeeping import BookkeepingController
from ebetl.controllers.b2b import B2bController
from ebetl.controllers.marketing import MarketingController, RepartiController, TipologieController, ProduttoriController
try:
    from collections import OrderedDict
except:
    from ordereddict import OrderedDict

from tg.predicates import has_permission

def todecimal(floatnum):
    if not floatnum:
        floatnum = 0
   
    return format_decimal(Decimal(str(floatnum)),format="###0.00", locale='en')
    
__all__ = ['RootController']



class ModalController(BaseController):
    """
    """

    @expose('ebetl.templates.modal.product')
    def product(self, id):
        """"""
        ret = DBSession.query(Prodotti )
        
        ret = ret.filter(Prodotti.numeroprodotto==id)
        ret = ret.one() 
        
        return dict(page='modal',result=ret)  

    @expose('ebetl.templates.modal.bookkeeping_book')
    def bookkeeping_book(self, id):
        """"""       
        return dict(page='modal',id=id, result=[id])  

    @expose('ebetl.templates.modal.b2bdoc_validate')
    def b2bdoc_validate(self, id, doc_num):
        """"""       
        return dict(page='modal',id=id, doc_num=doc_num, result=[id])  


    @expose('ebetl.templates.modal.b2b_book')
    def b2b_book(self, id):
        """"""       
        validated = DBSession.query(Factb2b).filter(and_(
            Factb2b.inputb2b_id == id,
            Factb2b.validated != 1
        )).all()
        return dict(page='modal',id=id,validated=validated, result=[id])  

    @expose('ebetl.templates.modal.b2b_book')
    def b2b_export(self, id):
        """"""       
        validated = DBSession.query(Factb2b).filter(and_(
            Factb2b.inputb2b_id == id,
            Factb2b.booked != 1
        )).all()
        return dict(page='modal',id=id,validated=validated, result=[id])  

class StockController(BaseController):
    """
    """

    @expose('ebetl.templates.stock')
    def index(self):
        """Handle the front-page."""
        results = DBSession.query(Inventarit).limit(10).all()
        return dict(page='stock', results=results) 

    def create(self):
        """POST /stocks: Create a new item"""
        # url('stocks')

    def new(self, format='html'):
        """GET /stocks/new: Form to create a new item"""
        # url('new_stock')

    def update(self, id):
        """PUT /stocks/id: Update an existing item"""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="PUT" />
        # Or using helpers:
        #    h.form(url('stock', id=ID),
        #           method='put')
        # url('stock', id=ID)

    def delete(self, id):
        """DELETE /stocks/id: Delete an existing item"""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="DELETE" />
        # Or using helpers:
        #    h.form(url('stock', id=ID),
        #           method='delete')
        # url('stock', id=ID)

    @expose('ebetl.templates.stock_show')
    def show(self, id):
        """GET /stocks/id: Show a specific item"""
        result = views.get_stock(id)
        doc = DBSession.query(Inventarit).filter(Inventarit.numeroinventario==id).one()
           
        return dict(page='stock', doc=doc, result=result)            

    @expose()
    def updatecost(self, id):
        """GET /stocks/id: Show a specific item"""       
        #result = views.get_stock_cogs(id)
        doc = DBSession.query(Inventarit).filter(Inventarit.numeroinventario==id).one()
        invs = DBSession.query(Inventarirconta).filter(Inventarirconta.numeroinventario==id).all()
        for ic in invs:
		    ic.costo, ic.datacosto = gcogs(ic.numeroprodotto, doc.numeromagazzino ,date=doc.datainventario)
		    if not ic.costo2  or ic.costo2 == 0:
				ic.costo2 = ic.costo
		    DBSession.add(ic)
        redirect('/stock/show/'+id)    
    @expose()
    def requestupg(self, id):
        """GET /stocks/id: Show a specific item"""       
    
        date=datetime.now()        
        try:
			obj = DBSession.query(Aggiornaic).filter(Aggiornaic.numeroinventario==id).one()
        except:
            obj = Aggiornaic()
            obj.numeroinventario=id
        obj.richiesta=date
        obj.status = 1
        email = ''
        DBSession.add(obj)
        redirect('/stock/showcost/'+id) 

    @expose('ebetl.templates.stock_show_cost')
    def showcost(self, id, *args):
        """GET /stocks/id: Show a specific item"""       
        result = views.get_stock_cogs(id, *args)
        doc = DBSession.query(Inventarit).filter(Inventarit.numeroinventario==id).one()
           
        return dict(page='stock', doc=doc, result=result) 

    #@expose('ebetl.templates.stock_show_cost')
    #def showreport(self, id, *args):
    #    """GET /stocks/id: Show a specific item"""       
    #    result = views.get_stock_cogs(id, *args)
    #    doc = DBSession.query(Inventarit).filter(Inventarit.numeroinventario==id).one()
    #       
    #    return dict(page='stock', doc=doc, result=result)

    def _datagrid(self, query_lst , groupby, fltr):
        ret = DBSession.query(*query_lst)
        #ret = ret.order_by(Factb2b.row)
        ret = ret.group_by(*groupby).filter(and_(*fltr))
        return ret.all()
 
    def _get_joins(self, ret):
		ret = ret.join(Prodotti, and_(Prodotti.numeroprodotto == Inventarirconta.numeroprodotto)) 
		ret = ret.join(Reparti, and_(Reparti.numeroreparto == Prodotti.numeroreparto))
		ret = ret.join(Gruppireparti, and_(Gruppireparti.numerogrupporeparto == Reparti.numerogrupporeparto))
		return ret
 
    @expose('ebetl.templates.stock_show_report')
    def showreport(self, id, ng=None,nr=None):
        """GET /showreport/id: Show a specific item"""
        doc = DBSession.query(Inventarit).filter(Inventarit.numeroinventario==id).one()
        """
        tables = (
                Inventarirconta, 
                Prodotti, 
                Reparti, 
                Gruppireparti 
                )
        columns = []
        query_args = []
        for m in tables:
            for c in m.__table__.columns:
                if not c in columns:
                    columns.append("%s"%(c))
                    query_args.append(c)
        """            
        totale_costo2 = Inventarirconta.costo2 * Inventarirconta.totale_qta                    
        
        COSTI = [
        
            label('totale_costo', func.sum(totale_costo2)),
        ] 
        fltr_query = [Inventarirconta.numeroinventario==id]
        group = [   Inventarirconta.numeroinventario, 
					Gruppireparti.numerogrupporeparto,
					Gruppireparti.grupporeparto]
        group_tot = [   Inventarirconta.numeroinventario ]
        if ng:
			group = group +[
					Reparti.numeroreparto, 
					Reparti.reparto
				]
			fltr_query = fltr_query + [Gruppireparti.numerogrupporeparto==ng]          
        if nr:
			group = group + [
					Prodotti.numeroprodotto,
					Prodotti.prodotto
			]                        
			fltr_query = fltr_query + [Reparti.numeroreparto==nr]          
        query_args =  group + COSTI
        query_args_tot = group_tot + COSTI
        ret = DBSession.query(*query_args)
        ret_tot = DBSession.query(*query_args_tot)
        fltr = [and_(
                    *fltr_query
                )
                ] 
        ret = ret.filter(*fltr)
        ret_tot = ret_tot.filter(*fltr)	
        ret = self._get_joins(ret)    				
        ret_tot = self._get_joins(ret_tot)
        ret = ret.group_by(*group)     		
        ret_tot = ret_tot.group_by(*group_tot)           
        results = ret.all()        
        totals = ret_tot.all()
        return dict(page='stock', id=id, ng=ng, nr=nr, doc=doc, results=results, totals=totals)

    def edit(self, id, format='html'):
        """GET /stocks/id/edit: Form to edit an existing item"""
        # url('edit_stock', id=ID)           



        


class PurchaseController(BaseController):
    """
    """

    @expose('ebetl.templates.purchase')
    def index(self):
        """Handle the front-page."""
        results = DBSession.query(Provenienze).filter_by(tipoprovenienza='FOR').all()
        return dict(page='purchase', results=results) 

    def create(self):
        """POST /stocks: Create a new item"""
        # url('stocks')

    def new(self, format='html'):
        """GET /stocks/new: Form to create a new item"""
        # url('new_stock')

    def update(self, id):
        """PUT /stocks/id: Update an existing item"""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="PUT" />
        # Or using helpers:
        #    h.form(url('stock', id=ID),
        #           method='put')
        # url('stock', id=ID)

    def delete(self, id):
        """DELETE /stocks/id: Delete an existing item"""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="DELETE" />
        # Or using helpers:
        #    h.form(url('stock', id=ID),
        #           method='delete')
        # url('stock', id=ID)

    @expose('ebetl.templates.supplier_show')
    def show(self, id):
        """GET /stocks/id: Show a specific item"""
        result = views.get_pricelist(id)
        
        ret = DBSession.query(Provenienze).filter(Provenienze.numeroprovenienza==id).one()
           
        return dict(page='stock', ret = ret, result=result)            

    def edit(self, id, format='html'):
        """GET /stocks/id/edit: Form to edit an existing item"""
        # url('edit_stock', id=ID)           



class ItemController(BaseController):
    """
    """

    @expose('ebetl.templates.item')
    def index(self, page=1):
        """Handle the front-page."""
        
                 
        results = DBSession.query(Prodotti)
        pags = paginate.Page(results, page, items_per_page=50)        
        return dict(page='item', results=pags.items, pags=pags) 

    def create(self):
        """POST /stocks: Create a new item"""
        # url('stocks')

    def new(self, format='html'):
        """GET /stocks/new: Form to create a new item"""
        # url('new_stock')

    def update(self, id):
        """PUT /stocks/id: Update an existing item"""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="PUT" />
        # Or using helpers:
        #    h.form(url('stock', id=ID),
        #           method='put')
        # url('stock', id=ID)

    def delete(self, id):
        """DELETE /stocks/id: Delete an existing item"""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="DELETE" />
        # Or using helpers:
        #    h.form(url('stock', id=ID),
        #           method='delete')
        # url('stock', id=ID)

    @expose('ebetl.templates.item_show')
    def show(self, id):
        """GET /stocks/id: Show a specific item"""

        doc = DBSession.query(Inventarit).filter(Inventarit.numeroinventario==id).one()
        if not doc.inventariconta:
            Inventarirconta(numeroinventario=doc.numeroinventario)
            DBSession.add(Inventarirconta)
            DBSession.flush()
        result = views.get_stock(id)            
        return dict(page='stock', doc=doc, result=result)            

    def edit(self, id, format='html'):
        """GET /stocks/id/edit: Form to edit an existing item"""
        # url('edit_stock', id=ID)           


class RootController(BaseController):
    """
    The root controller for the ebetl application.

    All the other controllers and WSGI applications should be mounted on this
    controller. For example::

        panel = ControlPanelController()
        another_app = AnotherWSGIApplication()

    Keep in mind that WSGI applications shouldn't be mounted directly: They
    must be wrapped around with :class:`tg.controllers.WSGIAppController`.

    """
    
    # The predicate that must be met for all the actions in this controller:
   
    
    secc = SecureController()
    admin = AdminController(model, DBSession, config_type=TGAdminConfig)
    
    stock = StockController()

    item = ItemController()
    
    purchase = PurchaseController()
    
    b2b = B2bController()
    
    bookkeeping = BookkeepingController()
    
    marketing = MarketingController()

    modal = ModalController() 
    
    reparti = RepartiController()   

    tipologie = TipologieController() 
    
    produttori = ProduttoriController()     
    
    #error = ErrorController()

    def _before(self, *args, **kw):
        tmpl_context.project_name = "ebetl"

    @expose('ebetl.templates.index')
    def index(self):
        """Handle the front-page."""
        return dict(page='index')

    @expose('')
    def post(self, *args, **kw):
        print [args]
        print [kw]

        
        try:
            pk = kw.get('pk')
            value = kw.get('value')
            if not value:
                value = '0'
            value = float(value)
            name = kw.get('name')
            doc_id, prod_id = pk.split('/')
            if name == 'qta' or name == 'qtaconf':
                p = DBSession.query(Prodotti).filter_by(numeroprodotto = prod_id).one()
                d = DBSession.query(Inventarit).filter_by(numeroinventario = doc_id).one()
                try :
                    ic = DBSession.query(Inventarirconta).filter(and_(
                        Inventarirconta.numeroinventario == doc_id,
                        Inventarirconta.numeroprodotto == prod_id
                        )).one()
                except:
                    ic = Inventarirconta(numeroinventario=doc_id, numeroprodotto=prod_id)
                    ic.qta = 0
                    ic.qtaconf = 0
                    #ic.costo = gcogs(prod_id, d.numeromagazzino ,date=d.datainventario)
                    ic.costo2 = 0
                if not ic.costo:
                    ic.costo = 0
                if not ic.qta:
                    ic.qta = 0
                if not ic.qtaconf:
                    ic.qtaconf = 0
                setattr(ic,name,value)    
                pzxc = p.pezzixcollo or 1                
                ic.totale_qta = ic.qta+ic.qtaconf*pzxc
                ic.totale_costo=ic.totale_qta*ic.costo                
                kw['totale_costo'] = todecimal(ic.totale_costo )
                kw['totale_qta']=todecimal(ic.totale_qta )
                kw['costo'] = todecimal(ic.costo)
                DBSession.add(ic)
            elif name == 'costo2':
                p = DBSession.query(Prodotti).filter_by(numeroprodotto = prod_id).one()
                d = DBSession.query(Inventarit).filter_by(numeroinventario = doc_id).one()
                ic = DBSession.query(Inventarirconta).filter(and_(
                        Inventarirconta.numeroinventario == doc_id,
                        Inventarirconta.numeroprodotto == prod_id
                        )).one()
                
                if not ic.costo:
                    ic.costo = 0
                #if not ic.qta:
                #    ic.qta = 0
                #if not ic.qtaconf:
                #    ic.qtaconf = 0
                setattr(ic,name,value)
                print name, value 
                print ic.costo, ic.costo2   
                #pzxc = p.pezzixcollo or 1                
                #ic.totale_qta = ic.qta+ic.qtaconf*pzxc
                ic.totale_costo=ic.totale_qta*ic.costo2                
                kw['totale_costo'] = todecimal(ic.totale_costo )                
                #kw['costo'] = todecimal(ic.costo)
                DBSession.add(ic)                
        except:
            raise
            pylons.response.status = "400 Error"
            return "Not a valid entry"
        """Handle the front-page."""

        import json
        return json.dumps(kw)

    @expose('ebetl.templates.about')
    def about(self):
        """Handle the 'about' page."""
        return dict(page='about')

    @expose('ebetl.templates.environ')
    def environ(self):
        """This method showcases TG's access to the wsgi environment."""
        return dict(page='environ', environment=request.environ)

    @expose('ebetl.templates.data')
    @expose('json')
    def data(self, **kw):
        """This method showcases how you can use the same controller for a data page and a display page"""
        return dict(page='data', params=kw)
    @expose('ebetl.templates.index')
    @require(predicates.has_permission('manage', msg=l_('Only for managers')))
    def manage_permission_only(self, **kw):
        """Illustrate how a page for managers only works."""
        return dict(page='managers stuff')

    @expose('ebetl.templates.index')
    @require(predicates.is_user('editor', msg=l_('Only for the editor')))
    def editor_user_only(self, **kw):
        """Illustrate how a page exclusive for the editor works."""
        return dict(page='editor stuff')

    @expose('ebetl.templates.login')
    def login(self, came_from=lurl('/')):
        """Start the user login."""
        login_counter = request.environ.get('repoze.who.logins', 0)
        if login_counter > 0:
            flash(_('Wrong credentials'), 'warning')
        return dict(page='login', login_counter=str(login_counter),
                    came_from=came_from)

    @expose()
    def post_login(self, came_from=lurl('/')):
        """
        Redirect the user to the initially requested page on successful
        authentication or redirect her back to the login page if login failed.

        """
        if not request.identity:
            login_counter = request.environ.get('repoze.who.logins', 0) + 1
            redirect('/login',
                params=dict(came_from=came_from, __logins=login_counter))
        userid = request.identity['repoze.who.userid']
        flash(_('Welcome back, %s!') % userid)
        redirect(came_from)

    @expose()
    def post_logout(self, came_from=lurl('/')):
        """
        Redirect the user to the initially requested page on logout and say
        goodbye as well.

        """
        flash(_('We hope to see you soon!'))
        redirect(came_from)
