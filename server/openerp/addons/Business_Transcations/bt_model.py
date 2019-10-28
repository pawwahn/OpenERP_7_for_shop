from ast import literal_eval
from xml.sax.saxutils import escape
import time
from openerp.osv import fields, osv
from datetime import datetime
from lxml import etree
from openerp import tools
from openerp.tools.translate import _
import logging
import urllib # Python URL functions
import urllib2 # Python URL functions

STATUS=[('active','Active'),
         ('inactive','Inactive')
	   ]
	   
UNIT =[('kg','KG'),
         ('dozen','Dozen'),('liter','Liter'),('piece','Piece'),('packet','Packet'),
	   ]
	   
PAYMENT_METHOD = [('cash','Cash'),('card','Card'),('paytm','Paytm'),('tez','Tez'),('cheque','Cheque')]

class bt_customer_details_setup(osv.Model):
    """ 
    This will contain the details of the customer and the registration of the customer
    """
    _name = 'bt.customer.details.setup'
    _rec_name='mob_no'
    #_rec_name='customer_name'
    _description = 'Customer Details'
	
    def name_get(self, cr, uid, ids, context=None):
        logging.info("****************")
        name_val = super(bt_customer_details_setup, self).name_get(cr, uid, ids, context=context)
#         if context and 'screen_context' in context:
#             context_value=context.get('screen_context',False)
#             if not context_value :
#                 return name_val 
        res = []
        for rec in self.browse(cr, uid, ids, context):
            #name = (rec.name )+ ' (' + (rec.employee_id or '')+')'
            mob_no = (rec.mob_no )+ ' (' + (rec.customer_name or '')+')' 
            res.append((rec.id, mob_no))
        if len(res) > 0 :
            return res
       
        return name_val  
    
    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        print "*/////////// called funct"
        if args is None:
            args = []
        if context is None:
            context={}
        if name and operator == 'ilike':
            # search on the name of the pricelist and its currency, opposite of name_get(),
            # Used by the magic context filter in the product search view.
            query_args = {'customer_name': '%'+name+'%' ,'limit': limit}
            logging.info(query_args)
            query = """SELECT p.id
                       FROM bt_customer_details_setup p
                       WHERE p.customer_name ilike %(customer_name)s
                       ORDER BY p.mob_no"""
            logging.info("***********************>>>>>>>>>>")
            if limit:
                query += " LIMIT %(limit)s"
            cr.execute(query, query_args)
            ids = [r[0] for r in cr.fetchall()]
            # regular search() to apply ACLs - may limit results below limit in some cases
            ids = self.search(cr, uid, [('id', 'in', ids)], limit=limit, context=context)
            if ids :
                 
                return self.name_get(cr, uid, ids, context)
        return super(bt_customer_details_setup, self).name_search(cr, uid, name, args=args, operator=operator, context=context, limit=limit)

   

	
    _columns = {
	    'customer_name':fields.char('Customer Name',required=True,size=50),
		'mob_no':fields.char('Mobile Number',size=10,required=True),
		'customer_entry_date':fields.date('Customer Details Entry Date',required=True,readonly=True),
		'status':fields.selection(STATUS,'Current Status',select=True),
        'address':fields.many2one('bt.customer.place','Place',size=50,required=True),
		'full_address':fields.text('Address',size=100,),
		'amount_in_wallet':fields.integer('Amount in Wallet',required=True),
		
    }
	
    _defaults = { 
                    'customer_entry_date': fields.date.context_today, 
                    'status': 'active',
                }
	
    _sql_constraints = [
        ('unique_mob_no', 
         'unique(mob_no)',
        'This Mobile number is already registered.. Hope you have cashback..!!!!')
    ]	
	
class bt_customer_place(osv.Model):
    """ 
    This will contain the details of the customer and the registration of the customer
    """
    _name = 'bt.customer.place'
    _rec_name='name'
    _description = 'City / Town'
	
    _columns = {
	    'name':fields.char('Place',required=True,size=20),
		'description':fields.text('Description',size=50),
		'status':fields.selection(STATUS,'Current Status',select=True),
    }
	
    _defaults = { 
                    'status': 'active',
                }
	
    _sql_constraints = [
        ('unique_name', 
         'unique(name)',
        'This Place is already registered.. !')
    ]	

	
