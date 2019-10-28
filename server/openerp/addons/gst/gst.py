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
from excel_styles import ExcelStyles
from __builtin__ import str




STATUS=[('active','Active'),
         ('inactive','Inactive')
	   ]
	   
FIRM=[('New KrishnaArjuna Textiles','New KrishnaArjuna Textiles'),
          ('Subhamastu Saree House','Subhamastu Saree House')
	    ]

TYPE=[('purchase','Purchase'),
          ('sales','Sales')
	    ]
	   
MONTH=[('JAN','JAN'),('FEB','FEB'),('MAR','MAR'),('APR','APR'),('MAY','MAY'),('JUN','JUN'),('JUL','JUL'),('AUG','AUG'),('SEPT','SEPT'),('OCT','OCT'),
        ('NOV','NOV'),('DEC','DEC')
	   ] 

GST_TYPE = [('IGST','IGST'),('CGST','CGST')]

class gst_header_sales(osv.Model):
    """ 
    This will contain the details of the customer and the registration of the customer
    """
    _name = 'gst.header.sales'
    _rec_name='sequence'
    _description = 'GST'
	
	
    _columns = {
        'sequence':fields.char('Sequence',size=50),
        'month':fields.selection(MONTH,'Month',required=True,select=True),
        'type':fields.selection(TYPE,'Type',required=True,select=True),
        'firm':fields.selection(FIRM,'Firm',required=True,select=True),
        'month_number' : fields.integer('Month Number'),
        'status':fields.selection(STATUS,'Status',select=True),
        'gst_header_details_line':fields.one2many('gst.detail.sales','gst_header_id'),
        'state': fields.selection([('draft', 'Draft'), \
									('created','Created'), \
                                    ('submit for gst', 'Submitted for GST'), \
                                    ('cancelled', 'Cancelled')], \
                                'Status', readonly=True, select=True),
        'financial_year': fields.many2one('gst.financial.years','Financial Year',required=True),
        'bill_amount': fields.float('Bill Amount'),
        'total_bill_amount': fields.float('Total Sale'),
        'total_cgst' : fields.float('Total CGST'),
        'total_sgst' : fields.float('Total SGST'),
        'total_igst' : fields.float('Total IGST'),
        'total_tax' : fields.float('Total Tax'),
        'report_data': fields.binary('File', readonly=True),
		'book_nums': fields.char('Book Numbers'),
        
    }
	
    def create(self, cr, uid,vals, context=None):
        logging.info(vals)
        logging.info("********************* create *********---------")
        vals['state'] = 'created'
        new_id = super(gst_header_sales,self).create(cr,uid,vals,context=context) 
        if 'total_value_update' not in context:
            detail_ids=self.pool.get('gst.detail.sales').search(cr,uid,[('gst_header_id','in',[new_id])],context=context)
            detail_objts=self.pool.get('gst.detail.sales').browse(cr,uid,detail_ids,context=context)
            total_bill_amount=0.0
            bill_amount=0.0
            total_cgst = 0.0
            total_sgst = 0.0
            total_igst = 0.0
            total_tax = 0.0
            for record in detail_objts:
                #logging.info(record)
                if record.bill_amount > 0:
                    total_bill_amount+=record.total_with_gst
                    bill_amount+=record.bill_amount
                    total_cgst+=record.cgst
                    total_sgst+=record.sgst
                    total_igst+=record.igst
                    total_tax+=record.total_tax
                else:
                    raise osv.except_osv(_('Invalid Bill Amount'), _("-- Some of the bill's amount is 0.00 --"))
            context['total_value_update']=True
            self.pool.get('gst.header.sales').write(cr,uid,[new_id],{'total_bill_amount':total_bill_amount,'bill_amount':bill_amount,'total_cgst':total_cgst,'total_sgst':total_sgst,'total_tax':total_tax,'total_igst':total_igst},context=context)
        
        return new_id
   
    def revoke(self,cr,uid,gst_id,vals,context=None):
        logging.info("inside revoke ********************* ")
        logging.info(vals)
        logging.info(gst_id)
        vals['state'] = 'draft'
        vals['status'] = 'active'
        return super(gst_header_sales,self).write(cr,uid,int(gst_id[0]),vals,context=context)
		#self.pool.get('gst.header.sales').write(cr,uid,gst_id,vals,context=context)		
		
    def cancel(self,cr,uid,gst_id,vals,context=None):
        logging.info("inside revoke ********************* ")
        logging.info(vals)
        logging.info(gst_id)
        vals['state'] = 'cancelled'
        vals['status'] = 'inactive'
        return super(gst_header_sales,self).write(cr,uid,int(gst_id[0]),vals,context=context)
		
    def gst_submit(self,cr,uid,gst_id,vals,context=None):
        logging.info("inside submit ********************* ")
        logging.info(vals)
        logging.info(gst_id)
        vals['state'] = 'submit for gst'
        return super(gst_header_sales,self).write(cr,uid,int(gst_id[0]),vals,context=context)

    def write(self,cr,uid,ids,vals,context=None):
        vals['state'] = 'created'
        new_id = super(gst_header_sales,self).write(cr,uid,ids,vals,context=context)
        if 'total_value_update' not in context:
            detail_ids=self.pool.get('gst.detail.sales').search(cr,uid,[('gst_header_id','in',ids)],context=context)
            detail_objts=self.pool.get('gst.detail.sales').browse(cr,uid,detail_ids,context=context)
            total_bill_amount=0.0
            bill_amount=0.0
            total_cgst = 0.0
            total_sgst = 0.0
            total_igst = 0.0
            total_tax = 0.0
            for record in detail_objts:
                if record.bill_amount > 0:
                    total_bill_amount+=record.total_with_gst
                    bill_amount+=record.bill_amount
                    total_cgst+=record.cgst
                    total_sgst+=record.sgst
                    total_igst+=record.igst
                    total_tax+=record.total_tax
                else:
                    raise osv.except_osv(_('Invalid Bill Amount'), _("-- Some of the bill's amount is 0.00 --"))
            context['total_value_update']=True
            self.pool.get('gst.header.sales').write(cr,uid,ids,{'total_bill_amount':total_bill_amount,'bill_amount':bill_amount,'total_cgst':total_cgst,'total_sgst':total_sgst,'total_tax':total_tax,'total_igst':total_igst},context=context)
        return new_id   		
            
    _defaults = {  
                    'status': 'active',
					'type' : 'sales',
					'state' : 'draft',
                }
				
    def print_sales(self,cr,uid,ids,context=None):
        out=cStringIO.StringIO()
        detail_query = """  select 
		                           to_char(bill_date,'dd/mm/yyyy'),bill_num::integer,sold_to,gst_num,bill_amount,cgst,sgst,igst,total_tax,total_with_gst,rcm,place,
                                   gst_state_code_setup.state_name
                            from 
							       gst_detail_sales,gst_state_code_setup 
						    where 
							       gst_detail_sales.country_state = gst_state_code_setup.id and gst_detail_sales.gst_header_id= %s order by bill_num
				"""
        cr.execute(detail_query,(ids[0],))
        detail_result= cr.fetchall()  
        logging.info("************>>>>>>>>>>>>>>>>>>>");
        #logging.info(detail_result)	
		
        header_query = """ 
            select 
	              firm,month,bill_amount,
				  total_sgst,total_cgst,
				  total_tax,total_bill_amount,
				  total_igst,fin_year 
            from 
			      gst_header_sales as ghs ,gst_financial_years as gfy 
		    where 
			      ghs.financial_year = gfy.id 
		    and   ghs.id = %s
		
		"""
        cr.execute(header_query,(ids[0],))
        header_result= cr.fetchone()  
        logging.info("************>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<")
        list1=[]
        list2=[]
        list3=[]
        list4=[]
        list5=[]
        list6=[]
        list7=[]
        list8=[]
        list9=[]
        list10=[]
        list11=[]
        list12=[]
        list13=[]
		
        serial_no=1
        for res in detail_result :
            logging.info(res)
            list1.append(res[0])
            list2.append(res[1])
            list3.append(res[2])
            list4.append(res[3])
            list5.append(res[4])
            list6.append(res[5])
            list7.append(res[6])
            list8.append(res[7])
            list9.append(res[8])
            list10.append(res[9])
            list11.append(res[10])
            list12.append(res[11])
            list13.append(res[12])
        data=[]
        report_data = self.read(cr, uid, ids, [], context=context)[0]
        workbook = xlsxwriter.Workbook(out)
        Style = ExcelStyles()
        worksheet = workbook.add_worksheet('GST SALES')
			
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
        worksheet.set_row(1,14)
        worksheet.set_column(1, 1, 12)
        worksheet.set_column(2, 2, 12)
        worksheet.set_column(3, 3, 28)
        worksheet.set_column(4, 4, 21) 
        worksheet.set_column(5, 5, 12)
        worksheet.set_column(6, 6, 10) 				
        worksheet.set_column(7, 7, 10)
        worksheet.set_column(8, 8, 10)
        worksheet.set_column(9, 9, 12)
        worksheet.set_column(10, 10, 12) 				
        worksheet.set_column(11, 11, 10)
        worksheet.set_column(12, 12, 15)
        worksheet.set_column(13, 13, 23) 				 									
                 
               # Write some data to add to plot on the chart.
        data_headings=['S.No','BILL DATE','BILL NO',"CUSTOMER'S NAME","CUSTOMER'S GST/AAD/PAN",'SALE VALUE','CGST','SGST','IGST','TOTAL TAX','TOTAL BILL','RCM','PLACE','STATE']
               
        data = [ list1,list2,list3,list4,list5,list6,list7,list8,list9,list10,list11,list12,list13]
				
        list1_len=len(list1)
        list2_len=len(list2)
        list3_len=len(list3)
        list4_len=len(list4)
        list5_len=len(list5)
        list6_len=len(list6)
        list7_len=len(list7)
        list8_len=len(list8)
        list9_len=len(list9)
        list10_len=len(list10)
        list11_len=len(list11)
        list12_len=len(list12)
        list13_len=len(list13)

        sno1=1
        list_sno1=[]
        for sno in list1:
            list_sno1.append(sno1)
            sno1=sno1+1

        worksheet.merge_range('A3:N3',"  DETAILS OF SALES DURING "+ header_result[1] + " ("+header_result[8] +")",merge_format)
        if header_result[0]!='New KrishnaArjuna Textiles':
            worksheet.merge_range('A1:N1',"  KOTA PADMAJA RANI ,GST NO: 37BZAPK0778D1ZH ",merge_format)
            worksheet.merge_range('A2:N2', "PROP : " + header_result[0] + " , MGC MARKET, SHOP NO: 304,CHIRALA",merge_format2)
        if header_result[0]=='New KrishnaArjuna Textiles':
            worksheet.merge_range('A1:N1',"  KOTA LAKSHMI RADHA SUVARCHALA , GST NO: 37CTQPK4284H1Z3",merge_format)
            worksheet.merge_range('A2:N2', "PROP : " + header_result[0] + " , MGC MARKET, SHOP NO: 302,CHIRALA"  ,merge_format2)
        worksheet.write('A4', data_headings[0],col_color)
        worksheet.write('B4', data_headings[1],col_color)
        worksheet.write('C4', data_headings[2],col_color)
        worksheet.write('D4', data_headings[3],col_color)
        worksheet.write('E4', data_headings[4],col_color)
        worksheet.write('F4', data_headings[5],col_color)
        worksheet.write('G4', data_headings[6],col_color)
        worksheet.write('H4', data_headings[7],col_color)
        worksheet.write('I4', data_headings[8],col_color)	
        worksheet.write('J4', data_headings[9],col_color)
        worksheet.write('K4', data_headings[10],col_color)
        worksheet.write('L4', data_headings[11],col_color)
        worksheet.write('M4', data_headings[12],col_color)
        worksheet.write('N4', data_headings[13],col_color)		

        worksheet.write_column('A5',list_sno1,col_color3)
        worksheet.write_column('B5', data[0],col_color2)
        worksheet.write_column('C5', data[1],col_color2)
        worksheet.write_column('D5', data[2],col_color2)
        worksheet.write_column('E5', data[3],col_color2)
        worksheet.write_column('F5', data[4],col_color3)
        worksheet.write_column('G5', data[5],col_color3)
        worksheet.write_column('H5', data[6],col_color3)
        worksheet.write_column('I5', data[7],col_color3)				
        worksheet.write_column('J5', data[8],col_color3)
        worksheet.write_column('K5', data[9],col_color3)
        worksheet.write_column('L5', data[10],col_color2)
        worksheet.write_column('M5', data[11],col_color2)
        worksheet.write_column('N5', data[12],col_color2)
		
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
			
        n=5;
        o=5;  
        for e in data[5]:
            f=len(data[5])
            worksheet.write_formula(('J%s')%(f+o),('{=sum(j5:j%s)}')%(n),col_color_bal1)
            n=n+1
			
        n=5;
        o=5;  
        for e in data[5]:
            f=len(data[5])
            worksheet.write_formula(('K%s')%(f+o),('{=sum(k5:k%s)}')%(n),col_color_bal1)
            n=n+1

        workbook.close()
        output_data =out.getvalue()
        logging.info("output dataaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa************************")
        logging.info(output_data)
        advice = ('Save this document to a .xlsx file.')
        self.write(cr, uid, ids, {'report_data':output_data}, context={})
        return { 'type': 'ir.actions.act_url', 'url': '/gst/export_gst_report?id='+ str(ids[0]) + '&db='+ str(cr.dbname) + '&uid=' + str(uid), 'nodestroy': True, 'target': 'new'}                    				
    			
		
