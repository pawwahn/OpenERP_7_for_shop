import openerp
from openerp.addons.web.controllers.main import manifest_list, module_boot, html_template
import openerp.addons.web.http as http
import logging
from openerp.addons.web.controllers.main import content_disposition
from openerp import pooler
import base64
import cStringIO
import xlsxwriter
import base64
from openerp.osv import osv, fields
from dateutil.parser import parse
from datetime import date, timedelta
from datetime import time

'''
 Author : Pavan Kota
 created on : 03May17 

'''


class rf_rates_upload(osv.osv_memory):
    _name = 'rf.rates.upload'
    _description = 'This is for uploading rates using excel format'

    _columns = {
        'file_name': fields.char('File name', required=False, size=255),
        'data': fields.binary('File', readonly=True),
        'name': fields.char('Filename', 50, readonly=True),
        'file': fields.binary('Upload File'),
    }

    ''' Function for download the excel template '''

    def export_rf_template(self, cr, uid, ids, context=None):
        logging.info("***********************>>>::::::::::::::::::::::::::")
        out = cStringIO.StringIO()
        workbook = xlsxwriter.Workbook(out)
        worksheet = workbook.add_worksheet('Product Rates Template')
        ''' Add a format for the header cells.'''
        header_format = workbook.add_format({
            'border': 1,
            'bg_color': '#FFFFCC',
            'bold': True,
            'text_wrap': True,
            'valign': 'vcenter',
            'indent': 1,
        })

        title_format = workbook.add_format({
            'border': 1,
            'bg_color': '#800000',
            'bold': True,
            'text_wrap': True,
            'valign': 'vcenter',
            'indent': 30,
            'font_size': 13,
            'font_color': '#FFFFCC'
        })

        ''' Set up layout for worksheet.'''
        worksheet.set_row(0, 30)
        worksheet.merge_range(0, 0, 0, 5, 'Product Rate Template', title_format)
        #     worksheet.set_column('A:A', 9)
        worksheet.set_column('A:A', 18)
        worksheet.set_column('B:B', 20)
        worksheet.set_column('C:C', 20)
        worksheet.set_column('D:D', 26)
        worksheet.set_column('E:E', 26)
        #         style = xlwt.easyxf(num_format_str='DD/MM/YYYY')
        #         worksheet.col(3).set_style(style)
        # worksheet.set_column('J:J', 35)

        ''' Headings...'''
        #  worksheet.write('A2', 'S.No', header_format)
        worksheet.write('A2', 'Company Name', header_format)
        worksheet.write('B2', 'Category', header_format)
        worksheet.write('C2', 'Size', header_format)
        worksheet.write('D2', 'Purchase Rate', header_format)
        worksheet.write('E2', 'Sale Rate', header_format)

        workbook.close()
        file_data = out.getvalue()
        file_data = base64.b64encode(file_data)
        logging.info("function came till here ------------------------>>>>>>>>>>>???????>?>")
        logging.info(file_data)
        logging.info(type(ids[0]))
        logging.info(cr.dbname)
        logging.info(type(uid))
        self.write(cr, uid, ids[0], {'data': file_data, 'name': 'rate_finder_template'}, context=None)
        return {'type': 'ir.actions.act_url','url': '/rfpk/export_xls?id=' + str(ids[0]) + '&db=' + str(cr.dbname) + '&uid=' + str(uid) + '&model=rf.rates.upload', 'nodestroy': True, 'target': 'new'}

    ''' Function to download error file'''

    def download_errors(self, cr, uid, ids, context=None):
        if not self.content:
            raise osv.except_osv(('Warning!'), ('There is no error file to show.'))
        requirement_upload_obj = self.browse(cr, uid, ids, context=context)[0]
        self.write(cr, uid, ids, {'data': self.content, 'name': 'rate_finder_upload_data_errors'}, context=None)
        return {'type': 'ir.actions.act_url',
                'url': '/rf_pk/download_errors?id=' + str(ids[0]) + '&db=' + str(cr.dbname) + '&uid=' + str(
                    uid) + '&model=rf.rates.upload', 'nodestroy': True, 'target': 'new'}

    '''Function to read the selected excel file and store it in the database'''
