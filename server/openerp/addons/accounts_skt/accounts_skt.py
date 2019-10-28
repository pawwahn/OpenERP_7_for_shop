from xml.sax.saxutils import escape
import time
from openerp.osv import fields, osv
from datetime import datetime
from lxml import etree
from openerp import tools
from openerp.tools.translate import _
import logging

STATUS=[('active','Active'),
         ('inactive','Inactive')
	   ]

class account_spending_types_setup(osv.Model):
    """ 
    This is to capture the 'N' number of spending types
    """
    _name = 'account.spending.types.setup'
    _rec_name='name'
    _description = 'Account Spending Types'
   
    _columns = {
        'date':fields.date('Date',size=10,required=True,readonly=True),
	    'name':fields.char('Spending Type Name',required=True,size=50),
        'status':fields.selection(STATUS,'Current Status',select=True),
        'description':fields.text('Description',size=2000),
		
    }
	
    _defaults = { 
                    'date': fields.date.context_today, 
                    'status': 'Active',
                }
	
    _sql_constraints = [
        ('unique_name', 
         'unique(name)',
        'This spending type is already captured.. Alert..!!!!')
    ]	
    
	
class account_spendings(osv.Model):
    """ 
    This will capture the spendings 
    """
    _name = 'account.spendings'
    _rec_name='acc_spending_type_id'
    _description = 'Account Spendings'
			
	
    def create(self, cr, uid, vals, context=None):
        vals['acc_spend_sequence']= self.pool.get('ir.sequence').get(cr,uid,'account.spending.sequence')
        return super(account_spendings,self).create(cr,uid,vals,context=context)
	
    def copy(self,cr,uid,id,default=None,context=None):
        raise osv.except_osv(_('Forbidden to duplicate'),_('Not possible to duplicate'))
		
    def update(self,cr,uid,account_spendings_id,context=None):
        vals={}
        acc_spending_header_obj=self.pool.get('account.spendings').search(cr,uid,[('id','=',account_spendings_id)],context=context)
        acc_spending_details_obj=self.pool.get('account.spendings.details').search(cr,uid,[('account_spendings_id','in',account_spendings_id)],context=context)
        details_sum=0
        for i in acc_spending_details_obj:
            in_details_obj=self.pool.get('account.spendings.details').browse(cr,uid,i,context=context)
            tot=in_details_obj.amount
            details_sum=details_sum+tot
            logging.info(details_sum);
            logging.info("spending check  *******************")
        return self.pool.get('account.spendings').write(cr,uid,account_spendings_id,{'final_amount':details_sum,'state':'in progress'},context=context) 
	
    _columns = {
        'name': fields.char('Name',size=35,required=True),
        'acc_spending_type_id':fields.many2one('account.spending.types.setup','Spending Type',required=True),
        'final_amount':fields.float('Final Amount'),
        'acc_spend_sequence': fields.char('Spending Sequence',size=20,readonly=True),		
        'created_date': fields.date('Bill Date',size=10,required=True,readonly=True),
        'acc_spending_details_line':fields.one2many('account.spendings.details','account_spendings_id'),
        'state': fields.selection([('new', 'New'), \
                                    ('in progress', 'In Progress'), \
                                    ('financial year close', 'Financial Year Close'), \
                                    ('cancelled', 'Cancelled')] , \
                                'Status', readonly=True, select=True),
		
    }
    _defaults = { 
                    'created_date': fields.date.context_today, 
                    'state':'new'
                }

    				
				
class account_spendings_details(osv.Model):
    """ 
    This will capture the spending details
    """
    _name = 'account.spendings.details'
    _rec_name='account_spendings_id'
    _description = 'Account Spending Details'		
	
    _columns = {
	    'account_spendings_id':fields.many2one('account.spendings'),
        'date': fields.date('Date',size=10,required=True),
        'notes':fields.char('Notes',size=50,required=True),
        'amount':fields.float('Amount',size=7,required=True),
    } 