class gst_detail_sales(osv.Model):
    """ 
    This will contain the details of the customer and the registration of the customer
    """
    _name = 'gst.detail.sales'
    _rec_name='gst_num'
    _description = 'Gst Details'
	
    _columns = {
        'gst_header_id':fields.many2one('gst.header.sales',ondelete="cascade"),
        'bill_date': fields.date('Bill Date',size=10,required=True),
        'sold_to':fields.char('Customer Name',size=200),
        'gst_num':fields.char('GST Number',size=15),
        'bill_num':fields.char('Bill Number',required=True,size=20),
        'bill_amount':fields.float('Bill Amount',size=20),
        'gst_type':fields.selection(GST_TYPE,'GST TYPE',select=True),
        'igst':fields.float('IGST',),
        'cgst':fields.float('CGST',),
        'sgst':fields.float('SGST',),
        'total_tax': fields.float('Total Tax',required=True),
        'total_with_gst':fields.float('Final Bill Amount',size=10),
        'country_state': fields.many2one('gst.state.code.setup','Country State',),
        'transport': fields.char('Transport',size=40),
        'place': fields.char('Place',size=40),
        'rcm': fields.char('RCM',size=80),
        'status':fields.selection(STATUS,'Current Status',select=True),
    }
    def create(self, cr, uid,vals, context=None):
        new_id = super(gst_detail_sales,self).create(cr,uid,vals,context=context) 
        return new_id
		
    def on_change_price_type(self,cr,uid,ids,bill_amount,gst_type,context=None):
        vals={}
        tot_tax = 0
        if gst_type == 'IGST':
            vals['igst'] = float((bill_amount*5)/100.0)
            vals['cgst'] = 0
            vals['sgst'] = 0
            vals['total_tax'] = float((bill_amount*5)/100.0)
            tot_tax = vals['total_tax']
            logging.info(float((bill_amount*5)/100.0))
            logging.info("****************")
            vals['total_with_gst']= bill_amount + tot_tax
        if gst_type == 'CGST':
            vals['igst'] = 0
            vals['cgst'] = float((bill_amount*2.5)/100.0)
            logging.info(vals['cgst'])
            vals['sgst'] = float((bill_amount*2.5)/100.0)
            vals['total_tax'] = float((bill_amount*5)/100.0)
            tot_tax = vals['total_tax']
            vals['total_with_gst']=bill_amount + float((bill_amount * 5)/100)
        return {'value':vals}
		
    def on_change_gst_tax_values(self,cr,uid,ids,cgst,sgst,igst,total_tax,bill_amount,context=None):
        vals={}
        vals['total_tax'] = cgst + sgst + igst
        vals['total_with_gst'] = total_tax + bill_amount
        return {'value':vals}
		
    _defaults = { 
                    #'status': 'active',
					'country_state': 2,
					'gst_type': 'CGST',
                }
				
    def on_change_gst_num(self,cr,uid,ids,gst_num,context=None):
        vals={}	
        if gst_num:
            if len(gst_num)!=15:
               raise osv.except_osv(_('Invalid GST Number'),_('-- Please Check The GST Num--'))   
            state_input = gst_num[:2]
            if not state_input.isdigit():
                raise osv.except_osv(_('Invalid GST Number'),_('-- Please Check The GST Num  --'))
            if gst_num[2].isdigit() or gst_num[3].isdigit() or gst_num[4].isdigit() or  gst_num[5].isdigit() or gst_num[6].isdigit() or gst_num[11].isdigit() or gst_num[13].isdigit():
                raise osv.except_osv(_('Invalid GST Number'),_('-- Please Check The GST Num  --'))
            if not gst_num[7].isdigit() or not gst_num[8].isdigit() or not gst_num[9].isdigit() or not gst_num[10].isdigit() or not gst_num[12].isdigit():
                raise osv.except_osv(_('Invalid GST Number'),_('-- Please Check The GST Num  --'))
            browse_state_obj = self.pool.get('gst.state.code.setup').browse(cr,uid,int(gst_num[:2]),context=context)
            state_obj = browse_state_obj.id
            if state_obj == 37 or state_obj == '':
                vals['gst_type'] = 'CGST'
            else:
                vals['gst_type'] = 'IGST'		
            state_id =self.pool.get('gst.state.code.setup').search(cr,uid,[('state_code','=',state_obj)],context=context)
            if state_id:
                vals['country_state']= state_id
                return {'value':vals}
            else:
                raise osv.except_osv(_('Invalid GST Number'),_('-- State Code Mismatch  --'))
        else:
            state_obj = 37
            state_id =self.pool.get('gst.state.code.setup').search(cr,uid,[('state_code','=',state_obj)],context=context)
            if state_id:
                vals['country_state']= state_id
                vals['gst_type'] = 'CGST'
                return {'value':vals}
            else:
                pass

        
    	