"""
    def read_excel(self, cr, uid, ids, context=None):
        self.content = ''
        upload_vehicle_request_obj = self.browse(cr, uid, ids, context=context)[0]
        input_data = self.read(cr, uid, ids, [], context=context)[0]
        if not upload_vehicle_request_obj.file_name:
            self.content = None
            raise osv.except_osv(_('Warning!'),
                                 _('Please select the file to upload'))
        fileName, fileExtension = os.path.splitext(upload_vehicle_request_obj.file_name)
        file_name = upload_vehicle_request_obj.file_name
        if str(fileExtension) not in ('.xls', '.xlsx'):
            raise osv.except_osv(_('Warning!'),
                                 _('Please upload valid file format.'))
        workbook = xlrd.open_workbook(file_contents=base64.b64decode(upload_vehicle_request_obj.file))
        vehicle_request_worksheet = workbook.sheet_by_index(0)
        if vehicle_request_worksheet.nrows == 2:
            raise osv.except_osv(_('Warning!'),
                                 _('Please fill the data and upload the file.'))
        num_rows = vehicle_request_worksheet.nrows - 2
        num_cells = vehicle_request_worksheet.ncols - 1
        error = ''

        if ((num_cells > 4) or (num_cells < 4)):
            raise osv.except_osv(_('Warning!'), _('Invalid template.. Please download new template '))

        requests_list = []
        status_obj = {}
        count = 0
        # import datetime
        now = datetime.now()

        company_obj = self.pool.get('company.setup')

        new_project = []
        employee_id = []
        employee = []
        request_curr_row = 1
        while request_curr_row <= num_rows:
            request_curr_row += 1
            row = vehicle_request_worksheet.row(request_curr_row)
            requestor_curr_cell = -1
            request_rows = {
                'created_by': uid,
                'created_date': now,
                'requested_date': now,
            }
            while requestor_curr_cell < num_cells:
                requestor_curr_cell += 1
                cell_type = vehicle_request_worksheet.cell_type(request_curr_row, requestor_curr_cell)
                cell_value = vehicle_request_worksheet.cell_value(request_curr_row, requestor_curr_cell)

                if requestor_curr_cell == 0:
                    if cell_value:
                        company_name = cell_value
                        company = company_obj.search(cr, uid, [('company_name_id', '=', cell_value)], context=context)
                        company_name_id = int(cell_value)
                        request_rows['company_name_id'] = cell_value
                    else:
                        error = error + "Company Name is mandatory ---->" + str(request_curr_row) + "\n"


                if requestor_curr_cell == 2:
                    if cell_value:
                        category = company_obj.search(cr, uid, [('company_name_id', '=', company_name),('category_name_id', '=', cell_value)], context=context)
                        company_category_id = int(cell_value)
                        request_rows['category_name_id'] = cell_value
                    else:
                        error = error + "Category Name is mandatory ---->" + str(request_curr_row) + "\n"

                if requestor_curr_cell == 3:
                    if cell_value:
                        request_rows['category_size'] = cell_value
                    else:
                        error = error + "Destination is mandatory ---->" + str(request_curr_row) + "\n"

                if requestor_curr_cell == 4:
                    if cell_value:
                        request_rows['remarks'] = cell_value
                        #                     else:
                        #                             error=error+"Reason is mandatory ---->"+str(request_curr_row)+"\n"
            requests_list.append(request_rows)

        if error:
            self.content = error
            raise osv.except_osv(('Error!'), ('Please Click on the download error file button to view all the errors.'))

        for request in requests_list:
            request['needed_on'] = datetime.strptime(request['needed_on'], '%Y-%m-%d').strftime('%d/%m/%Y')
            vehicle_request_id = vehicle_request_obj.submit_requests(cr, uid, False, request, False)
        return self.pool.get('warning_box').info(cr, uid, title='Success',
                                                 message='Products Price uploaded successfully.')

    '''This method will change the format of excel date'''

    def get_xlrd_date(self, cr, uid, value, context=None):
        date_value = xlrd.xldate_as_tuple(value, 0)
        return datetime(*date_value).strftime("%d/%m/%Y")

    '''This method will check whether the duplicate value exists in the List'''

    # def check_duplicate_value(self, cr, uid, vals, request_list):
    #     i = 0
    #     if request_list and vals:
    #         for request in request_list:
    #             if i <= 1:
    #                 if request['needed_on'] == vals['needed_on'] and request['reporting_time'] == vals[
    #                     'reporting_time'] and request['requestor_id'] == vals['requestor_id'] and request[
    #                     'from_place'] == vals['from_place'] and request['to_place'] == vals['to_place']:
    #                     i += 1
    #             else:
    #                 break
    #     if i > 1:
    #         return True
    #     else:
    #         return False


"""
