import os
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

STATUS=[('yes','YES'),
         ('no','NO')
	   ]
	   
IS_DISCOUNT=[('in time','In Time'),
         ('inactive','Inactive')
	   ]
	   
VAT=[('1',1),
     ('2',2),('3',3)
	   ]
	
	
	
class sac_pay_bill_to_agent(osv.Model):
    """ 
    This will contain the details of the customer bill
    """
    _name = 'sac.pay.bill.to.agent'
    _rec_name='my_own_bill_no'
    _description = 'Customer Details'
	
    def on_changeagent(self, cr, uid ,ids, haste_or_agent=False, context=None):
        val={}
        if haste_or_agent:
            logging.info("inside on change of agent ****************************")
            agent_obj = self.pool.get('sac.agent.details.setup').browse(cr,uid,haste_or_agent,context=context)
            logging.info(haste_or_agent)
            logging.info(agent_obj.agent_mob_no)
            val['haste_mob_num'] = agent_obj.agent_mob_no or False
            return {'value':val}
        return False
		
    def bill_amount_line(self, cr, uid, ids, field, arg, context=None):
        val = 0;
        if 'verify' in context:
            logging.info("################ inside if block");
            logging.info(context)
            res = {}
            search_ids = self.pool.get('sac.manufacturer.bill.details').search(cr,uid,[('sac_pay_bill_to_agent_id','=',ids[0])])
            for line in self.pool.get('sac.manufacturer.bill.details').browse(cr,uid,search_ids,context=context):
                val += line.product_wise_tot_bill
            res[ids[0]] = val
            return res	
        else:
            logging.info("inside else block ################")
            res = {}
            line_id = 0
            for line in self.browse(cr,uid,ids,context=context):
                val += line.bill_amount
                logging.info(self.browse(cr,uid,ids,context=context));
                logging.info("#############################################");
                res[line_id] = val
            return res
			
    def paid_amount_line(self, cr, uid, ids, field, arg, context=None):
        val = 0;
        if 'verify_payment' in context:
            logging.info("$$$$$$$$$$$$$ inside if block $$$$$$$$$$");
            logging.info(context)
            res = {}
            search_ids = self.pool.get('sac.manufacture.payment.details').search(cr,uid,[('sac_pay_bill_to_agent_id','=',ids[0])])
            for line in self.pool.get('sac.manufacture.payment.details').browse(cr,uid,search_ids,context=context):
                val += line.amount
            res[ids[0]] = val
            return res	
        else:
            logging.info("$$$$$$ inside else block ##############")
            res = {}
            line_id = 0
            for line in self.browse(cr,uid,ids,context=context):
                val += line.paid_amount
                logging.info(self.browse(cr,uid,ids,context=context));
                logging.info("#############################################");
                res[line_id] = val
            return res
			
    def Revoke(self,cr,uid,sac_pay_bill_to_agent_id,context=None):
	    return self.pool.get('sac.pay.bill.to.agent').write(cr,uid,sac_pay_bill_to_agent_id,{'state':'new'},context=context)     
	
    def verify(self,cr,uid,sac_pay_bill_to_agent_id,vals,context=None):
        object_search = self.search(cr, uid, [('id','=',sac_pay_bill_to_agent_id)],context=context)
        for i in object_search:
                object_browse = self.browse(cr,uid,i,context=context)
                edit_date = object_browse.bill_entered_date
                edit_discount_before = object_browse.discount_before
                pay_on_today= datetime.datetime.strptime(edit_date,'%Y-%m-%d') + datetime.timedelta(days=edit_discount_before)
        new_tot = 0;
        to_pay_amount =0;
        new_tot_after_discount = 0;
        to_return_amount = 0;
        const_new_tot = 0;
        tot_paid_amount = 0;
        bill_details_obj= self.pool.get('sac.manufacturer.bill.details').search(cr,uid,[('sac_pay_bill_to_agent_id','in',sac_pay_bill_to_agent_id)],context=context)
        payment_details_obj = self.pool.get('sac.manufacture.payment.details').search(cr,uid,[('sac_pay_bill_to_agent_id','in',sac_pay_bill_to_agent_id)],context=context)		
        for i in bill_details_obj:
            sub_bill_det_obj= self.pool.get('sac.manufacturer.bill.details').browse(cr, uid, i ,context=context)
            total=sub_bill_det_obj.product_wise_tot_bill
            const_total = sub_bill_det_obj.product_wise_tot_bill_static
            new_tot = new_tot + total
            const_new_tot = const_new_tot + const_total
        self.pool.get('sac.pay.bill.to.agent').write(cr,uid,sac_pay_bill_to_agent_id,{'pay_on_today':pay_on_today,'bill_amount':new_tot,'bill_amount_manufacture':const_new_tot,'bill_amount_dummy':new_tot,'balance_amount':to_pay_amount},context=context)
        for i in bill_details_obj:
            sub_bill_det_obj= self.pool.get('sac.manufacturer.bill.details').browse(cr, uid, i ,context=context)
            total=sub_bill_det_obj.final_prod_wise_tot
            new_tot_after_discount = new_tot_after_discount + total
        self.pool.get('sac.pay.bill.to.agent').write(cr,uid,sac_pay_bill_to_agent_id,{'new_bill_amount':new_tot_after_discount,'new_bill_amount_dummy':new_tot_after_discount},context=context)
        bill_return_details = self.pool.get('sac.manufacture.return.details').search(cr,uid,[('sac_pay_bill_to_agent_id','in',sac_pay_bill_to_agent_id)],context=context)			
		
        for individual_return in bill_return_details:
            sub_return_det_obj= self.pool.get('sac.manufacture.return.details').browse(cr, uid, individual_return ,context=context)
            return_amount = sub_return_det_obj.new_prod_wise_tot_bill_return
            to_return_amount = to_return_amount + return_amount
        self.pool.get('sac.pay.bill.to.agent').write(cr,uid,sac_pay_bill_to_agent_id,{'return_amount':to_return_amount,'balance_amount':to_pay_amount,'return_amount_dummy':to_return_amount},context=context)			
		
        for individual_payment in payment_details_obj:
            payment_det_obj= self.pool.get('sac.manufacture.payment.details').browse(cr, uid, individual_payment ,context=context)
            payment_amount = payment_det_obj.amount
            tot_paid_amount = tot_paid_amount + payment_amount
        ####context['verify_payment']=True
        self.pool.get('sac.pay.bill.to.agent').write(cr,uid,sac_pay_bill_to_agent_id,{'paid_amount':tot_paid_amount,'paid_amount_dummy':tot_paid_amount},context=context)			
        
        bill_obj= self.search(cr,uid,[('id','in',sac_pay_bill_to_agent_id)],context=context)
        for x in bill_obj:
            bill_object= self.browse(cr, uid, x ,context=context)
            if (bill_object.is_eligible_for_discount == True):
                bal_to_pay = (bill_object.new_bill_amount_dummy) - (bill_object.return_amount_dummy + bill_object.paid_amount)
                if ((bill_object.new_bill_amount_dummy) > (bill_object.return_amount_dummy + bill_object.paid_amount )):
                    logging.info('here 11111111111')
                    logging.info((bill_object.paid_amount < bill_object.new_bill_amount_dummy ))
                    self.write(cr,uid,sac_pay_bill_to_agent_id,{'state':'payment in progress'},context=context)	
                if (bill_object.paid_amount == 0):
                    logging.info('here 2222222222')
                    self.write(cr,uid,sac_pay_bill_to_agent_id,{'state':'billed'},context=context)	
                if ((bill_object.paid_amount + bill_object.return_amount_dummy) == (bill_object.new_bill_amount_dummy)):
                    logging.info('here 33333333333')
                    self.write(cr,uid,sac_pay_bill_to_agent_id,{'state':'payment cleared'},context=context)	
                return self.write(cr,uid,sac_pay_bill_to_agent_id,{'balance_amount':bal_to_pay},context=context)			
            else:
                bal_to_pay = (bill_object.bill_amount_dummy) - (bill_object.return_amount_dummy + bill_object.paid_amount)
                if ((bill_object.paid_amount > 0) and (bill_object.paid_amount < bill_object.bill_amount_dummy)) :
                    self.write(cr,uid,sac_pay_bill_to_agent_id,{'state':'payment in progress'},context=context)	
                if (bill_object.paid_amount == 0):
                    self.write(cr,uid,sac_pay_bill_to_agent_id,{'state':'billed'},context=context)	
                if ((bill_object.paid_amount + bill_object.return_amount_dummy) == (bill_object.bill_amount_dummy)):
                    self.write(cr,uid,sac_pay_bill_to_agent_id,{'state':'payment cleared'},context=context)	
                return self.write(cr,uid,sac_pay_bill_to_agent_id,{'balance_amount':bal_to_pay},context=context)	
        

    _columns = {
	    'my_own_bill_no':fields.char('Bill No',size=20,readonly=True),
        'manufacturer_bill_no':fields.char('Manufacturer Bill No',size=20,required=True),
        'bill_entered_date':fields.date('Bill Entered Date',size=20,readonly=True),
        'manufacturer_name':fields.char('Manufacturer Name',size=50,required=True),
        'transport':fields.many2one('sac.transport.details.setup','Address',required=True),
        'manufacturer_bill_details_line':fields.one2many('sac.manufacturer.bill.details','sac_pay_bill_to_agent_id'),
        'payment_bill_details_line':fields.one2many('sac.manufacture.payment.details','sac_pay_bill_to_agent_id'),
        'return_bill_details_line':fields.one2many('sac.manufacture.return.details','sac_pay_bill_to_agent_id'),
		'bill_notes':fields.text('Notes',size=200),
        'accountability_type': fields.many2one('accountability.type.setup','Bill Type',required=True),
        'haste_or_agent': fields.many2one('sac.agent.details.setup','Agent Name',required=True),	
        'bill_amount':fields.float('Bill Amount',required=True),
		####'bill_amount':fields.function(bill_amount_line,store=True, type='float', string='Bill Amount'),
        'bill_amount_manufacture':fields.float('Bill Amount',required=True,readonly=True),
        'bill_amount_dummy':fields.float('Bill Amount'),
        'new_bill_amount': fields.float('New Bill Amount',size=10),
        'new_bill_amount_dummy' : fields.float('New Bill Amount',size=10),
        'bill_date':fields.date('Manufacturer Bill Date',required=True),
        'discount_before': fields.integer('Pay Before',required=True),
        #'lr_freight': fields.float('LR Freight'),
        #'lr_number': fields.integer('LR Number',size=18,required=True),
		'lr_number': fields.char('LR Number',size=18,required=True),
        'sno': fields.integer('S.No',size=4,required=True),
        'state': fields.selection([('new', 'New'), \
                                    ('billed','Billed'), \
                                    ('payment in progress', 'Payment In Progress'), \
                                    ('payment cleared', 'Payment Cleared'), \
                                    ('cancelled', 'Cancelled')], \
                                'Status', readonly=True, select=True),
        'pay_on_today':fields.date('To Pay on',readonly=True),	
        'balance_amount': fields.float('Remaining Amount to Pay',size=10),
        'paid_amount' : fields.float('Remaining Amount to Pay',size=10),
        ####'paid_amount':fields.function(paid_amount_line,store=True, type='float', string='Remaining Amount to pay'),
        'paid_amount_dummy' : fields.float('Remaining Amount to Pay',size=10),
        'return_amount': fields.float('Return Amount',size=10),
        'return_amount_dummy': fields.float('Return Amount',size=10),
        'final_amount': fields.float('Final Amount',size=10),
        'pre_final_amount': fields.float('Pre Final Amount',size=10),
        #'dalali_amount':fields.float('Dalali Amount'),
        #'dalali_percent': fields.float('Dalali Percent'),
        #'is_eligible_for_discount' : fields.selection(STATUS,'Is Eligible?',select=True),
        'is_eligible_for_discount' : fields.boolean('Eligibility '),
        #'bill_attachment_id':fields.many2one('paid.bill.attachments','Attach'),
    }
    
    def add_attachment(self, cr, uid, ids, context=None):
        logging.info("check for ids in add_arrachment function ********")
        logging.info(ids)
        request_id = self.browse(cr, uid, ids[0], context=None).id
        logging.info(request_id)
        cr.execute('''select id from paid_bill_attachments where bill_attachment_id =%s ''',(request_id,))
        doc_obj = cr.fetchone()
        logging.info("check for doc_obj *****")
        logging.info(doc_obj)
        doc_id = False
        if doc_obj:
            logging.info("yes #######")
            doc_id = doc_obj[0] or False
        return{
                     'type': 'ir.actions.act_window',
                     'name': "Attachments",
                     'res_model': 'paid.bill.attachments',
                     'view_type': 'form',
                     'view_mode': 'form',
                     'target': 'new',
                     'res_id':doc_id,
					 'context':{'bill_attachment_id':request_id,'uid':uid},
		
		        }
	
    _defaults = { 
                    'bill_entered_date': fields.date.context_today,
                    'state': 'new',	
                    'is_eligible_for_discount' : True,
                    'accountability_type' : 1,				
                }
				
    _sql_constraints = [
        ('unique_sno', 
         'unique(sno)',
        'Serial Number is already existed..!! Please Recheck...!!')
    ]
				
    def create(self, cr, uid, vals, context=None):
        if vals:
            logging.info("inside create function ##########")
            logging.info(vals)
            dis_b4 = int(vals['discount_before'])
            tme=vals['bill_date']
            vals['pay_on_today'] = datetime.datetime.strptime(tme,'%Y-%m-%d') + datetime.timedelta(days=dis_b4)
            #new_date = datetime.datetime.strptime(tme,'%Y-%m-%d') + datetime.timedelta(days=dis_b4)
            vals['my_own_bill_no']= self.pool.get('ir.sequence').get(cr,uid,'sac.pay.bill.to.agent.sequence')
            return super(sac_pay_bill_to_agent,self).create(cr,uid,vals,context=context)
			
    def copy(self,cr,uid,id,default=None,context=None):
        raise osv.except_osv(_('Forbidden to duplicate'),_('Not possible to duplicate the bill'))
		
	
    
            # return self.pool.get('sac.pay.bill.to.agent').write(cr,uid,ids,{'pay_on_today':pay_on_today},context=context)
		
