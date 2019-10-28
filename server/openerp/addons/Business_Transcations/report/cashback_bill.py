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
import cashback


class bill_report_generation(report_sxw.rml_parse):
    active_id = 0
    def __init__(self, cr, uid, name, context):
        global active_id
        active_id = context['active_ids']
        logging.info("Inside INIT function **");
        bill_report_generation.active_id = active_id 
        super(bill_report_generation, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
									'get_bill_report': self.get_bill_report,
		})		
		
    def get_bill_report(self, data):
        total_bill = {}
        bill_header = {}
        bill_detail = {}
        total_bill_list = []
        cashback_bill_id = bill_report_generation.active_id[0]
		
        query1 = """ select 	cb.id,	
							cb.bill_no,
							cb.bill_amount,
							cds.amount_in_wallet,
							to_char(cb.bill_date,('dd/mm/YYYY')) as bill_date,
							cb.discount_for_next_purchase,
							cb.pay_final_bill,
							cb.customer_name,
							cds.mob_no
					from 	
							customer_bill as cb,
							customer_details_setup as cds
					where 	
							cb.id = %s and
							cb.customer_name = cds.id"""
							
        self.cr.execute(query1,(cashback_bill_id,))
        logging.info(query1)
        bill_header = self.cr.dictfetchone()
        total_bill.update({'bill_header':bill_header})
		
        query2 = """select  product_name,
							description,
							quantity,
							price,
							product_wise_tot_bill
					from 	
							customer_bill_details
					where customer_bill_id = %s"""
					
        self.cr.execute(query2, (cashback_bill_id,))
        bill_detail = self.cr.dictfetchall()
        #total_bill.append(bill_detail)
        total_bill.update({'bill_detail':bill_detail})
        total_bill_list.append(total_bill)
        logging.info(total_bill);
        logging.info("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%");
        return total_bill_list
		
report_sxw.report_sxw('report.bill_report','customer.bill','addons/cashback/report/cashback.rml',parser = bill_report_generation, header =  False)