
from xml.sax.saxutils import escape
import time
from openerp.osv import fields, osv
from datetime import datetime
import datetime
from datetime import timedelta
from lxml import etree
from openerp import tools
from openerp.tools.translate import _
import logging
import re

def json_serial(obj):
    if isinstance(obj, datetime):
        serial = obj.isoformat()
        return serial
    raise TypeError ("Type not serializable")

STATUS=[('active','Active'),
         ('inactive','Inactive')
	   ]
	   
C_OR_D_STATUS = [('credit','Credit'),
				  ('debit','Debit')
	]
	   
VAT=[('1',1),
     ('2',2),('3',3)
	   ]
	   
from xml.sax.saxutils import escape
import time
from openerp.osv import fields, osv
from datetime import datetime
from lxml import etree
from openerp import tools
from openerp.tools.translate import _
import logging
	
class credit_customer_bill(osv.Model):
    """ 
    This will contain the details of the customer bill
    """
    _name = 'credit.customer.bill'
    _rec_name='bill_no'
    _description = 'Customer Details'
	
    def generateBill(self,cr,uid,credit_customer_bill_id,context=None):
        vals={}
        logging.info(credit_customer_bill_id)
        logging.info("**************************************")
        final_bill_after_discount = 0
        bill_object=self.pool.get('credit.customer.bill').search(cr,uid,[('id','=',credit_customer_bill_id)],context=context)
        for i in bill_object:
            for_dic_val=self.pool.get('credit.customer.bill').browse(cr,uid,i,context=context)
            discount_value = for_dic_val.discount_amount
        bill_obj=self.pool.get('credit.customer.bill.details').search(cr,uid,[('credit_customer_bill_id','in',credit_customer_bill_id)],context=context)
        total_bill_amount=0
        for i in bill_obj:
            in_obj=self.pool.get('credit.customer.bill.details').browse(cr,uid,i,context=context)
            tot=in_obj.product_wise_tot_bill
            total_bill_amount=total_bill_amount+tot
        final_bill_after_discount = total_bill_amount - discount_value
        self.pool.get('credit.customer.bill').write(cr,uid,credit_customer_bill_id,{'bill_amount':total_bill_amount,'final_bill_amount':final_bill_after_discount,'state':'billed'},context=context)
        #self.pool.get('customer.credit.debit.details').write(cr,uid,credit_customer_bill_id,{'credit_amount':final_bill_after_discount},context=context)

		
        payment_bill_object=self.pool.get('credit.customer.bill').search(cr,uid,[('id','=',credit_customer_bill_id)],context=context)
        payment_bill_obj=self.pool.get('credit.customer.payment.details').search(cr,uid,[('credit_customer_bill_id','in',credit_customer_bill_id)],context=context)
        paid_amount=0
        for j in payment_bill_obj:
            payment_in_obj=self.pool.get('credit.customer.payment.details').browse(cr,uid,j,context=context)
            tot=payment_in_obj.amount
            paid_amount=paid_amount+tot
        self.pool.get('credit.customer.bill').write(cr,uid,credit_customer_bill_id,{'balance_to_pay':paid_amount,'state':'payment cleared'},context=context)
        #to_pay = total_bill_amount - paid_amount
        to_pay = final_bill_after_discount - paid_amount
        if (paid_amount > 0):
            self.pool.get('credit.customer.bill').write(cr,uid,credit_customer_bill_id,{'balance_to_pay':to_pay,'state':'payment in progress'},context=context)
        if (paid_amount == 0):
            self.pool.get('credit.customer.bill').write(cr,uid,credit_customer_bill_id,{'balance_to_pay':to_pay,'state':'billed'},context=context)
        if (to_pay == 0 ):
            self.pool.get('credit.customer.bill').write(cr,uid,credit_customer_bill_id,{'balance_to_pay':to_pay,'state':'payment cleared'},context=context)
        logging.info("*******************************=====================")
        #logging.info(vals)
        #logging.info(vals['final_bill_after_discount'])
        bill_payments_id = self.pool.get('customer.bills.payments').search(cr,uid,[('bill_id','=',credit_customer_bill_id),('credit_debit_type','=','debit')],context=context)
        logging.info("5555555555555555555555555")
        logging.info(bill_payments_id)
        logging.info(bill_payments_id[0])
        #new_values_dict = {'debit_amount':final_bill_after_discount}
        #print '$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$',new_values_dict
        
		
        return self.pool.get('customer.bills.payments').write(cr, uid,bill_payments_id[0], {'debit_amount':final_bill_after_discount,'credit_amount':0},context=context)
        #new_id = super(credit_customer_payment_details,self).write(cr,uid,ids,vals,context=context)
        #return new_id		
			
    def revokeBill(self,cr,uid,credit_customer_bill_id,context=None):
	    return self.pool.get('credit.customer.bill').write(cr,uid,credit_customer_bill_id,{'state':'new'},context=context)	
	
    def get_data(self,cr,uid,from_date,to_date,context=None):
        logging.info("=============== dates")
        logging.info(from_date)
        logging.info(to_date)
        month_year = []
        sales = []
        if from_date:
            from_date = datetime.strptime(from_date , '%d/%m/%Y').strftime('%Y-%m-%d')
        else:
            raise osv.except_osv(_('From date is mandatory'),_('Alert'))
        if to_date:
            to_date = datetime.strptime(to_date , '%d/%m/%Y').strftime('%Y-%m-%d')
        else:
            raise osv.except_osv(_('To date is mandatory'),_('Alert'))
        cr.execute('''select to_char(bill_date,'Mon-YYYY') as year_month,to_char(bill_date,'YYYY') as year,to_char(bill_date,'Mon') as month,
                           sum("bill_amount") as "Sales"
			   
                      from 
                              credit_customer_bill
                      where 
                              bill_date>=%s and bill_date<=%s group by 1,2,3 order by year desc;''',(from_date,to_date))
        graph_data = cr.fetchall()
        for month in graph_data:
            month_year.append(month[0]) 
            sales.append(month[3])
        #return graph_data
        return month_year,sales
		
    def get_state_wise_data(self,cr,uid,from_date,to_date,context=None):
        logging.info("state wise function called =================================")
        state_wise = []
        sale_amount = []
        if from_date:
            from_date = datetime.strptime(from_date , '%d/%m/%Y').strftime('%Y-%m-%d')
        if to_date:
            to_date = datetime.strptime(to_date , '%d/%m/%Y').strftime('%Y-%m-%d')
        cr.execute('''SELECT state, SUM(bill_amount) FROM credit_customer_bill 
                      where 
                              bill_date>=%s and bill_date<=%s GROUP BY state order by state;''',(from_date,to_date))
        state_graph_data = cr.fetchall()
        #for record in state_graph_data:
        #    state_wise.append(record[0]) 
        #   sale_amount.append(record[1])
        return state_graph_data
        #return state_wise,sale_amount

			
    # def on_changename(self, cr, uid ,ids, customer_name=False, context=None):
        # val={}
        # if customer_name:
            # customer = self.pool.get('customer.details.setup').browse(cr,uid,customer_name,context=context)
            # logging.info("########################## onchange name")
            # logging.info(customer)
            # #val['customer_name'] = customer.customer_name or False
            # val['customer_address'] = customer.address.id or False
            # val['mob_no'] = customer.mob_no or False
            # logging.info(val);
            # return {'value':val}
        # return False
  
    def on_changenumber(self, cr, uid ,ids, mob_no=False, context=None):
        val={}
        if mob_no:
            customer = self.pool.get('customer.details.setup').browse(cr,uid,mob_no,context=context)
            logging.info("########################## onchange mobile")
            logging.info(customer)
            val['customer_name'] = customer.customer_name or False
            val['customer_address'] = customer.address.id or False
            #val['mob_no'] = customer.mob_no or False
            logging.info(val);
            return {'value':val}
        return False

    def on_changeplace(self, cr, uid ,ids, customer_address=False, context=None):
        val={}
        if customer_address:
            customer_address_obj = self.pool.get('credit.customer.bill').browse(cr,uid,customer_address,context=context)
            address_id = customer_address_obj.id
            all_mob_obj=self.pool.get('customer.details.setup').search(cr,uid,[('address','=',address_id)],context=context)
            logging.info(all_mob_obj);
            mob_numbers_list = [];
            val['mob_no'] = all_mob_obj or False
            logging.info(val);
            return {'value':val}
        return False		
    
    def print_bill(self,cr,uid,vals,context=None):
        datas = {'ids':ids}
        return {'type':'ir.actions.report.xml','report_name':'bill_report','datas': datas,}
	
    def create(self, cr, uid, vals, context=None):
        if vals['bill_type'] == 1: 
            vals['bill_no']= self.pool.get('ir.sequence').get(cr,uid,'cb.seq.acc')
        elif vals['bill_type'] == 2: 
            vals['bill_no']= self.pool.get('ir.sequence').get(cr,uid,'cb.seq.num')
        else:
            vals['bill_no']= self.pool.get('ir.sequence').get(cr,uid,'cr.seq.cre')
        logging.info("check for vals *************");
        logging.info(vals);
        #return super(credit_customer_bill,self).create(cr,uid,vals,context=context)
        new_id = super(credit_customer_bill,self).create(cr,uid,vals,context=context)
        bill_id = self.pool.get('credit.customer.bill').search(cr,uid,[('bill_no','=',vals['bill_no'])],context=context)
		
        values = {
					#'customer_id':vals['customer_name'],
					#'customer_name':vals['mob_no'],
					'customer_id':vals['mob_no'],
					'customer_name':vals['customer_name'],
					'bill_num':vals['bill_no'],
					'bill_id':bill_id[0],
					'credit_debit_type':'debit',
					'cre_deb_date' : vals['bill_date'],
					'credit_amount':0,
				}		
        self.pool.get('customer.bills.payments').create(cr,uid,values,context=context)
        return new_id 		
		
    def copy(self,cr,uid,id,default=None,context=None):
        raise osv.except_osv(_('Forbidden to duplicate'),_('Not possible to duplicate the bill'))
		
		
    _columns = {
	    'bill_no':fields.char('Bill No',size=20,readonly=True),
		'customer_name':fields.char('Customer Name'),
        #'customer_name':fields.many2one('customer.details.setup','Customer Name',required=True),
		'customer_address':fields.many2one('customer.place','Place'),
        #'mob_no':fields.char('Mobile Number',size=10),
		'mob_no' : fields.many2one('customer.details.setup','Customer Mobile',required=True),
        'bill_amount':fields.float('Bill Amount'),
        'balance_to_pay':fields.float('Balance Amount'),
        'bill_date': fields.date('Bill Date',size=10,required=True,readonly=True),
        'credit_customer_bill_details_line':fields.one2many('credit.customer.bill.details','credit_customer_bill_id'),
        'credit_customer_bill_payment_line':fields.one2many('credit.customer.payment.details','credit_customer_bill_id'),
        'bill_notes':fields.text('Bill Note',size=200),
        'payment_notes':fields.text('Payment Note',size=200),
        'bill_type': fields.many2one('bill.type.setup','Bill Type',required=True),
        'discount_amount': fields.float('Discount Amount'),
        'final_bill_amount': fields.float('Final Bill Amount',size=10),
        'state': fields.selection([('new', 'New'), \
                                    ('billed', 'Billed'), \
                                    ('payment in progress', 'Payment In Progress'), \
                                    ('payment cleared', 'Payment Cleared'), \
                                    ('cancelled', 'Cancelled')], \
                                'Status', readonly=True, select=True),
		
    }
    _defaults = { 
                    'bill_date': fields.date.context_today, 
                    'state':'new',
                    'bill_type' : 2,
                }		
				