class gst_state_code_setup(osv.Model):
    """ 
    This deals with the bill type setup
    """
    _name = 'gst.state.code.setup'
    _rec_name='state_name'
    _description = 'GST State Code'
	
    _columns = {
        'state_name':fields.char('State',required=True,size=40),
        'state_code': fields.integer('State Code',required=True),
        'description':fields.text('Description',size=100),
        'status':fields.selection(STATUS,'Current Status',select=True),
    }
	
    _defaults = { 
                    'status': 'active',
				
                }
	
    _sql_constraints = [
        ('unique_name', 
         'unique(name)',
        'This Accountability type is already registered.. !')
    ]
	
	
class gst_financial_years(osv.Model):
    """ 
    This deals with the bill type setup
    """
    _name = 'gst.financial.years'
    _rec_name='fin_year'
    _description = 'GST Fin Years'
	
    _columns = {
        'fin_year':fields.char('State',required=True,size=9),
        'description':fields.text('Description',size=100),
        'current_year': fields.boolean('Current Year'),
        'status':fields.selection(STATUS,'Current Status',select=True),
    }
	
    _defaults = { 
                    'status': 'inactive',
				
                }
				
    _sql_constraints = [
        ('unique_name', 
         'unique(fin_year)',
        'This Financial Year is already registered.. !')
    ]
	

