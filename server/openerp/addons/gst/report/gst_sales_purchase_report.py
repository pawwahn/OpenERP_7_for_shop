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

class gst_sales_purchase_report(osv.Model):
    
    _name = 'gst.sales.purchase.report'
    _columns = {
        'firm':fields.selection(FIRM,'Firm',required=True,select=True),
        'financial_year': fields.many2one('gst.financial.years','Financial Year',required=True),
        'report_data': fields.binary('File', readonly=True),
        'name': fields.char('Filename', size=50, readonly=True),
		'type':fields.selection(TYPE,'Type',required=True,select=True),
    }

    def get_report(self,cr,uid,ids,context=None):
            out=cStringIO.StringIO()
            datas = self.read(cr, uid, ids, [], context = context)[0]
            firm = datas['firm']
            financial_year = datas['financial_year'][0]
            
            if datas['type'] == 'purchase':			
                purchase_query = """    select 
			                                 month,fin_year,bill_amount,total_igst,total_cgst,total_sgst,total_tax,total_bill_amount
									from 
									         gst_header_purchase as ghp,gst_financial_years as gfy 
									where 
									         firm = %s and ghp.financial_year = gfy.id and ghp.financial_year = %s order by ghp.create_date 
			
							"""
                cr.execute(purchase_query,(firm,financial_year))
                detail_result= cr.fetchall()  
            if datas['type'] == 'sales':
                sales_query = """    select 
			                                month,fin_year,bill_amount,total_igst,total_cgst,total_sgst,total_tax,total_bill_amount
									from 
									         gst_header_sales as ghs,gst_financial_years as gfy 
									where 
									         firm = %s and ghs.financial_year = gfy.id and ghs.financial_year = %s order by ghs.create_date 
			
							"""
                cr.execute(sales_query,(firm,financial_year))
                detail_result= cr.fetchall()  

            list1=[]
            list2=[]
            list3=[]
            list4=[]
            list5=[]
            list6=[]
            list7=[]
            list8=[]			
            list9 = []
            serial_no=1
            for res in detail_result :
		        list1.append(res[0])
		        list2.append(res[1])
		        list3.append(res[2])
		        list4.append(res[3])
		        list5.append(res[4])
		        list6.append(res[5])
		        list7.append(res[6])
		        list8.append(res[7])
				
            data=[]
            report_data = self.read(cr, uid, ids, [], context=context)[0]
            workbook = xlsxwriter.Workbook(out)
            Style = ExcelStyles()
            if datas['type']=='purchase':
                if datas['firm'] == 'New KrishnaArjuna Textiles':			
                    worksheet = workbook.add_worksheet("NKT's YEARLY PURCHASE REPORT")
                else:
                    worksheet = workbook.add_worksheet("SSH's YEARLY PURCHASE REPORT")
            else:
                if datas['firm'] == 'New KrishnaArjuna Textiles':						
                    worksheet = workbook.add_worksheet("NKT's YEARLY SALES REPORT")
                else:
                    worksheet = workbook.add_worksheet("SSH's YEARLY SALES REPORT")
			
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
            worksheet.set_column(0, 0, 5)
            worksheet.set_row(1,20)
            worksheet.set_column(1, 1, 12)
            worksheet.set_column(2, 2, 18)
            worksheet.set_column(3, 3, 20)
            worksheet.set_column(4, 4, 20) 
            worksheet.set_column(5, 5, 15)
            worksheet.set_column(6, 6, 15) 				
            worksheet.set_column(7, 7, 15)
            worksheet.set_column(8, 8, 15)
			
            data_headings=['S.No','MONTH','FINANCIAL YEAR',"BILL AMOUNT","TOTAL IGST",'TOTAL CGST','TOTAL SGST','TOTAL TAX','TOTAL BILL']
				   
            data = [ list1,list2,list3,list4,list5,list6,list7,list8]
					
            list1_len=len(list1)
            list2_len=len(list2)
            list3_len=len(list3)
            list4_len=len(list4)
            list5_len=len(list5)
            list6_len=len(list6)
            list7_len=len(list7)
            list8_len=len(list8)
            sno1=1
            list_sno1=[]
            for sno in list1:
             	list_sno1.append(sno1)
                sno1=sno1+1
            if datas['firm']=='New KrishnaArjuna Textiles':	
                worksheet.merge_range('A1:I1',"  KOTA LAKSHMI RADHA SUVARCHALA , GST NO: 37CPQPK4284H1Z3",merge_format)
                worksheet.merge_range('A2:I2', "PROP : " + datas['firm'] + " , MGC MARKET, SHOP NO: 302,CHIRALA"  ,merge_format2)
            else:
                worksheet.merge_range('A1:I1',"  KOTA PADMAJA RANI ,GST NO: 37BZAPK0778D1ZH ",merge_format)
                worksheet.merge_range('A2:I2', "PROP : " + datas['firm'] + " , MGC MARKET, SHOP NO: 304,CHIRALA",merge_format2)
				
            if datas['type']=='purchase':			
                worksheet.merge_range('A3:I3'," DETAILS OF PURCHASE DURING THE FINANCIAL YEAR "+ datas['financial_year'][1],merge_format)
            if datas['type']=='sales':			
                worksheet.merge_range('A3:I3'," DETAILS OF SALES DURING THE FINANCIAL YEAR "+ datas['financial_year'][1],merge_format)

            worksheet.write('A4', data_headings[0],col_color)
            worksheet.write('B4', data_headings[1],col_color)
            worksheet.write('C4', data_headings[2],col_color)
            worksheet.write('D4', data_headings[3],col_color)
            worksheet.write('E4', data_headings[4],col_color)
            worksheet.write('F4', data_headings[5],col_color)
            worksheet.write('G4', data_headings[6],col_color)
            worksheet.write('H4', data_headings[7],col_color)
            worksheet.write('I4', data_headings[8],col_color)	
			
            worksheet.write_column('A5',list_sno1,col_color3)
            worksheet.write_column('B5', data[0],col_color2)
            worksheet.write_column('C5', data[1],col_color2)
            worksheet.write_column('D5', data[2],col_color3)
            worksheet.write_column('E5', data[3],col_color3)
            worksheet.write_column('F5', data[4],col_color3)
            worksheet.write_column('G5', data[5],col_color3)
            worksheet.write_column('H5', data[6],col_color3)
            worksheet.write_column('I5', data[7],col_color3)				
            #worksheet.write_column('J5', data[8],col_color3)
			
            n=5;
            o=5;  
            for e in data[5]:
                f=len(data[5])
                worksheet.write_formula(('D%s')%(f+o),('{=sum(d5:d%s)}')%(n),col_color_bal1)
                n=n+1
			
            n=5;
            o=5;  
            for e in data[5]:
                f=len(data[5])
                worksheet.write_formula(('E%s')%(f+o),('{=sum(e5:e%s)}')%(n),col_color_bal1)
                n=n+1
			
            n=5;
            o=5;  
            for e in data[5]:
                f=len(data[5])
                worksheet.write_formula(('F%s')%(f+o),('{=sum(f5:f%s)}')%(n),col_color_bal1)
                n=n+1
			
            n=5;
            o=5;  
            for e in data[6]:
                f=len(data[6])
                worksheet.write_formula(('G%s')%(f+o),('{=sum(g5:g%s)}')%(n),col_color_bal1)
                n=n+1
			
            n=5;
            o=5;  
            for e in data[5]:
                f=len(data[5])
                worksheet.write_formula(('H%s')%(f+o),('{=sum(h5:h%s)}')%(n),col_color_bal1)
                n=n+1
			
            n=5;
            o=5;  
            for e in data[5]:
                f=len(data[5])
                worksheet.write_formula(('I%s')%(f+o),('{=sum(i5:i%s)}')%(n),col_color_bal1)
                n=n+1

            workbook.close()
            output_data =out.getvalue()
            advice = ('Save this document to a .xlsx file.')
            self.write(cr, uid, ids, {'report_data':output_data}, context={})
            return { 'type': 'ir.actions.act_url', 'url': '/gst/export_gst_purchase_sales_report?id='+ str(ids[0]) + '&db='+ str(cr.dbname) + '&uid=' + str(uid) + '&type=' + str(datas['type']), 'nodestroy': True, 'target': 'new'}                    				