class credit_customer_bill_details(osv.Model):
    """ 
    This will contain the individual details of the customer's bill
    """
    _name = 'credit.customer.bill.details'
    _description = 'Credit Customer Bill Details'
	
    def on_change_price(self,cr,uid,ids,quantity,return_qty,price,context=None):
        vals={}
        qty = (quantity - return_qty)
        item_total=price* qty
        vals['product_wise_tot_bill']=item_total
        return {'value':vals}		
	
    _columns = {
	    'credit_customer_bill_id':fields.many2one('credit.customer.bill',ondelete="cascade"),
        'product_name':fields.char('Product Name',size=30,required=True),
        'quantity':fields.float('Quantity',size=10,required=True),
        'return_qty': fields.float('Quantity'),
        'description':fields.char('Description',size=100),
        'price':fields.float('Price(per piece)',size=7,required=True),
        'product_wise_tot_bill':fields.float('Sub Total',required=True,size=10),
        'checked':fields.boolean('Checked'),
        'double_checked':fields.boolean('Doubled Checked'),
		
    } 
	
	
class credit_customer_payment_details(osv.Model):
    """ 
    This will contain the individual details of the customer's bill
    """
    _name = 'credit.customer.payment.details'
    _description = 'Credit Customer Payment Details'	
	
    _columns = {
	    'credit_customer_bill_id':fields.many2one('credit.customer.bill',ondelete="cascade"),
        'bill_date': fields.date('Bill Date',size=10,required=True),
        'description':fields.char('Description',size=100),
        'amount':fields.float('Amount Paid',size=7,required=True),
        'payment_type_id':fields.many2one('payment.type.setup','Payment Type',required=True),
        'checked':fields.boolean('Checked'),
    } 
	
    def create(self,cr,uid,vals,context=None):
        new_id = super(credit_customer_payment_details,self).create(cr,uid,vals,context=context)
        logging.info(new_id)
        paid_amnt_obj = self.pool.get('credit.customer.payment.details').browse(cr,uid,new_id,context=context)
        header_obj = self.pool.get('credit.customer.bill').browse(cr,uid,vals['credit_customer_bill_id'],context=context)
        logging.info("inside create of ccpd +++++++++++++++++++")
        logging.info(header_obj)
        logging.info(header_obj.mob_no)
        new_values_dict = {
							#'customer_id':header_obj.customer_name.id,
							#'customer_name':header_obj.customer_name.mob_no,
							'customer_id':header_obj.mob_no.id,
							'customer_name':header_obj.mob_no.customer_name,
							'credit_debit_type':'credit',
							'bill_num':header_obj.bill_no,
							'bill_id':header_obj.id,
							#'credit_amount':header_obj.final_bill_amount,
							'credit_amount':paid_amnt_obj.amount,
							'debit_amount' :0,
							'place':header_obj.mob_no.address.name,
							'line_id': new_id,
						    'cre_deb_date' : paid_amnt_obj.bill_date
						   #'cre_deb_date' : header_obj.bill_date
						}
        self.pool.get('customer.bills.payments').create(cr,uid,new_values_dict,context=context)		
        return new_id
		
    #def write(self,cr,uid,vals,context=None):
    def write(self,cr,uid,ids,vals,context=None):
        if 'amount' in vals:
            customer_bills_payments_ids = self.pool.get('customer.bills.payments').search(cr,uid,[('line_id','=',ids[0])],context=context)
            if len(customer_bills_payments_ids) >0:
                new_values_dict = {'credit_amount': vals['amount']}
                self.pool.get('customer.bills.payments').write(cr,uid,customer_bills_payments_ids[0],new_values_dict,context=context)
        new_id = super(credit_customer_payment_details,self).write(cr,uid,ids,vals,context=context)
        return new_id
	
    _defaults = { 
                    'bill_date': fields.date.context_today, 
                }	
				


