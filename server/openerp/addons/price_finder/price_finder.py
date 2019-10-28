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


class ssh_company(osv.Model):
    _name='ssh.company'
    _rec_name = 'company'
    _description = 'company'
    _columns = {
        'company': fields.char('Sizes',required=True),
        'pur_rate' : fields.float('Purchase Price',required=True),
        'gst_per' : fields.float('GST Charged',required=True),
        'price_inc_tax': fields.float('Taxed Price', required=True),
        'sale_rate' : fields.float('Sale Price',required=True),
        'sale_gst_per': fields.float('Sale Price GST', required=True),
        'final_gst_price': fields.float('Final Sale Price', required=True),
        'status' :fields.selection(STATUS, 'Status',required=True),
        
    }

    def on_change_price(self,cr,uid,ids,pur_rate,gst_per,context=None):
        vals={}
        price_added_per_pur_rate = (pur_rate * gst_per) / 100
        taxed_rate = price_added_per_pur_rate + pur_rate
        vals['price_inc_tax']=taxed_rate
        return {'value':vals}

    def on_change_gst(self,cr,uid,ids,sale_rate,sale_gst_per,context=None):
        vals={}
        logging.info("++++++++++++++++++++++++++++###############")
        logging.info(sale_rate)
        logging.info(sale_gst_per)
        our_tax_amount = (sale_rate * sale_gst_per) / 100
        taxed_rate = sale_rate + our_tax_amount
        vals['final_gst_price']=taxed_rate
        return {'value':vals}
    
    _defaults = {
        'status':'active',
        'gst_per' : 5,
        'sale_gst_per' : 5,
    }

    
class ssh_company_rate(osv.Model):
    _name='ssh.company.rate'
    _rec_name = 'company_name_id'
    _description = 'category'
		
    def on_change_company(self, cr, uid, ids, company_name_id=False, context=None):
        val = {}
        if company_name_id:
            logging.info("*********>>>>>>>>>>>>>>")
            logging.info(company_name_id)
            company_obj = self.pool.get('ssh.company').browse(cr, uid, company_name_id, context=context)
            if company_obj:
                val['pur_rate'] = company_obj.pur_rate or False
                val['price_inc_tax'] = company_obj.price_inc_tax or False
                val['sale_price'] = company_obj.sale_rate or False
                val['our_gst_per'] = company_obj.sale_gst_per or False
                val['new_sale_price'] = company_obj.final_gst_price or False

                return {'value': val }
            else:
                raise osv.except_osv (_('Unsuccessful Attempt..!'),_('No Product found'))
        return True

    def create(self, cr, uid, vals, context):
        cr.execute('''delete from ssh_company_rate''')
        return False
    
    _columns = {
        'company_name_id' : fields.many2one('ssh.company',required=True),
        'pur_rate' : fields.float('Purchase Price',required=True),
        'price_inc_tax': fields.float('Final Purchase Price', required=True),
        'sale_price' : fields.float('Sale Price',required=True),
        'our_gst_per': fields.float('GST Per', required=True),
        'new_sale_price' : fields.float('New Sale Price'),
        
    }
    
        
