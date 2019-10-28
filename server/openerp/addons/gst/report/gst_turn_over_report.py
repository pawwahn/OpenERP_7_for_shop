from openerp.osv import fields, osv
import xlwt
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

FIRM=[('New KrishnaArjuna Textiles','New KrishnaArjuna Textiles'),
          ('Subhamastu Saree House','Subhamastu Saree House'),
	    ]

TYPE=[('purchase','Purchase'),
          ('sales','Sales')
	    ]

class gst_turnover_report(osv.Model):
    
    _name = 'gst.turnover.report'
    _columns = {
        'firm':fields.selection(FIRM,'Firm',required=True,select=True),
        'financial_year': fields.many2one('gst.financial.years','Financial Year',required=True),
        'report_data': fields.binary('File', readonly=True),
        'name': fields.char('Filename', size=50, readonly=True),
        
    }

    def get_report(self,cr,uid,ids,context=None):
            out=cStringIO.StringIO()
            datas = self.read(cr, uid, ids, [], context = context)[0]
            firm = datas['firm']
            financial_year = datas['financial_year'][0]
			
            if firm and financial_year:
                logging.info("*******************************")
                logging.info(firm)
                logging.info(financial_year)
                purchase_query = """    select 
										 month,bill_amount,total_tax,total_bill_amount
								from 
										 gst_header_purchase as ghp,gst_financial_years as gfy 
								where 
										 firm = %s and ghp.financial_year = gfy.id and ghp.financial_year = %s order by ghp.create_date 
		
						"""
                cr.execute(purchase_query,(firm,financial_year))
                purchase_records= cr.fetchall()  
            
                sales_query = """    select 
										month,bill_amount,total_tax,total_bill_amount
								from 
										 gst_header_sales as ghs,gst_financial_years as gfy 
								where 
										 firm = %s and ghs.financial_year = gfy.id and ghs.financial_year = %s order by ghs.create_date 
		
						"""
                cr.execute(sales_query,(firm,financial_year))
                sale_records= cr.fetchall() 
            else:
                raise osv.except_osv(_('Invalid Selction'),_('-- Please select both the data  --'))

            list_purchase_month=[]
            list_purchase_bill_amount=[]
            list_purchase_total_tax=[]
            list_purchase_tot_bill_amount=[]
			
            list_sales_month=[]
            list_sales_bill_amount=[]
            list_sales_total_tax=[]
            list_sales_tot_bill_amount=[]
            serial_no=1
            for res in purchase_records :
		        list_purchase_month.append(res[0])
		        list_purchase_bill_amount.append(res[1])
		        list_purchase_total_tax.append(res[2])
		        list_purchase_tot_bill_amount.append(res[3])
				
            for res in sale_records :
		        list_sales_month.append(res[0])
		        list_sales_bill_amount.append(res[1])
		        list_sales_total_tax.append(res[2])
		        list_sales_tot_bill_amount.append(res[3])
				
				
            data=[]
            report_data = self.read(cr, uid, ids, [], context=context)[0]
            workbook = xlsxwriter.Workbook(out)
            Style = ExcelStyles()
            if datas['firm'] == 'New KrishnaArjuna Textiles':			
                worksheet = workbook.add_worksheet("NKT's TURNOVER REPORT")
            else:
                worksheet = workbook.add_worksheet("SSH's TURNOVER REPORT")
            			
            bold=workbook.add_format({'bold':1})
            col_color=workbook.add_format({'bg_color':'#99CCFF','border':1,'bold': 2,'align': 'center'})
            col_color.set_text_wrap()
            col_color2=workbook.add_format({'border':1,'bold': 2,'align': 'left'})
            col_color3=workbook.add_format({'border':1,'bold': 2,'align': 'right'})
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
            merge_format2 = workbook.add_format({
                                                    'bold': 1,
                                                    'border': 1,
                                                    'align': 'center',
                                                    'valign': 'vcenter',
                                                    'fg_color': '#48C9B0'})
            serial_no = 1
            #worksheet.set_column(0, 0, 5)
            worksheet.set_row(1,20)
            worksheet.set_column(0, 0, 10)
            worksheet.set_column(1, 1, 15)
            worksheet.set_column(2, 2, 10)
            worksheet.set_column(3, 3, 11)
            #worksheet.set_column(4, 4, 20) 
            #worksheet.set_column(5, 5, 15)
            worksheet.set_column(6, 6, 10) 				
            worksheet.set_column(7, 7, 15)
            worksheet.set_column(8, 8, 10)
            worksheet.set_column(9, 9, 11)
			
            data_headings=['MONTH','PURCHASE VALUE','TOTAL TAX','TOTAL     ','MONTH','SALE VALUE','TOTAL TAX','TOTAL     ']
				   
            data = [ list_purchase_month,list_purchase_bill_amount,list_purchase_total_tax,list_purchase_tot_bill_amount,
			         list_sales_month,list_sales_bill_amount,list_sales_total_tax,list_sales_tot_bill_amount]
					
            list1_len=len(list_purchase_month)
            list2_len=len(list_purchase_bill_amount)
            list3_len=len(list_purchase_total_tax)
            list4_len=len(list_purchase_tot_bill_amount)
            list5_len=len(list_sales_month)
            list6_len=len(list_sales_bill_amount)
            list7_len=len(list_sales_total_tax)
            list8_len=len(list_sales_tot_bill_amount)
            
            if datas['firm']=='New KrishnaArjuna Textiles':	
                worksheet.merge_range('A1:J1',"  KOTA LAKSHMI RADHA SUVARCHALA , GST NO: 37CPQPK4284H1Z3",merge_format)
                worksheet.merge_range('A2:J2', "PROP : " + datas['firm'] + " , MGC MARKET, SHOP NO: 302,CHIRALA"  ,merge_format2)
            else:
                worksheet.merge_range('A1:J1',"  KOTA PADMAJA RANI ,GST NO: 37BZAPK0778D1ZH ",merge_format)
                worksheet.merge_range('A2:J2', "PROP : " + datas['firm'] + " , MGC MARKET, SHOP NO: 304,CHIRALA",merge_format2)
							
            worksheet.merge_range('A3:J3'," DETAILS OF TURNOVER DURING THE FINANCIAL YEAR "+ datas['financial_year'][1],merge_format)
            worksheet.merge_range('A5:D5'," PURCHASE DETAILS ",merge_format2)
            worksheet.merge_range('G5:J5'," SALE DETAILS ",merge_format2)
			
            worksheet.write('A7', data_headings[0],col_color)
            worksheet.write('B7', data_headings[1],col_color)
            worksheet.write('C7', data_headings[2],col_color)
            worksheet.write('D7', data_headings[3],col_color)
            
            worksheet.write('G7', data_headings[4],col_color)
            worksheet.write('H7', data_headings[5],col_color)
            worksheet.write('I7', data_headings[6],col_color)
            worksheet.write('J7', data_headings[7],col_color)			
			
            worksheet.write_column('A9',data[0],col_color3)
            worksheet.write_column('B9', data[1],col_color3)
            worksheet.write_column('C9', data[2],col_color3)
            worksheet.write_column('D9', data[3],col_color3)
           
            worksheet.write_column('G9', data[4],col_color3)
            worksheet.write_column('H9', data[5],col_color3)
            worksheet.write_column('I9', data[6],col_color3)				
            worksheet.write_column('J9', data[7],col_color3)
			
            n=9; 			
            for e in data[2]:
                f=len(data[2])
                worksheet.write_formula(('B%s')%(list1_len+9),('{=sum(B9:B%s)}')%(n),col_color_bal1)
                #worksheet.write_formula(('D%s')%(f+o),('{=sum(d5:d%s)}')%(n),col_color_bal1)
                n=n+1
			
            n=9;  
            for e in data[2]:
                f=len(data[2])
                worksheet.write_formula(('C%s')%(f+9),('{=sum(c9:c%s)}')%(n),col_color_bal1)
                n=n+1
			
            n=9;  
            for e in data[2]:
                f=len(data[2])
                worksheet.write_formula(('D%s')%(f+9),('{=sum(d9:d%s)}')%(n),col_color_bal1)
                n=n+1
			
            n=9;  
            for e in data[5]:
                f=len(data[5])
                worksheet.write_formula(('H%s')%(f+9),('{=sum(h9:h%s)}')%(n),col_color_bal1)
                n=n+1
			
            n=9;  
            for e in data[5]:
                f=len(data[5])
                worksheet.write_formula(('I%s')%(f+9),('{=sum(i9:i%s)}')%(n),col_color_bal1)
                n=n+1
				
            n=9;  
            for e in data[5]:
                f=len(data[5])
                worksheet.write_formula(('J%s')%(f+9),('{=sum(j9:j%s)}')%(n),col_color_bal1)
                n=n+1

            workbook.close()
            output_data =out.getvalue()
            advice = ('Save this document to a .xlsx file.')
            self.write(cr, uid, ids, {'report_data':output_data}, context={})
            return { 'type': 'ir.actions.act_url', 'url': '/gst/export_gst_turnover_report?id='+ str(ids[0]) + '&db='+ str(cr.dbname) + '&uid=' + str(uid), 'nodestroy': True, 'target': 'new'}                    				