class payment_type_setup(osv.Model):
    """ 
    This will contain the details of the customer and the registration of the customer
    """
    _name = 'payment.type.setup'
    _rec_name='name'
    _description = 'Payment Type'
	
    _columns = {
	    'name':fields.char('Payment Type',required=True,size=20),
		'description':fields.text('Description',size=50),
		'payment_type_created_date':fields.date('Payment Type Created Date',required=True,readonly=True),
		'status':fields.selection(STATUS,'Current Status',select=True),
    }
	
    _defaults = { 
                    'payment_type_created_date': fields.date.context_today, 
                    'status': 'Active',
                }
	
    _sql_constraints = [
        ('unique_name', 
         'unique(name)',
        'This Payment type is already registered.. !')
    ]	
	
class bill_type_setup(osv.Model):
    """ 
    This deals with the bill type setup
    """
    _name = 'bill.type.setup'
    _rec_name='name'
    _description = 'Bill Type'
	
    _columns = {
	    'name':fields.char('Payment Type',required=True,size=20),
		'description':fields.text('Description',size=50),
		'status':fields.selection(STATUS,'Current Status',select=True),
    }
	
    _defaults = { 
                    'status': 'Active',
                }
	
    _sql_constraints = [
        ('unique_name', 
         'unique(name)',
        'This Bill type is already registered.. !')
    ]	
	
	
