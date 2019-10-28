import logging
from openerp.osv import osv, fields
from datetime import datetime
from string import lower
from datetime import date
from openerp import pooler, tools
from openerp.osv import fields, osv
from openerp.tools.translate import _
import cStringIO
import xlsxwriter
import xlrd
import os
import base64
from dateutil.parser import parse
from datetime import date, timedelta
# from xlwt import easyxf
# import xlwt
#from utility import MyHTMLParser
from openerp import SUPERUSER_ID
import gst
from datetime import time
MONTH=[('JAN','JAN'),('FEB','FEB'),('MAR','MAR'),('APR','APR'),('MAY','MAY'),('JUN','JUN'),('JUL','JUL'),('AUG','AUG'),('SEPT','SEPT'),('OCT','OCT'),
        ('NOV','NOV'),('DEC','DEC')
	   ]

GST_TYPE = [('IGST','IGST'),('CGST','CGST')]

STATUS = [('active', 'Active'),
          ('inactive', 'Inactive')
          ]

FIRM = [('New KrishnaArjuna Textiles', 'New KrishnaArjuna Textiles'),
        ('Subhamastu Saree House', 'Subhamastu Saree House')
        ]

class gst_purchase_data_upload (osv.osv_memory):
    _name = 'gst.purchase.data.upload'
    _description = 'This is for uploading GST purchase data by using excel format'

    _columns = {
                'file_name': fields.char('File name', required=False,size=255),
                'data': fields.binary('File', readonly=True),
                'name': fields.char('Filename', 50, readonly=True),
                'file': fields.binary('Upload File'),
                'month':fields.selection(MONTH,'Month',required=True,select=True),
                'firm': fields.selection(FIRM, 'Firm', required=True, select=True),
                'financial_year': fields.many2one('gst.financial.years', 'Financial Year', required=True),
                }

    def read_excel(self, cr, uid, ids, context=None):
        self.content = ''
        logging.info("**************")
        logging.info(ids)
        upload_purchase_data_obj = self.browse(cr, uid, ids, context=context)[0]
        logging.info(upload_purchase_data_obj)
        input_data = self.read(cr, uid, ids, [], context=context)[0]
        logging.info(input_data)

        if not upload_purchase_data_obj.file_name:
            self.content = None
            raise osv.except_osv(_('Warning!'),
                                 _('Please select the file to upload'))
        fileName, fileExtension = os.path.splitext(upload_purchase_data_obj.file_name)
        logging.info("*********>>>>>>>")
        logging.info(fileName)
        logging.info(fileExtension)
        file_name = upload_purchase_data_obj.file_name
        logging.info(file_name)
        if str(fileExtension) not in ('.xls', '.xlsx'):
            raise osv.except_osv(_('Warning!'),
                                 _('Please upload valid file format.'))

        workbook = xlrd.open_workbook(file_contents=base64.b64decode(upload_purchase_data_obj.file))
        purchase_gst_worksheet = workbook.sheet_by_index(0)
        if purchase_gst_worksheet.nrows == 4:
            raise osv.except_osv(_('Warning!'),
                                 _('Please fill the data and upload the file.'))
        num_rows = purchase_gst_worksheet.nrows -3
        num_cells = purchase_gst_worksheet.ncols - 1
        logging.info("===============")
        logging.info(num_rows)
        logging.info(num_cells)
        #sheet = workbook[workbook.get_sheet_names()[0]]
        error = ''

        if ((num_cells > 13) or (num_cells < 13)):
            raise osv.except_osv(_('Warning!'), _('Invalid template.. Please download new template '))

        purchase_data = []
        individual_data = {}
        header_id = self.pool.get('gst.header.purchase').search(cr, uid, [('firm', '=', str(input_data['firm'])),
                                                                          ('month', '=', str(input_data['month'])),
                                                                          ('financial_year', '=',input_data['financial_year'][0])],
                                                                context=context)
        if header_id:
            individual_data['gst_header_id'] = header_id[0]
            current_row = 3
            while current_row <= num_rows:
                current_row +=1
                cells = purchase_gst_worksheet.row_slice(rowx=current_row,start_colx=1,end_colx=14)
                purchase_data.append(cells)
            logging.info("===============>>>>")
            logging.info(purchase_data)
            for data in purchase_data:
                logging.info("<<<<<<<<<<=======>>>>")
                logging.info(data)
                if data[3]:
                    purchased_from_id = self.pool.get('gst.purchased.from.setup').search(cr, uid, [('gst_num', '=', data[3].value)],context=context)
                    if purchased_from_id:
                        logging.info("===== This is already existing: {} --->".format(purchased_from_id))
                        logging.info(purchased_from_id)
                        individual_data['purchase_from_many_to_one'] = purchased_from_id[0]
                    else:
                        logging.info("=====***********==========>>>>")
                        vals={'gst_num':data[3].value,'shop_name':data[2].value,'status':'active'}
                        purchased_from_new_id=self.pool.get('gst.purchased.from.setup').create(cr,uid,vals,context=context)
                        logging.info(purchased_from_new_id)
                        individual_data['purchase_from_many_to_one'] = int(purchased_from_new_id)
                if data[0]:
                    individual_data['bill_date'] = str(data[0].value)
                    logging.info("check for date format ==========")
                    logging.info(individual_data['bill_date'])
                if data[1]:
                    individual_data['bill_num'] = str(data[1].value)
                if data[3]:
                    individual_data['gst_num'] = str(data[3].value)
                if data[4]:
                    individual_data['bill_amount'] = data[4].value
                if data[5]:
                    individual_data['cgst'] = data[5].value
                if data[6]:
                    individual_data['sgst'] = data[6].value
                if data[7]:
                    individual_data['igst'] = data[7].value
                if data[8]:
                    individual_data['total_tax'] = data[8].value
                if data[9]:
                    individual_data['total_with_gst'] = data[9].value
                if data[10]:
                    individual_data['hsn'] = data[10].value
                if data[11]:
                    individual_data['place'] = str(data[11].value)
                if data[12]:
                    state_obj = self.pool.get('gst.state.code.setup').search(cr, uid, [('state_name', 'ilike' , str(data[12].value))],context=context)
                    #state_id = self.pool.get('gst.state.code.setup').browse(cr, uid, state_obj, context=context)
                    logging.info("****>>>>>>>>>country state>>>>>>>>>>>>>")
                    logging.info(state_obj)
                    logging.info(state_obj[0])
                    individual_data['country_state'] = state_obj[0]

                logging.info("****>>>>>>>>>individual_data>>>>>>>>>>>>>")
                logging.info(individual_data)
                self.pool.get('gst.detail.purchase').create(cr, uid, individual_data, context=context)
        else:
            raise osv.except_osv(_('Uploading to a wrong month'), _('-- Please create the month record--'))



            


