
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

class customer_details_setup(osv.Model):
    """ 
    This will contain the details of the customer and the registration of the customer
    """
    _name = 'customer.details.setup'
    _rec_name='mob_no'
    #_rec_name='customer_name'
    _description = 'Customer Details'
	
    def name_get(self, cr, uid, ids, context=None):
        logging.info("****************")
        name_val = super(customer_details_setup, self).name_get(cr, uid, ids, context=context)
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
                       FROM customer_details_setup p
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
        return super(customer_details_setup, self).name_search(cr, uid, name, args=args, operator=operator, context=context, limit=limit)

   

	
    _columns = {
	    'customer_name':fields.char('Customer Name',required=True,size=50),
		'mob_no':fields.char('Mobile Number',size=10,required=True),
		'customer_entry_date':fields.date('Customer Details Entry Date',required=True,readonly=True),
		'status':fields.selection(STATUS,'Current Status',select=True),
        'address':fields.many2one('customer.place','Place',size=50,required=True),
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
	
class customer_place(osv.Model):
    """ 
    This will contain the details of the customer and the registration of the customer
    """
    _name = 'customer.place'
    _rec_name='name'
    _description = 'City / Town'
	
    _columns = {
	    'name':fields.char('Place',required=True,size=20),
		'description':fields.text('Description',size=50),
		'status':fields.selection(STATUS,'Current Status',select=True),
    }
	
    _defaults = { 
                    #'status': 'active',
                }
	
    _sql_constraints = [
        ('unique_name', 
         'unique(name)',
        'This Place is already registered.. !')
    ]	


class range_of_discount_setup(osv.Model):
    """ 
    This will contain from range and to range details for discount
    """
    _name = 'range.of.discount.setup'
    _rec_name='status'
    _description = 'Discount Details'
    
    _columns = {
	    'from_range':fields.char('From Range',required=True,size=5),
		'to_range':fields.char('To Range',size=5,required=True),
		'discount_in_per':fields.integer('Discount(in %age)',required=True),
		'status':fields.selection(STATUS,'Current Status',select=True),
    }
	
class customer_bill(osv.Model):
    """ 
    This will contain the details of the customer bill
    """
    _name = 'customer.bill'
    _rec_name='bill_no'
    _description = 'Customer Details'
	
    def generate_bill(self,cr,uid,customer_bill_id,context=None):
        vals={}
        bill_object=self.search(cr,uid,[('id','=',customer_bill_id)],context=context)
        bill_obj=self.pool.get('customer.bill.details').search(cr,uid,[('customer_bill_id','in',customer_bill_id)],context=context)
        customer_bill_object = self.browse(cr,uid,int(customer_bill_id[0]),context=context)
        logging.info("***************************7777")
        # for history
        old_bill = customer_bill_object.bill_amount
        old_pay_final_bill = customer_bill_object.pay_final_bill
        logging.info("*********#########################")
       # for history
		
        x=0
        for i in bill_obj:
            in_obj=self.pool.get('customer.bill.details').browse(cr,uid,i,context=context)
            tot=in_obj.product_wise_tot_bill
            x=x+tot
            #logging.info(x);
            #logging.info("cash bill with out discount *******************")
        context['generate']=True
        fin_bill_obj= self.search(cr,uid,[('id','in',customer_bill_id)],context=context)
        for k in fin_bill_obj:
            for_update_bill=self.browse(cr,uid,k,context=context)
            fin_bill_amount=for_update_bill.amount_in_wallet
            new_value_bill=x - fin_bill_amount
            mob_id = for_update_bill.mob_no.id    # this is for on_chnage of customer number
            #mob_id = for_update_bill.customer_name.id     # this is for on_chnage of customer name
			
        if not new_value_bill:
            raise osv.except_osv(_('You have not purchased anything'), _('But bill is generated.. Edit the bill and add the items purchased'))

        if (new_value_bill>0):
            cr.execute('''  select id,from_range,to_range,discount_in_per from range_of_discount_setup where status='active' order by from_range ''')
            dis_obj = cr.fetchall()
            logging.info(dis_obj)
            logging.info("kkkkkkkkkkkkkkkkkkkkkkkk")
            logging.info(x)
            if dis_obj:
                for ind_dis_obj in dis_obj:
                    #logging.info(ind_dis_obj[1])
                    #logging.info(ind_dis_obj[2])
                    #logging.info("new value bill, *****************")
                    if ( (new_value_bill >= float(ind_dis_obj[1])) and (new_value_bill <= float(ind_dis_obj[2]))):
                        next_cash_back = (new_value_bill * ind_dis_obj[3])/100	
                        self.pool.get('customer.details.setup').write(cr,uid,mob_id,{'amount_in_wallet':next_cash_back},context=context)
                        self.write(cr,uid,customer_bill_id,{'bill_amount':x,'pay_final_bill':new_value_bill,'discount_for_next_purchase':next_cash_back,'state':'billed'},context=context) 										
        
                new_bill = x
                new_pay_final_bill = new_value_bill
        
                if(float(old_bill) != float(new_bill)):
                    remarks_parameter = 'Bill Amount'
                    self.create_history(cr, uid,old_bill,new_bill,remarks_parameter,customer_bill_id[0])
							
                if(float(old_pay_final_bill) != float(new_pay_final_bill)):
                    remarks_parameter = 'Final Bill Amount'
                    self.create_history(cr, uid,old_pay_final_bill,new_pay_final_bill,remarks_parameter,customer_bill_id[0])
            #else:
            #    raise osv.except_osv(_('Warning'),_('Out of discount range..Contact OWNER..!'))
        else:
            next_cash_back = fin_bill_amount;
            self.write(cr,uid,customer_bill_id,{'bill_amount':x,'pay_final_bill':x,'discount_for_next_purchase':next_cash_back,'state':'billed'},context=context)        
            if(float(old_bill) != float(x)):
                remarks_parameter = 'Bill Amount'
                self.create_history(cr, uid,old_bill,x,remarks_parameter,customer_bill_id[0])			
            if(float(old_pay_final_bill) != float(x)):
                remarks_parameter = 'Final Bill Amount'
                self.create_history(cr, uid,old_pay_final_bill,x,remarks_parameter,customer_bill_id[0])			
 	
    def on_changenumber(self, cr, uid ,ids, mob_no=False, context=None):
        val={}
        if mob_no:
            customer = self.pool.get('customer.details.setup').browse(cr,uid,mob_no,context=context)
            val['customer_name'] = customer.customer_name or False
            val['amount_in_wallet'] = customer.amount_in_wallet or False
            return {'value':val}
        return False	
		
    def create_history(self,cr, uid,old_parameter,new_parameter,remarks_parameter,bill_id):
        current_date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        history_vals={'value_from' : old_parameter,
                      'value_to' : new_parameter,
                      'remarks' : remarks_parameter,
                      'modified_by' : uid,
                      'date' : current_date_time,
                      'customer_history_id' : bill_id
                    }
        return self.pool.get('customer.bill.history').create(cr,uid,history_vals)
        	
    
    def create(self, cr, uid, vals, context=None):
        vals['bill_no']= self.pool.get('ir.sequence').get(cr,uid,'customer.bill.sequence')
        return super(customer_bill,self).create(cr,uid,vals,context=context)
		
    def copy(self,cr,uid,id,default=None,context=None):
        raise osv.except_osv(_('Forbidden to duplicate'),_('Not possible to duplicate the bill'))
		
    def revokeBill(self,cr,uid,customer_bill_id,context=None):
	    return self.pool.get('customer.bill').write(cr,uid,customer_bill_id,{'state':'edit'},context=context) 

    def print_bill(self,cr,uid,ids,vals,context=None):
        datas = {'ids':ids}
        return {'type': 'ir.actions.report.xml','report_name': 'bill_report','datas': datas,}	
		
    def cancel(self,cr,uid,customer_bill_id,context=None):
        search_id = self.search(cr,uid,[('id','=',customer_bill_id[0])],context=context)
        bill_obj = self.browse(cr,uid,search_id[0],context=context)
        logging.info(bill_obj)
        before_wallet_amount = bill_obj.amount_in_wallet
        mob_no = bill_obj.mob_no
        self.pool.get('customer.details.setup').write(cr,uid,int(mob_no),{'amount_in_wallet':before_wallet_amount},context=context)
        return self.write(cr,uid,customer_bill_id,{'state':'cancelled'},context=context) 

    def send_sms(self,cr,uid,vals,context=None):
        logging.info(cr)
        logging.info(vals)
        logging.info("check for the data")
        
        cr.execute(''' select 	bill_no,pay_final_bill,discount_for_next_purchase,cds.mob_no,cds.customer_name				
                       from 
                                customer_bill cb, customer_details_setup cds where cb.id= %s and cb.mob_no = cds.id''',(vals[0],))
        result = cr.fetchall()
        logging.info(result)
        logging.info(result[0][3])
        logging.info("******************************>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        
        cr.execute(''' select 
								authkey,sender,route 				
						from 
								sms_details_setup where status='active' ''')
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
		
    _columns = {
	    'bill_no':fields.char('Bill No',size=20,readonly=True),
	    #'mob_no':fields.char('Mobile Number',size=50),
		#'customer_name':fields.many2one('customer.details.setup','Customer Name',size=10,required=True),
        'customer_name':fields.char('Mobile Name',size=50),
		'mob_no':fields.many2one('customer.details.setup','Customer Number',size=10,required=True),
		'bill_amount':fields.float('Bill Amount'),
        #'bill_amount':fields.function(amount_line,store=True, type='float', string='Bill Amount'),
		'amount_in_wallet':fields.float('Amount in Wallet',required=True),
		'bill_date': fields.date('Bill Date',size=10,required=True,readonly=True),
		'customer_bill_details_line':fields.one2many('customer.bill.details','customer_bill_id'),
        'history_line': fields.one2many('customer.bill.history','customer_history_id'),
		'discount_for_next_purchase':fields.float('Cash backfor next purchase',size=10),
        'pay_final_bill':fields.float('Final Bill'),
        'state': fields.selection([('new', 'New'), \
									('edit','Edit'), \
                                    ('billed', 'Billed'), \
                                    ('cancelled', 'Cancelled')], \
                                'Status', readonly=True, select=True),
    }
    _defaults = { 
                    'bill_date': fields.date.context_today, 
                    'state':'new'
                }	

class customer_bill_history(osv.Model):
    _name='customer.bill.history'
    _rec_name = 'modified_by'
    _description = 'customer history details'
   #_order = 'customer_history_id desc'

    _columns = {
        'customer_history_id':fields.many2one('customer.bill','Customer Bill',ondelete="cascade"),
        'modified_by'       : fields.many2one('res.users','Modified by',required=True),
        'date'              : fields.datetime('Date',required=True),
        'value_from'         : fields.char('From Value'),
        'value_to'           : fields.char('To Value'),
        'remarks'           : fields.text('Remarks',size=4000)
    }

				
				
class customer_bill_details(osv.Model):
    """ 
    This will contain the individual details of the customer's bill
    """
    _name = 'customer.bill.details'
    _rec_name='bill_no'
    _description = 'Customer Bill Details'
	
    def on_change_price(self,cr,uid,ids,price,quantity,context=None):
        vals={}
        item_total=price*quantity
        logging.info(item_total)
        vals['product_wise_tot_bill']=item_total
        return {'value':vals}		
	
    _columns = {
	    'customer_bill_id':fields.many2one('customer.bill'),
	    'bill_no':fields.char('Bill No',size=10),
		'product_name':fields.char('Product Name',size=30,required=True),
		'quantity':fields.float('Quantity',size=10,required=True),
		'description':fields.char('Description',size=100),
		'price':fields.float('Price(per piece)',size=7,required=True),
		'product_wise_tot_bill':fields.float('Sub Total',required=True,size=10),
		
		
    } 
	
class sms_details_setup(osv.Model):
    """ 
    This will contain the individual details of the customer's bill
    """
    _name = 'sms.details.setup'
    _rec_name='sender'
    _description = 'SMS Details Setup'
	
    _columns = {
	    'authkey':fields.char('Auth Key',size=40,required=True),
		'sender':fields.char('Sender',size=30,required=True),
        'route':fields.char('Route',size=30,required=True),
        'status':fields.selection(STATUS,'Current Status',select=True),
	}	
	
class cb_setup_configuration(osv.Model):
    """
    This config is for product owner and product user
    """
    _name = 'cb.setup.configuration'
    _rec_name = 'application_last_date'
    _description = 'Product owner and Product user'
    _columns = {
        'sms_consumed' : fields.integer('SMS Consumed'),
        'sms_fixed_balance' : fields.integer('SMS Fixed Balance'),
        'application_last_date' : fields.date('Application Last Date'),
	
    }