######### remove if req     
class customer_dynamic_pay(osv.Model):
    _name = 'customer.dynamic.pay'
    _description = 'customer dynamic pay'
    
    def on_change_customer(self,cr,uid,ids,customer_id,context=None):
        
        vals={}
        curr_line_id = {}
        detail_vals = {}
        details_list = []
        #logging.info("************************")
        #cr.execute(''' select customer_name,place from customer_details_setup where id = %s ''',(customer_id,))
        
        cr.execute('''
						select 
								cp.name,
								cds.customer_name,
								cds.mob_no 
						from 
							customer_details_setup cds, 
							customer_place cp
						where 
							cds.address = cp.id and 
							cds.id = %s''',(customer_id,))
		
        customer_header_obj = cr.fetchone()
        logging.info("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")    
        logging.info(customer_header_obj[0])
        logging.info(customer_header_obj[1])
        vals['customer_number'] = customer_header_obj[1]
        vals['customer_place'] = customer_header_obj[0]
        
        cr.execute(''' select id,
					credit_debit_type,debit_amount,credit_amount,
					cre_deb_date,
					--description,
                    bill_num
					from customer_bills_payments where customer_id = %s order by create_date desc ''',(customer_id,))
        customer_obj = cr.fetchall()
        logging.info(customer_obj)
        logging.info("************************")
        #if len(customer_obj)&gt;0:
        
        for i in customer_obj:
            logging.info("******-0--------------")
            logging.info(i)
            dynamic_lines = {
                            'credit_debit_type' : i[1],
                            'debit_amount' : i[2],
                            'credit_amount' : i[3],
                            'customer_id' : customer_id,
							'cre_deb_date' : i[4],
							#'description' : i[5],
					        'bill_num' : i[5],
                            
                            }
            inner_list = [1,i[0],dynamic_lines]
            details_list.append(inner_list)
        vals['dynamic_lines']=details_list
        logging.info(vals)
        logging.info("5555555555555555%%%%%%%%%%%%")
        return {'value':vals}
        #else:
        #    raise osv.except_osv(_('Warning!'),_("No data found"))
            
    
    _columns = {
        'customer_id' : fields.many2one('customer.details.setup','Customer Name',required=True),
        'dynamic_lines':fields.one2many('customer.bills.payments','customer_bill_id'),
        'customer_number' : fields.char('Number',size=40),
        'customer_place' : fields.char('Customer Place',size=30),
    }
    
    def create(self,cr,uid,vals,context=None):
        logging.info("inside create function ************************* ")
        logging.info(vals)
        
        if 'dynamic_lines' in vals:
            for val_list in vals['dynamic_lines']:
                if len(val_list)>0 and val_list[0] == 0:
                    val_list[2]['customer_id'] = vals['customer_id']
                if val_list[2]['credit_debit_type'] == 'credit':
                    val_list[2]['debit'] = 0
                if val_list[2]['credit_debit_type'] == 'debit':
                    val_list[2]['credit'] = 0
                    
        new_id = super(customer_dynamic_pay,self).create(cr,uid,vals,context=context)
        logging.info(new_id)
        return new_id
    
    def write(self,cr,uid,ids,vals,context=None):
        logging.info('$$$$$$$$$$$$$*********************$$$$$$$$$$$$$$$$$')
        logging.info(vals)
        logging.info(ids)
        if vals:
            new_id = super(customer_dynamic_pay,self).write(cr,uid,ids,vals,context=context)
            logging.info("inside write vals **********")
        for individual_record in vals['dynamic_lines']:
            if individual_record[0]==0:
                search_object = self.pool.get('customer.dynamic.pay').search(cr,uid,[('id','=',ids[0])],context=context)
                browse_obj = self.pool.get('customer.dynamic.pay').browse(cr,uid,search_object[0],context=context)
                #logging.info(browse_obj.customer_id.id)
                customer_id = browse_obj.customer_id.id
                #logging.info(search_object)
                cbs_search_ids = self.pool.get('customer.bills.payments').search(cr,uid,[('customer_bill_id','=',ids[0]),('customer_id','=',None)],context=context)
                logging.info(cbs_search_ids)
                cbs_vals = {'customer_id':customer_id}
                for ind_id in cbs_search_ids:
                    logging.info("inside for loop *********")
                    self.pool.get('customer.bills.payments').write(cr,uid,ind_id,vals,context=context)
            
			
        return new_id

## customer wise payments

class customer_bills_payments(osv.Model):
     _name='customer.bills.payments'
     _rec_name = 'customer_name'
     _description = 'customer details'
 
     _columns = {
         'customer_id':fields.many2one('customer.details.setup','Customer Name'),  
         'customer_bill_id' : fields.many2one('customer.dynamic.pay','Dynamic Pay',ondelete="cascade"),     #######           
         'customer_name':fields.char('Customer Name',size=50),
         'place':fields.char('Place',size=100),
         'credit_debit_type': fields.selection(C_OR_D_STATUS,'C / D',size=20,required=True),
		 #'status':fields.selection(STATUS,'Current Status',select=True),
         'bill_id': fields.integer('Bill ID',size=6),
         'bill_num': fields.char('Bill Number',size=26),
         'credit_amount': fields.float('Credit Amount',store=True),
         'debit_amount' : fields.float('Debit Amount',store=True),
         'line_id':fields.integer('Detail_id'),
         'cre_deb_date' : fields.date('Date',required=True),
         'description': fields.char('Description',size=40),
     }	
	 
