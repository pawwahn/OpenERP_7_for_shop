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
# from utility import MyHTMLParser
from openerp import SUPERUSER_ID
import gst
from datetime import time

MONTH = [('JAN', 'JAN'), ('FEB', 'FEB'), ('MAR', 'MAR'), ('APR', 'APR'), ('MAY', 'MAY'), ('JUN', 'JUN'), ('JUL', 'JUL'),
         ('AUG', 'AUG'), ('SEPT', 'SEPT'), ('OCT', 'OCT'),
         ('NOV', 'NOV'), ('DEC', 'DEC')
         ]

GST_TYPE = [('IGST', 'IGST'), ('CGST', 'CGST')]

STATUS = [('active', 'Active'),
          ('inactive', 'Inactive')
          ]

FIRM = [('New KrishnaArjuna Textiles', 'New KrishnaArjuna Textiles'),
        ('Subhamastu Saree House', 'Subhamastu Saree House')
        ]


class gst_sales_data_upload(osv.osv_memory):
    _name = 'gst.sales.data.upload'
    _description = 'This is for uploading GST purchase data by using excel format'

    _columns = {
        'file_name': fields.char('File name', required=False, size=255),
        'data': fields.binary('File', readonly=True),
        'name': fields.char('Filename', 50, readonly=True),
        'file': fields.binary('Upload File'),
        'month': fields.selection(MONTH, 'Month', required=True, select=True),
        'firm': fields.selection(FIRM, 'Firm', required=True, select=True),
        'financial_year': fields.many2one('gst.financial.years', 'Financial Year', required=True),
    }

    def read_excel(self, cr, uid, ids, context=None):
        self.content = ''
        logging.info("**************")
        logging.info(ids)
        upload_sales_data_obj = self.browse(cr, uid, ids, context=context)[0]
        logging.info(upload_sales_data_obj)
        input_data = self.read(cr, uid, ids, [], context=context)[0]
        logging.info(input_data)

        if not upload_sales_data_obj.file_name:
            self.content = None
            raise osv.except_osv(_('Warning!'),
                                 _('Please select the file to upload'))
        fileName, fileExtension = os.path.splitext(upload_sales_data_obj.file_name)
        logging.info("*********>>>>>>>")
        logging.info(fileName)
        logging.info(fileExtension)
        file_name = upload_sales_data_obj.file_name
        logging.info(file_name)
        if str(fileExtension) not in ('.xls', '.xlsx'):
            raise osv.except_osv(_('Warning!'),
                                 _('Please upload valid file format.'))

        workbook = xlrd.open_workbook(file_contents=base64.b64decode(upload_sales_data_obj.file))
        sales_gst_worksheet = workbook.sheet_by_index(0)
        if sales_gst_worksheet.nrows == 4:
            raise osv.except_osv(_('Warning!'),
                                 _('Please fill the data and upload the file.'))
        num_rows = sales_gst_worksheet.nrows - 3
        num_cells = sales_gst_worksheet.ncols - 1
        logging.info("===============")
        logging.info(num_rows)
        logging.info(num_cells)
        # sheet = workbook[workbook.get_sheet_names()[0]]
        error = ''

        if ((num_cells > 13) or (num_cells < 13)):
            raise osv.except_osv(_('Warning!'), _('Invalid template.. Please download new template '))

        sales_data = []
        individual_data = {}
        header_id = self.pool.get('gst.header.sales').search(cr, uid, [('firm', '=', str(input_data['firm'])),
                                                                          ('month', '=', str(input_data['month'])),
                                                                          ('financial_year', '=',
                                                                           input_data['financial_year'][0])],
                                                                context=context)
        logging.info("===============>>>>")
        logging.info(header_id)
        if header_id:
            individual_data['gst_header_id'] = header_id[0]
            current_row = 3
            while current_row <= num_rows:
                current_row += 1
                cells = sales_gst_worksheet.row_slice(rowx=current_row, start_colx=1, end_colx=14)
                sales_data.append(cells)
            logging.info("===============>>>>")
            logging.info(sales_data)
            for data in sales_data:
                logging.info("<<<<<<<<<<=======>>>>")
                logging.info(data)
                if data[0]:
                    individual_data['bill_date'] = str(data[0].value)
                if data[1]:
                    individual_data['bill_num'] = int(data[1].value)
                if data[2]:
                    individual_data['sold_to'] = str(data[2].value)
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
                    individual_data['rcm'] = data[10].value
                if data[11]:
                    individual_data['place'] = str(data[11].value)
                if data[12]:
                    state_obj = self.pool.get('gst.state.code.setup').search(cr, uid,
                                                                             [('state_name', 'ilike', data[12].value)],
                                                                             context=context)
                    # state_id = self.pool.get('gst.state.code.setup').browse(cr, uid, state_obj, context=context)
                    logging.info("****>>>>>>>>>>>>>>>>>>>>>>")
                    individual_data['country_state'] = state_obj[0]

                logging.info("****>>>>>>>>>>>>>>>>>>>>>>")
                logging.info(individual_data)
                self.pool.get('gst.detail.sales').create(cr, uid, individual_data, context=context)
            # detail_objts = self.pool.get('gst.detail.sales').browse(cr, uid, header_id[0], context=context)
            # logging.info("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
            # logging.info(detail_objts)
            # total_bill_amount = 0.0
            # bill_amount = 0.0
            # total_cgst = 0.0
            # total_sgst = 0.0
            # total_igst = 0.0
            # total_tax = 0.0
            # for record in detail_objts:
            #     # logging.info(record)
            #     total_bill_amount += record.total_with_gst
            #     bill_amount += record.bill_amount
            #     total_cgst += record.cgst
            #     total_sgst += record.sgst
            #     total_igst += record.igst
            #     total_tax += record.total_tax
            # context['total_value_update'] = True
            # self.pool.get('gst.header.sales').write(cr, uid, header_id[0],
            #                                         {'total_bill_amount': total_bill_amount, 'bill_amount': bill_amount,
            #                                          'total_cgst': total_cgst, 'total_sgst': total_sgst,
            #                                          'total_tax': total_tax, 'total_igst': total_igst}, context=context)
        else:
            raise osv.except_osv(_('Uploading to a wrong month'), _('-- Please create the month record--'))