class gst_agent_setup(osv.Model):
    """ 
    This deals with the bill type setup
    """
    _name = 'gst.agent.setup'
    _rec_name='agent_name'
    _description = 'GST State Code'
	
    _columns = {
        'agent_name':fields.char('State',required=True,size=50),
        'description':fields.text('Description',required=True,size=100),
        'status':fields.selection(STATUS,'Current Status',select=True),
    }
	
    _defaults = { 
                    'status': 'active',
				
                }
	
    _sql_constraints = [
        ('unique_name', 
         'unique(agent_name)',
        'This Agent is already registered.. !')
    ]
	
class gst_purchased_from_setup(osv.Model):
    """ 
    This deals with the bill type setup
    """
    _name = 'gst.purchased.from.setup'
    _rec_name='shop_name'
    _description = 'GST State Code'
	
    _columns = {
        'shop_name':fields.char('State',required=True,size=60),
        'gst_num':fields.char('GST Number',required=True,size=15),
        'description':fields.text('Description',size=100),
        'status':fields.selection(STATUS,'Current Status',select=True),
    }
	
    def on_change_gst_num(self,cr,uid,ids,gst_num,context=None):
        vals={}	
        if gst_num:
            logging.info("*****************-----")
            logging.info(gst_num[0])
            logging.info(gst_num[14])
            logging.info("*****************----->>>")
            if len(gst_num)!=15:
               raise osv.except_osv(_('Invalid GST Number'),_('-- Please Check The GST Num--'))   
            state_input = gst_num[:2]
            if not state_input.isdigit():
                raise osv.except_osv(_('Invalid GST Number'),_('-- Please Check The GST Num  --'))
            if gst_num[2].isdigit() or gst_num[3].isdigit() or gst_num[4].isdigit() or  gst_num[5].isdigit() or gst_num[6].isdigit() or gst_num[11].isdigit() or gst_num[13].isdigit():
                raise osv.except_osv(_('Invalid GST Number'),_('-- Please Check The GST Num  --'))
            if not gst_num[7].isdigit() or not gst_num[8].isdigit() or not gst_num[9].isdigit() or not gst_num[10].isdigit() or not gst_num[12].isdigit():
                raise osv.except_osv(_('Invalid GST Number'),_('-- Please Check The GST Num  --'))
            browse_state_obj = self.pool.get('gst.state.code.setup').browse(cr,uid,int(gst_num[:2]),context=context)
            state_obj = browse_state_obj.id
            if state_obj == 37 or state_obj == '':
                vals['gst_type'] = 'CGST'
            else:
                vals['gst_type'] = 'IGST'		
            state_id =self.pool.get('gst.state.code.setup').search(cr,uid,[('state_code','=',state_obj)],context=context)
            if state_id:
                vals['country_state']= state_id
                return {'value':vals}
            else:
                raise osv.except_osv(_('Invalid GST Number'),_('-- State Code Mismatch  --'))
        else:
            state_obj = 37
            state_id =self.pool.get('gst.state.code.setup').search(cr,uid,[('state_code','=',state_obj)],context=context)
            if state_id:
                vals['country_state']= state_id
                vals['gst_type'] = 'CGST'
                return {'value':vals}
            else:
                pass
	
    _defaults = { 
                    'status': 'active',
				
                }
	
    _sql_constraints = [
        ('unique_name', 
         'unique(gst_num)',
        'This GST number is already registered.. !')
    ]