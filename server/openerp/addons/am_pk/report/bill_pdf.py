#
#    Author : Pavan Kota
#

import time
from openerp import pooler
from openerp.report import report_sxw
from openerp.osv import osv, fields
#from tools import amount_to_text_in
from osv import osv
#from tools import amount_to_text_en
import logging
from datetime import datetime
from dateutil import parser
import base64
import am_pk

class bill_balance_details_report(report_sxw.rml_parse):    
    
    def __init__(self, cr, uid, name, context):
        logging.info('in INIT')
        super(bill_balance_details_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({     
                'get_balance_payments' : self.get_balance_payments,
        })
    
    def get_balance_payments(self,data):
        filter = []
        query = """ select 
							bill_no,
							bill_amount,
							bill_date,
							cp.name,
							state,
							balance_to_pay,
							ccb.customer_name,
							cds.mob_no 
					from    credit_customer_bill as ccb,
							customer_place as cp, 
							customer_details_setup as cds
					where   ccb.customer_address = cp.id and
	                        ccb.customer_address = cp.id and 
	                        cds.id = ccb.mob_no and 
							bill_date >= %s::date and 
							bill_date <= %s::date order by bill_no""";
        
        user_condition="";
        if data['state']:
            user_condition="and state = % (data['state'])"
            query = query + user_condition
        new_user_condition="";
        if data['mob_no']:
            new_user_condition="and ccb.mob_no =%s" % (data['ccb.mob_no'])
            query = query + new_user_condition
        
        self.cr.execute(query,(data['from_date'],data['to_date']) )
        form_data=self.cr.dictfetchall()
        ids = []
        if len(ids) <= 0:
            raise osv.except_osv("Warning !","No Data Found !!")
            return  False    
        else:
            logging.info("check reservation data ***********************************")
            return form_data
                
report_sxw.report_sxw('report.bill_balance_details_report','credit.customer.bill.payment.report','addons/am_pk/report/bill_pdf.rml',parser=bill_payment_report, header=False)

class credit_customer_bill_detail_report(osv.Model):
    _name = 'credit.customer.bill.payment.report'
    
    _columns = {
        'from_date': fields.date('From Date'),
        'to_date': fields.date('To Date'),
        'address': fields.many2one('customer.place','Place'),
        'state': fields.many2one([('new', 'New'), \
                                    ('billed', 'Billed'), \
                                    ('payment in progress', 'Payment In Progress'), \
                                    ('payment cleared', 'Payment Cleared'), \
                                    ('cancelled', 'Cancelled')], \
                                'Status', readonly=True, select=True),
        'mob_no': fields.many2one('customer.details.setup','Customer Name'),
    }
    
    _defaults = {
        'from_date' : lambda *a: ((time.strftime('%Y-%m')) + '-01'),
        'to_date': lambda *a: time.strftime('%Y-%m-%d'),
    }


    def print_bill_details(self,cr,uid,ids,context=None):
        logging.info('inside the function ***************');
        this = self.browse(cr, uid, ids)[0]
        meeting_id =False
        empl =False
        if this.state:
            project_id=this.state;
        if this.mob_no:
            mob_no=this.mob_no.id;
            
        #data = self.read(cr, uid, ids, [], context=context)[0]
        data = {
             'model':'credit.customer.bill.payment.report',
             'from_date':this.from_date,
             'to_date':this.to_date,
             'state':this.state,
             'mob_no': this.mob_no,
        }
        
        logging.info(data)
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'bill_payment_details',
            'datas':data,
        }
