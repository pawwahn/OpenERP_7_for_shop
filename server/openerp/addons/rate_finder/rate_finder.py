from openerp.osv import fields, osv
import logging
from openerp.tools.translate import _
import time
import datetime
from openerp.osv import osv


STATUS=[
          ('active','Active'),
          ('inactive','Inactive'),
       ]

'''
author: kota
'''
class company_setup(osv.Model):
    _name='company.setup'
    _rec_name = 'company_name'
    _description = 'company Details'
    _columns = {
        'company_name': fields.char('Company Name',required=True,size=60),
        'company_description':fields.text('Description',size=100),
        'status' :fields.selection(STATUS, 'Status',required=True),
    }

    _defaults = {
        'status':'active',
    }

    _sql_constraints = [
                     ('unique_company_name',
                      'unique(company_name)',
                      ' It is already registered..!')
    ]

class company_category(osv.Model):
    _name='company.category'
    _rec_name = 'category_name'
    _description = 'category'
    _columns = {
        'company_name_id' : fields.many2one('company.setup',required=True),
        'category_name' : fields.char('Category',required=True),
        'status' :fields.selection(STATUS, 'Status',required=True),

    }

    _defaults = {
        'status':'active',
    }

    _sql_constraints = [
                     ('unique_category_name',
                      'unique(category_name)',
                      ' Category is already registered..!'),

]

class company_category_size(osv.Model):
    _name='company.category.size'
    _rec_name = 'category_size'
    _description = 'category size'
    _columns = {
        'company_name_id' : fields.many2one('company.setup',required=True),
        'category_name' : fields.many2one('company.category',required=True),
        'category_size': fields.char('Sizes',required=True),
        'pur_rate' : fields.float('Purchase Price',required=True),
        'gst_per' : fields.float('GST Charged',required=True),
        'price_inc_tax': fields.float('Taxed Price', required=True),
        'sale_rate' : fields.float('Sale Price',required=True),
        'status' :fields.selection(STATUS, 'Status',required=True),
        
    }

    def on_change_price(self,cr,uid,ids,pur_rate,gst_per,context=None):
        vals={}
        price_added_per_pur_rate = (pur_rate * gst_per) / 100
        taxed_rate = price_added_per_pur_rate + pur_rate
        vals['price_inc_tax']=taxed_rate
        return {'value':vals}
    
    _defaults = {
        'status':'active',
    }

    _sql_constraints = [
                     ('unique_category_size',
                      'unique(category_size),',
                      ' size is already registered..!'),

]
    
    
class company_category_rate(osv.Model):
    _name='company.category.rate'
    _rec_name = 'company_name_id'
    _description = 'category'


    def on_change_size(self, cr, uid, ids, category_size_id=False, context=None):
        val = {}
        global cust_num
        if category_size_id:
            customer = self.pool.get('company.category.size').browse(cr, uid,  category_size_id , context=context)
            if customer:
                val['pur_rate'] =  customer.pur_rate or False
                val['sale_price'] = customer.sale_rate or False
                return {'value' :val }
            else:
                raise osv.except_osv(('Warning'),('No product..'))
        return True
		
    def on_change_company(self, cr, uid, ids, company_name_id=False, context=None):
        val = {}
        if company_name_id:
            company_obj = self.pool.get('company.category.size').browse(cr, uid, company_name_id, context=context)
            if company_obj:
                return {'value':{'category_name_id':False, 'category_size': False,'pur_rate':False,'sale_price':False} }
            else:
                raise osv.except_osv (_('Unsuccessful Attempt..!'),_('No Product found'))
        return True

    def on_change_category(self, cr, uid, ids, category_name_id=False, context=None):
        val = {}
        if category_name_id:
            company_obj = self.pool.get('company.category.size').browse(cr, uid, category_name_id, context=context)
            if company_obj:
                return {'value':{'category_size': False,'pur_rate':False,'sale_price':False}}
            else:
                raise osv.except_osv (_('Unsuccessful Attempt..!'),_('No Product found'))
        return True
		
    def create(self, cr, uid, vals, context):
        cr.execute('''delete from company_category_rate''')
        return False


    #def on_change_size(self, cr, uid, ids, category_size=False, context=None):
    #    val = {}
    #    if category_size:
    #        company_obj = self.pool.get('company.category.size').browse(cr, uid, category_size, context=context)
    #        if company_obj:
    #            return {'value':{'pur_rate': False,'sale_price':False}}
    #        else:
    #            raise osv.except_osv (_('Unsuccessful Attempt..!'),_('No Product found'))

    
    _columns = {
        'company_name_id' : fields.many2one('company.setup',required=True),
        'category_name_id' : fields.many2one('company.category',required=True),
        'category_size' : fields.many2one('company.category.size',required=True),
        'pur_rate' : fields.float('Purchase Price',required=True),
        'sale_price' : fields.float('Sale Price',required=True),
        
    }
    
        
