from openerp.osv import fields, osv
#from openerp import models, fields, api
#from openerp.exceptions import ValidationError
import xlwt
from excel_styles import ExcelStyles
import os, glob
import re
from xlrd import open_workbook
import base64
import cStringIO
import datetime 
import time
import json
from datetime import date
import locale
from decimal import Decimal
import xlsxwriter
from operator import add
import logging
from report import report_sxw
from excel_styles import ExcelStyles
from __builtin__ import str


class cashback_file_data(osv.Model):
     _name = 'cashback.file.data'
     
     _columns = {
         'data': fields.binary('File', readonly=True),
         'name': fields.char('Filename', 50, readonly=True),
    }
     

class cashback_summary(osv.Model):
    _name = 'cashback.summary'
    _columns = {
        'from_date': fields.date('From Date',required=True),
        'to_date': fields.date('To Date',required=True),
        'report_data': fields.binary('File', readonly=True),
        'name': fields.char('Filename', 50, readonly=True),
    }    
	
    _defaults = { 
        'from_date':date(date.today().year, date.today().month, 1).strftime('%Y-%m-%d'),
        'to_date': date.today().strftime('%Y-%m-%d'),
        
    }
    
    
    def date_format(self,cr,uid,ids,date):
        return datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%d/%m/%Y')
    
    ''' 
        This method will check the valid from date and to date.
    '''
    @staticmethod
    def check_valid_date(from_date,to_date):
        if to_date < from_date:
            raise osv.except_osv(('Error!'),('From date should be less than To date.'))
            return False
        else:
            return True
			
    def get_input_values(self,cr,uid,ids,context=None):
            out=cStringIO.StringIO()
            data = self.read(cr, uid, ids, [], context = context)[0]
            from_date = data['from_date']
            to_date = data['to_date']
            
            
            if cashback_summary.check_valid_date(from_date,to_date):               
                query = """  select 
								customer.customer_name,
								customer.mob_no,
								to_char(customer.write_date,'dd/mm/yyyy'),
								place.name,
								customer.amount_in_wallet 
						from 
								customer_details_setup customer,
								customer_place place,
								customer_bill ccb
						where 
								customer.address = place.id	"""
										
                if data['from_date'] > data ['to_date']:
                    raise osv.except_osv(('Waring!'),('From Date cannot greater than To Date'))
				#to_char(est_start_date,'dd/mm/yyyy'),	
                if data['from_date']:
                    from_date_condition = " and to_char(ccb.bill_date,'yyyy-mm-dd')  >='%s' " % (str(data['from_date']),)
                    query = query + from_date_condition
            
                if data['to_date']:
                    to_date_condition = " and to_char(ccb.bill_date,'yyyy-mm-dd') <='%s'" % (str(data['to_date']),)
                    query = query + to_date_condition  

                bill_order_by_condition=" order by ccb.bill_date"
                query = query + bill_order_by_condition
                
                    
                cr.execute(query,())
                result= cr.fetchall()  
                logging.info("************>>>>>>>>>>>>>>>>>>>");
                logging.info(query)
                logging.info(result)
                list1=[]
                list2=[]
                list3=[]
                list4=[]
                list5=[]
                #list6 = []
                
                serial_no=1
                for res in result :
                    logging.info(res)
                    list1.append(res[0])
                    list2.append(res[1])
                    list3.append(res[2])
                    list4.append(res[3])
                    list5.append(res[4])
                    #list6.append(res[5])
              
                   
                data=[]
                #if result == []:    
                     #raise osv.except_osv(('Warning!'),('No Employee Resigned for any Reason'))    
                #else: 
               
                report_data = self.read(cr, uid, ids, [], context=context)[0]
                workbook = xlsxwriter.Workbook(out)
                Style = ExcelStyles()
                worksheet = workbook.add_worksheet('Cashback Summary')
                
                #format = workbook.add_format()
                #format.set_text_wrap()

                #worksheet.write(0, 0, "Some long text to wrap in a cell", format)
                bold=workbook.add_format({'bold':1})
                col_color=workbook.add_format({'bg_color':'#99CCFF','border':1,'bold': 2,'align': 'center'})
                col_color.set_text_wrap()
                col_color_bal1=workbook.add_format({'bg_color':'#73CDFF','border':1,'bold': 2,'align': 'right'})
                col_color_bal1.set_text_wrap()
                col_color_bal2=workbook.add_format({'bg_color':'#26CEFF','border':1,'bold': 2,'align': 'right'})
                col_color_bal2.set_text_wrap()
                head_color=workbook.add_format({'bg_color':'#80880'})
                set_center=workbook.add_format({'bg_color':'#99CCFF','border':1,'bold': 2,'align': 'center'})
                merge_format = workbook.add_format({
                                                    'bold': 1,
                                                    'border': 1,
                                                    'align': 'center',
                                                    'valign': 'vcenter',
                                                    'fg_color': '#C0C0C0'})
                
                serial_no = 1
                
                worksheet.set_column(0, 0, 8)
                worksheet.set_row(1,20)
                worksheet.set_column(1, 1, 30)
                worksheet.set_column(2, 2, 15)
                worksheet.set_column(3, 3, 20)
                worksheet.set_column(4, 4, 24) 
                worksheet.set_column(5, 5, 20)
                
                # Create a new Chart object.
                chart = workbook.add_chart({'type': 'column'}) 
               # Write some data to add to plot on the chart.
                data_headings=['S.No','Customer Name','Mobile Number','Last Bill Date','Place','Wallet Amount']
               
                data = [ list1,list2,list3,list4,list5]
				
                logging.info("check for individual list values %%%%%%%%%%%%%%%%%%%%")
                logging.info(data)
                list1_len=len(list1)
                list2_len=len(list2)
                list3_len=len(list3)
                list4_len=len(list4)
                list5_len=len(list5)
                #list6_len=len(list6)
                
                sno1=1
                list_sno1=[]
                for sno in list1:
                    list_sno1.append(sno1)
                    sno1=sno1+1
                    
                
                worksheet.merge_range('A1:F1',"  Cashback Summary Details between " + datetime.datetime.strptime(from_date, '%Y-%m-%d').strftime('%d/%m/%Y')+" "+" and "+" "+datetime.datetime.strptime(to_date, '%Y-%m-%d').strftime('%d/%m/%Y'),merge_format)
                worksheet.write('A2', data_headings[0],col_color)
                worksheet.write('B2', data_headings[1],col_color)
                worksheet.write('C2', data_headings[2],col_color)
                worksheet.write('D2', data_headings[3],col_color)
                worksheet.write('E2', data_headings[4],col_color)
                worksheet.write('F2', data_headings[5],col_color)
              
                #for res in data:
                worksheet.write_column('A3',list_sno1)
                worksheet.write_column('B3', data[0])
                worksheet.write_column('C3', data[1])
                worksheet.write_column('D3', data[2])
                worksheet.write_column('E3', data[3])
                worksheet.write_column('F3', data[4])
                      
                workbook.close()
                output_data =out.getvalue()
                advice = ('Save this document to a .xls file.')
                self.write(cr, uid, ids, {'report_data':output_data, 'advice':advice, 'name':'Cashback_Summary_Report'}, context=None)
                #return { 'type': 'ir.actions.act_url', 'url': '/am_pk/export_income_report?id='+ str(ids[0]) + '&db='+ str(cr.dbname) + '&uid=' + str(uid), 'nodestroy': True, 'target': 'new'}                    
                return { 'type': 'ir.actions.act_url', 'url': '/cashback/export_cashback_report?id='+ str(ids[0]) + '&db='+ str(cr.dbname) + '&uid=' + str(uid),'nodestroy': True, 'target': 'new'}				
               
         
    
    
    