class sac_manufacturer_bill_details(osv.Model):
    """ 
    This will contain the bill details
    """
    _name = 'sac.manufacturer.bill.details'
    _rec_name='sac_pay_bill_to_agent_id'
    _description = 'Manufacturer Bill Details'
	
    def on_change_product(self,cr,uid,ids,sac_class_setup_id,context=None):
        vals={}
        if classification_setup_id:
            classification_obj = self.pool.get('sac.class.setup').browse(cr,uid,sac_class_setup_id,context=context)
        vals['price']=classification_obj.price
        return {'value':vals}
		
    def on_change_prices(self,cr,uid,ids,price,quantity,discount_in_per,discount_per_piece,context=None):
        vals={}
        item_total=price*quantity
        logging.info(item_total)
        vals['product_wise_tot_bill']=item_total
        vals['product_wise_tot_bill_static'] = item_total
        vals['final_prod_wise_tot'] = item_total
        return {'value':vals}
		
    def on_change_price(self,cr,uid,ids,price,quantity,discount_in_per,discount_per_piece,return_qty,context=None):
        vals={}
        item_total=price*(quantity - return_qty)
        item_total_manf=price*(quantity)
        logging.info(item_total)
        vals['product_wise_tot_bill']=item_total
        vals['product_wise_tot_bill_static'] = item_total_manf
        logging.info("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
        new_price = price - discount_per_piece
        logging.info(new_price)
        logging.info((float(discount_in_per/100.0)*price))
        new_price_new = float(new_price) - (float(discount_in_per/100.0)*new_price)
        logging.info("$$$$$$$$$$$$$$$$$$$$$$$$$$");
        logging.info(new_price_new)
        #updated_price = new_price - discount_per_piece
        vals['new_price'] = new_price_new
        item_total_after_disc = new_price_new * (quantity - return_qty)
        vals['final_prod_wise_tot'] = item_total_after_disc
        return {'value':vals}
		
    
	
    _columns = {
	    'sac_pay_bill_to_agent_id':fields.many2one('sac.pay.bill.to.agent'),
        'product_name':fields.char('Product Name'),
		'quantity':fields.float('Quantity',size=10),
		'description':fields.char('Description',size=100),
		'price':fields.float('Price(per piece)',size=7,required=True),
		'product_wise_tot_bill':fields.float('Sub Total',required=True,size=10),
        'product_wise_tot_bill_static': fields.float('Sub Total',size=10,),
        'discount_in_per' : fields.float('% discount',size=4),
        'discount_per_piece': fields.float('Dis/Pc',size=5),
        'return_qty': fields.float('Return Qty',size=5),
        'new_price':fields.float('New Price ?',size=7,),
        'final_prod_wise_tot': fields.float('Final Sub Tot',size=10),
        #'sac_pay_bill_to_agent_id':fields.many2one('sac.pay.bill.to.agent'),
    } 
		
class sac_manufacture_payment_details(osv.Model):
    """ 
    This will contain the payment details of us to the manufacturer
    """
    _name = 'sac.manufacture.payment.details'
    _rec_name='sac_pay_bill_to_agent_id'
    _description = 'Payment Details'
	
    
    _columns = {	
	    'sac_pay_bill_to_agent_id':fields.many2one('sac.pay.bill.to.agent'),
        'date':fields.date('Date'),
		'amount':fields.float('Amount',size=10),
		'description':fields.char('Description',size=100),
		'payment_type': fields.many2one('payment.type.setup'),
        
    }

class sac_manufacture_return_details(osv.Model):
    """ 
    This will contain the payment details of us to the manufacturer
    """
    _name = 'sac.manufacture.return.details'
    _rec_name='sac_pay_bill_to_agent_id'
    _description = 'Return Details'
	
    '''def on_change_price(self,cr,uid,ids,qty,amount,context=None):
        vals={}
        item_total= qty * amount
        logging.info(item_total)
        vals['prod_wise_tot_bill_return']=item_total
        #vals['final_prod_wise_tot'] = item_total
        return {'value':vals}
	'''	
    def on_change_prices(self,cr,uid,ids,amount,qty,discount_in_per,discount_per_piece,context=None):
        vals={}
        #after_discount_per_peice = 0
        item_total= qty * amount
        logging.info("item total ***********")
        logging.info(item_total)
        vals['prod_wise_tot_bill_return']=item_total
        tot_piece_less = amount * discount_per_piece
        logging.info("kkkkkkkkkkkkkkkkkk")
        logging.info(tot_piece_less)
        logging.info("jjjjjjjjjjjjjjjjjjjjjjjj")
        logging.info(qty)
        logging.info("&&&&&&&&&&&&&&------------")
        logging.info(amount)
        logging.info("@%^&&^^^^^^^^^^^^%%%%%%%$$$$$$######~~~~~~~~~")
        logging.info(discount_per_piece)
		###########################   check on change functionality of return products and new return amount to be deduced... do this in development & change it in production..
        disc_piece_less = item_total - tot_piece_less
        logging.info("##!!!!!!!!!!!!!!!!!!!!!@@@@@@@@@@")
        logging.info(disc_piece_less)
        tot_per_disc = (disc_piece_less * discount_in_per) / 100
        logging.info("^^^^^^^^^^^^%%%%%%%%%")
        logging.info(tot_per_disc)
        per_wise_disc = disc_piece_less - tot_per_disc
        logging.info("$$$$$$$$$")
        logging.info(per_wise_disc)
        vals['new_price'] = per_wise_disc
        vals['new_prod_wise_tot_bill_return'] = per_wise_disc		
        return {'value':vals}
	
    
    _columns = {	
	    'sac_pay_bill_to_agent_id':fields.many2one('sac.pay.bill.to.agent'),
        'product_name': fields.char('Product Name',size=25),
        'qty': fields.float('Quantity',size=5),
		'amount':fields.float('Amount',size=10),
		'description':fields.char('Description',size=100),
        'prod_wise_tot_bill_return': fields.float('Product Wise Bill',size=10),
		
        'discount_in_per' : fields.float('% discount',size=4),
        'discount_per_piece': fields.float('Dis/Pc',size=5),
        'new_price':fields.float('New Price ?',size=7,),
        'new_prod_wise_tot_bill_return': fields.float('Product Wise Bill',size=10),
    }	
		
		
''' agent details'''

class sac_agent_details_setup(osv.Model):
    """ 
    This will contain the details of the customer and the registration of the customer
    """
    _name = 'sac.agent.details.setup'
    _rec_name='agent_name'
    _description = 'Customer Details'
	
    _columns = {
	    'agent_name':fields.char('Agent Name',required=True,size=50),
		'agent_mob_no':fields.char('Mobile Number',size=10,required=True),
		'agent_registered_date':fields.date('Customer Entry Date',required=True,readonly=True),
		'status':fields.selection(STATUS,'Current Status',select=True),
        'address':fields.char('Address',size=2000),
		
    }
	
    _defaults = { 
                    'agent_registered_date': fields.date.context_today, 
                    'status':'yes',
                    'address':'Chirala'
                }
	
    _sql_constraints = [
        ('unique_agent_mob_no', 
         'unique(agent_mob_no)',
        'This Agent or Mobile number is already registered...!!')
    ]
	
'''Transport Details'''

''' agent details'''

class sac_transport_details_setup(osv.Model):
    """ 
    This will contain the details of the customer and the registration of the customer
    """
    _name = 'sac.transport.details.setup'
    _rec_name='transport_name'
    _description = 'Transport Details'
	
   
    _columns = {
	    'transport_name':fields.char('Transport Name',required=True,size=50),
		'transport_mob_no':fields.char('Mobile Number',size=15,required=True),
		'transport_registered_date':fields.date('Transport Entry Date',required=True,readonly=True),
		'status':fields.selection(STATUS,'Current Status',select=True),
        'address':fields.char('Address',size=2000),
		
    }
	
    _defaults = { 
                    'transport_registered_date': fields.date.context_today, 
                    'status':'yes',
                    'address':'Chirala'
                }
	
    _sql_constraints = [
        ('unique_transport_name', 
         'unique(transport_name)',
        'This Transport is already registered...!!')
    ]
		
class accountability_type_setup(osv.Model):
    """ 
    This deals with the bill type setup
    """
    _name = 'accountability.type.setup'
    _rec_name='name'
    _description = 'Accountability Type'
	
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
        'This Accountability type is already registered.. !')
    ]
	