class bt_customer_bill(osv.Model):
    """ 
    This will contain the details of the customer bill
    """
    _name = 'bt.customer.bill'
    _rec_name='bill_no'
    _description = 'Customer Details'
	
    
    def on_changenumber(self, cr, uid ,ids, mob_no=False, context=None):
        val={}
        if mob_no:
            customer = self.pool.get('bt.customer.details.setup').browse(cr,uid,mob_no,context=context)
            val['customer_name'] = customer.customer_name or False
            val['amount_in_wallet'] = customer.amount_in_wallet or False
            return {'value':val}
        return False	
			
    _columns = {
	    'bill_no':fields.char('Bill No',size=20,readonly=True),
	    #'mob_no':fields.char('Mobile Number',size=50),
		#'customer_name':fields.many2one('customer.details.setup','Customer Name',size=10,required=True),
        'customer_name':fields.char('Mobile Name',size=50),
		'mob_no':fields.many2one('bt.customer.details.setup','Customer Number',size=10,required=True),
		'bill_amount':fields.float('Bill Amount'),
		'bill_date': fields.date('Bill Date',size=10,required=True,readonly=True),
        'discount_amount': fields.float('Discount'),
		'discount_for_next_purchase': fields.float('Credit balance for next purchase'),
        'amount_in_wallet': fields.float('Wallet Amount'),
        'final_amount': fields.float('Final Amount'),
		'cgst_amount':fields.float('CGst'),
		'sgst_amount':fields.float('SGst'),
		'igst_amount':fields.float('IGst'),
		'total_gst':fields.float('Tot GST'),
		'given_amount': fields.float('Given Amount'),
		'change_to_be_tendered' : fields.float('Give Change'),
		'customer_bill_details_line':fields.one2many('bt.customer.bill.details','customer_bill_id'),
        'history_line': fields.one2many('bt.customer.bill.history','customer_history_id'),
		'payment_method':fields.selection(PAYMENT_METHOD,'Payment Mode',required=True,select='cash'),
        'state': fields.selection([('new', 'New'), \
									('edit','Edit'), \
                                    ('billed', 'Billed'), \
                                    ('cancelled', 'Cancelled')], \
                                'Status', readonly=True, select=True),
    }
    _defaults = { 
                    'bill_date': fields.date.context_today, 
                    'state':'new',
					'payment_method':'cash',
                }	
				
    def send_sms(self,cr,uid,vals,context=None):
        logging.info(cr)
        logging.info(vals)
        logging.info("check for the data")
        
        cr.execute(''' select 	bill_no,final_amount,discount_for_next_purchase,cds.mob_no,cds.customer_name				
                       from 
                                bt_customer_bill cb, bt_customer_details_setup cds where cb.id= %s and cb.mob_no = cds.id''',(vals[0],))
        result = cr.fetchall()
        logging.info(result)
        logging.info(result[0][3])
        logging.info("******************************>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        
        cr.execute(''' select 
								authkey,sender,route 				
						from 
								bt_sms_details_setup where status='active' ''')
        sms_data = cr.fetchone()
        logging.info(sms_data)
		
        #authkey = "125423AhKOMIg5Bm57da5ec8" # Your authentication key.
        mobiles = result[0][3] # Multiple mobiles numbers separated by comma.
        message = " Hi %s, your final bill after redeeming wallet amount is Rs.%s /- and your updated wallet amount is Rs.%s/-. Enjoy shopping..!" %(result[0][4],result[0][1],result[0][2])
        logging.info(message)		
        #sender = "PAVANK"               # Sender ID,While using route4 sender id should be 6 characters long.
        #route = "4" # Define route
		
        if sms_data:
			authkey = sms_data[0]
			sender = sms_data[1]
			route = sms_data[2]
			
			
			if not authkey:
				raise osv.except_osv(_('No authkey'),_('Check for SMS balance'))
			if not mobiles:
				raise osv.except_osv(_('Cashback'),_('Enter valid mobile number'))
			if not sender:
				raise osv.except_osv(_('No sender id'),_('Route 4 is not valid'))
			if not route:
				raise osv.except_osv(_('Route Alert'),_('Route is not defined'))
			values = {
			  'authkey' : authkey,
			  'mobiles' : mobiles,
			  'message' : message,
			  'sender' : sender,
			  'route' : route
			}
			logging.info(values)
			url = "https://control.msg91.com/api/sendhttp.php" # API URL
			postdata = urllib.urlencode(values) # URL encoding the data here.
			if not url:
				raise osv.except_osv(_('Alert'),_('URL not defined / No Internet connection'))
			if not postdata:
				raise osv.except_osv(_('Alert'),_('Check for Post Data'))
			req = urllib2.Request(url, postdata)
			if not req:
				raise osv.except_osv(_('Alert'),_('No internet connection'))
			response = urllib2.urlopen(req)
			if not response:
				raise osv.except_osv(_('Alert'),_('No internet connection'))
			output = response.read() # Get Response
			if not output:
				raise osv.except_osv(_('Alert'),_('No internet connection'))
			logging.info(output) # Print Response		
			#return True
			raise osv.except_osv(_('Transaction Successful..!'),_('SMS is sent to the customer'))
        else:
            raise osv.except_osv(_('Error'),_('Parameters missing..'))
				
    def create(self, cr, uid, vals, context=None):
        vals['bill_no']= self.pool.get('ir.sequence').get(cr,uid,'bt.customer.bill.sequence')
        return super(bt_customer_bill,self).create(cr,uid,vals,context=context)
		
    def copy(self,cr,uid,id,default=None,context=None):
        raise osv.except_osv(_('Forbidden to duplicate'),_('Not possible to duplicate the bill'))
		
    def revokeBill(self,cr,uid,customer_bill_id,context=None):
	    return self.pool.get('bt.customer.bill').write(cr,uid,customer_bill_id,{'state':'edit'},context=context) 


class bt_customer_bill_history(osv.Model):
    _name='bt.customer.bill.history'
    _rec_name = 'modified_by'
    _description = 'customer history details'
   #_order = 'customer_history_id desc'

    _columns = {
        'customer_history_id':fields.many2one('bt.customer.bill','Customer Bill',ondelete="cascade"),
        'modified_by'       : fields.many2one('res.users','Modified by',required=True),
        'date'              : fields.datetime('Date',required=True),
        'value_from'         : fields.char('From Value'),
        'value_to'           : fields.char('To Value'),
        'remarks'           : fields.text('Remarks',size=4000)
    }

	
class bt_customer_bill_details(osv.Model):
    """ 
    This will contain the individual details of the customer's bill
    """
    _name = 'bt.customer.bill.details'
    #_rec_name='bill_no'
    _description = 'Customer Bill Details'
	
    def on_change_price(self,cr,uid,ids,price,quantity,context=None):
        vals={}
        item_total=price*quantity
        logging.info(item_total)
        vals['product_wise_tot_bill']=item_total
        return {'value':vals}		
	
    _columns = {
	    'customer_bill_id':fields.many2one('bt.customer.bill'),
	    'product_name':fields.many2one('bt.cb.stock.details',required=True),
		'quantity':fields.float('Qty',required=True),
		#'description':fields.char('Description'),
		'price':fields.float('Price',required=True),
		'product_wise_tot_bill':fields.float('Sub Tot',required=True),
        'total_gst': fields.float('Total GST'),
        'return_qty': fields.float('Return Qty'),
		'cgst':fields.float('CGst Per'),
		'sgst':fields.float('SGst Per'),
		'igst':fields.float('IGst Per'),
		'product_wise_tot_bill_inc_gst':fields.float('Total',required=True),
    }
		 

	
class bt_customer_bill_detail_history(osv.Model):
    _name='bt.customer.bill.detail.history'
    _rec_name = 'modified_by'
    _description = 'customer history details'
   #_order = 'customer_history_id desc'

    _columns = {
        'customer_history_id':fields.many2one('bt.customer.bill','Customer Bill',ondelete="cascade"),
        'modified_by'       : fields.many2one('res.users','Modified by',required=True),
        'date'              : fields.datetime('Date',required=True),
        'value_from'         : fields.char('From Value'),
        'value_to'           : fields.char('To Value'),
        'remarks'           : fields.text('Remarks',size=4000)
    }

				
				
	
class bt_sms_details_setup(osv.Model):
    """ 
    This will contain the individual details of the customer's bill
    """
    _name = 'bt.sms.details.setup'
    _rec_name='sender'
    _description = 'SMS Details Setup'
	
    _columns = {
	    'authkey':fields.char('Auth Key',size=40,required=True),
		'sender':fields.char('Sender',size=30,required=True),
        'route':fields.char('Route',size=30,required=True),
        'status':fields.selection(STATUS,'Current Status',select=True),
	}	
	
class bt_cb_setup_configuration(osv.Model):
    """
    This config is for product owner and product user
    """
    _name = 'bt.cb.setup.configuration'
    _rec_name = 'application_last_date'
    _description = 'Product owner and Product user'
    _columns = {
        'sms_consumed' : fields.integer('SMS Consumed'),
        'sms_fixed_balance' : fields.integer('SMS Fixed Balance'),
        'application_last_date' : fields.date('Application Last Date'),
	}

class bt_cb_stock_details(osv.Model):
    """
    This config is for product stock details
    """
    _name = 'bt.cb.stock.details'
    _rec_name = 'product_name'
    
    _columns = {
        'product_name':fields.char('Product Name',required=True),
        'available_qty':fields.float('Available Quantity',required=True),
        'purchased_price':fields.float('Purchased Price',required=True),
        'cgst_per':fields.float('CGst Per'),
        'sgst_per':fields.float('SGst Per'),
        'igst_per':fields.float('IGst Per'),
        #'units':fields.many2one('bt.cb.units','UNITS',required=True),
        'units':fields.selection(UNIT,'UNITS',required=True),
        'profit':fields.float('Profit',required=True),
        'min_sale_price':fields.float('Min Sale Price',required=True),
        'max_sale_price':fields.float('Max Sale Price',required=True),
        'status':fields.selection(STATUS,'Current Status',select=True),
	}
	
	
class bt_cb_units(osv.Model):
    """
    This config is for product owner and product user
    """
    _name = 'bt.cb.units'
    _rec_name = 'name'
    _description = 'Product owner and Product user'
    _columns = {
        'name' : fields.char('Units',required=True),
        'description' : fields.text('Description'),
        'status':fields.selection(STATUS,'Current Status',select=True),
    }
	
    _defaults = { 
                    'status': 'active',
                }
				
class bt_range_of_discount_setup(osv.Model):
    """ 
    This will contain from range and to range details for discount
    """
    _name = 'bt.range.of.discount.setup'
    _rec_name='status'
    _description = 'Discount Details'
    
    _columns = {
	    'from_range':fields.char('From Range',required=True,size=5),
		'to_range':fields.char('To Range',size=5,required=True),
		'discount_in_per':fields.integer('Discount(in %age)',required=True),
		'status':fields.selection(STATUS,'Current Status',select=True),
    }
	
class bt_send_bulk_sms(osv.Model):
    _name='bt.send.bulk.sms'
    _rec_name = 'name'
    _description = 'Group SMS details'
	
    _columns = {
	    'name':fields.char('Name',required=True,size=50),
		'created_date':fields.date('Created Date',size=5,required=True),
		'description':fields.text('Discount Details',size=150,required=True),
        'status':fields.selection(STATUS,'Current Status',select=True),
    }
	
    _defaults = { 
	                'created_date': fields.date.context_today, 
                    'status': 'active',
                }
				
    def send_bulk_sms(self,cr,uid,vals,context=None):
        contact_details = []
        cr.execute(''' select 	description
                       from 
                                bt_send_bulk_sms cb where cb.id= %s ''',(vals[0],))
        result = cr.fetchall()
        cr.execute(''' select 
								authkey,sender,route 				
						from 
								bt_sms_details_setup where status='active' ''')
        sms_data = cr.fetchone()
        cr.execute(''' select 
								mob_no 				
						from 
								bt_customer_details_setup where status='active' ''')
        contact_details = cr.fetchall()
        mobiles = list(contact_details)
        message = result[0]		
        if sms_data:
			if not sms_data[0]:
				raise osv.except_osv(_('No authkey'),_('Check for SMS balance'))
			if not mobiles:
				raise osv.except_osv(_('Cashback'),_('Enter valid mobile number'))
			if not sms_data[1]:
				raise osv.except_osv(_('No sender id'),_('Route 4 is not valid'))
			if not sms_data[2]:
				raise osv.except_osv(_('Route Alert'),_('Route is not defined'))
        else:
            raise osv.except_osv(_('Error'),_('Parameters missing..'))
        for mob in mobiles:
            values = { 'authkey' :sms_data[0] , #authkey
			  #'mobiles' : mobiles,
			  'mobiles' : mob[0],
			  'message' : message[0],
			  'sender' : sms_data[1],  #sender
			  'route' : sms_data[2]}   #route
            url = "https://control.msg91.com/api/sendhttp.php" # API URL
            postdata = urllib.urlencode(values) # URL encoding the data here.
            if not url or not postdata:
                raise osv.except_osv(_('Alert'),_('URL or Post Data not defined / No Internet connection'))
            req = urllib2.Request(url, postdata)
            if not req:
                raise osv.except_osv(_('Alert'),_('No internet connection'))
            response = urllib2.urlopen(req)
            if not response:
                raise osv.except_osv(_('Alert'),_('No internet connection'))
            output = response.read() # Get Response
            if not output:
                raise osv.except_osv(_('Alert'),_('No internet connection'))		
			#return True
        raise osv.except_osv(_('Transaction Successful..!'),_('SMS is sent to the customer'))
        