class paid_bill_attachments(osv.Model):
    _name ='paid.bill.attachments'
    _columns = {
    'name': fields.char('Document Name',store=False,),
    'attachment' : fields.binary('Attachment',store=False,),   
    'bill_attachment_id': fields. many2one('sac.pay.bill.to.agent','SPBA Id',ondelete='cascade',),
    'document_attachment_id' : fields.one2many('paid.bill.attachments.detail','document_id','Document Id',editable=True),
    'attachment_text':fields.char(string = 'Filename',store=False),
    }
    def add_attachment(self,cr,uid,ids,context=None):
         
        bill_attachment_id=context.get('bill_attachment_id',False)
        cr.execute('''select id,name,attachment,attachment_text from paid_bill_attachments where id=%s''',(str(ids[0]),))
        detail=cr.fetchone()
        attach_id=detail[0]  
        document_name = detail[1]
        attachment = detail[2]
        attachment_text=detail[3] 
                              
        if document_name:
            if attachment:
                FILE_TYPES=['.jpeg','.jpg','.png', '.xlsx','.pdf','.ppt','.txt','.doc','.docx','.xls','.ods','.pdf']
                fileName, fileExtension = os.path.splitext(str(attachment_text))
                if not fileExtension in FILE_TYPES:
                    raise osv.except_osv(('Error!'),('Allowed formats for uploading attachments - jpeg, jpg, png, pdf,  ppt, txt, doc, docx, xls, ods, pdf,xlsx'))                
                self.write(cr,uid,attach_id,{'bill_attachment_id':bill_attachment_id,},context=None)
                
                self.pool.get('paid.bill.attachments.detail').create(cr,uid,{'name':document_name,'attachment':attachment,'document_id':ids[0],'attachment_text':attachment_text},context=None)
            else:
                Warning ="Please attach the file for "+document_name
                raise osv.except_osv(('Warning!'),(Warning)) 
        else:
            Warning = "Please enter the Document Name"
            raise osv.except_osv(('Warning!'),(Warning))
        self.write(cr,uid,ids[0],{'name':'','attachment':'','attachment_text':''},context=None)
        return {
                     'type': 'ir.actions.act_window',
                     'name': "Attachment",
                     'res_model': 'paid.bill.attachments',
                     'view_type': 'form',
                     'view_mode': 'form',
                     'target': 'new',
                     'res_id':ids[0],
                    }
    def delete_attachment(self, cr, uid, ids, context=None):
         
        cr.execute('''SELECT pbd.id 
							 FROM paid_bill_attachments pbd  join paid_bill_attachments_detail pbad 
							 on pbd.id=pbad.document_id 
							 where pbad.attach_check_box=true and pbad.id='%s' ''',(ids[0],))
        delete_attachment=cr.fetchall()
        logging.info(delete_attachment)
        if delete_attachment:
            for id in delete_attachment:
                self.pool.get('paid.bill.attachments.detail').unlink(cr,uid,id,context=None)
        else:
            Warning = "Please select atleast one attachment"
            raise osv.except_osv(('Warning!'),(Warning))
        return {
                     'type': 'ir.actions.act_window',
                     'name': "Attachment",
                     'res_model': 'paid.bill.attachments',
                     'view_type': 'form',
                     'view_mode': 'form',
                     'target': 'new',
                     'res_id':ids[0],
                         
                    }
class paid_bill_attachments_detail(osv.Model):
    _name ='paid.bill.attachments.detail'
    _columns = {
    'attach_check_box':fields.boolean(' ',default=False),
    'name': fields.char('Document Name'),
    'attachment' : fields.binary('Attachment'),
    'document_id' : fields.many2one('paid.bill.attachments','Attachment', required=True, ondelete='cascade',attachment=True,),
    'attachment_text':fields.char(string = 'Filename'),
    
    }
    def download(self,cr,uid,ids,context=None):
        logging.info(ids[0])
        return { 'type': 'ir.actions.act_url', 'url': '/stock_pk/download?id='+ str(ids[0]) + '&db='+ str(cr.dbname) + '&uid=' + str(uid)+'&model=paid.bill.attachments.detail', 'nodestroy': True, 'target': 'new'}