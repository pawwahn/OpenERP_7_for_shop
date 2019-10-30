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

FIRM = [('New KrishnaArjuna Textiles', 'New KrishnaArjuna Textiles'),
        ('Subhamastu Saree House', 'Subhamastu Saree House'),
        ]

TYPE = [('purchase', 'Purchase'),
        ('sales', 'Sales')
        ]


class gst_daywise_sale_report(osv.Model):
    _name = 'gst.daywise.sale.report'
    _columns = {
        'firm': fields.selection(FIRM, 'Firm', required=True, select=True),
        'from_date': fields.date('Bill Date', size=10, required=True),
        'financial_year': fields.many2one('gst.financial.years', 'Financial Year', required=True),
        'report_data': fields.binary('File', readonly=True),
        'name': fields.char('Filename', size=50, readonly=True),

    }

    def get_report(self, cr, uid, ids, context=None):
        out = cStringIO.StringIO()
        datas = self.read(cr, uid, ids, [], context=context)[0]
        firm = datas['firm']
        from_date = datas['from_date'][0]
        to_date = datas['from_date'][1]

        if firm and from_date and to_date:
            logging.info("*******************************")
            logging.info(firm)
            logging.info(from_date)
            logging.info(to_date)

            sales_query = """   select
                                    bill_date,
                                    sum(bill_amount),
                                    sum(sgst) as sgst,
                                    sum(cgst) as cgst,
                                    sum(igst) as igst,
                                    sum(gst_detail_sales.total_tax) as tot_tax,
                                    sum(gst_detail_sales.bill_amount) as tot_bill_amount
                                from 
                                    gst_detail_sales,gst_header_sales
                                where
                                    firm = %s and 
                                    gst_header_sales.id = gst_detail_sales.gst_header_id and 
                                    gst_detail_sales.bill_date>= %s::date and gst_detail_sales.bill_date<= %s::date
                                group by bill_date
                                order by bill_date"""
            cr.execute(sales_query, (firm, from_date, to_date))
            sale_records = cr.fetchall()
        else:
            raise osv.except_osv(_('Invalid Selction'), _('-- Please select both the data  --'))

        list_sale_date = []
        list_sale_bill_amount = []
        list_sale_sgst = []
        list_sale_cgst = []
        list_sale_igst = []
        list_sale_total_tax = []
        list_sale_tot_bill_amount = []

        serial_no = 1
        for res in sale_records:
            list_sale_date.append(res[0])
            list_sale_bill_amount.append(res[1])
            list_sale_sgst.append(res[2])
            list_sale_cgst.append(res[3])
            list_sale_igst.append(res[4])
            list_sale_total_tax.append(res[5])
            list_sale_tot_bill_amount.append(res[6])

        data = []
        report_data = self.read(cr, uid, ids, [], context=context)[0]
        workbook = xlsxwriter.Workbook(out)
        Style = ExcelStyles()
        if datas['firm'] == 'New KrishnaArjuna Textiles':
            worksheet = workbook.add_worksheet("NKT's DAY-WISE REPORT")
        else:
            worksheet = workbook.add_worksheet("SSH's DAY-WISE REPORT")

        bold = workbook.add_format({'bold': 1})
        col_color = workbook.add_format({'bg_color': '#99CCFF', 'border': 1, 'bold': 2, 'align': 'center'})
        col_color.set_text_wrap()
        col_color2 = workbook.add_format({'border': 1, 'bold': 2, 'align': 'left'})
        col_color3 = workbook.add_format({'border': 1, 'bold': 2, 'align': 'right'})
        col_color_bal1 = workbook.add_format({'bg_color': '#73CDFF', 'border': 1, 'bold': 2, 'align': 'right'})
        col_color_bal1.set_text_wrap()
        col_color_bal2 = workbook.add_format({'bg_color': '#26CEFF', 'border': 1, 'bold': 2, 'align': 'right'})
        col_color_bal2.set_text_wrap()
        head_color = workbook.add_format({'bg_color': '#80880'})
        set_center = workbook.add_format({'bg_color': '#99CCFF', 'border': 1, 'bold': 2, 'align': 'center'})
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
        # worksheet.set_column(0, 0, 5)
        worksheet.set_row(1, 20)
        worksheet.set_column(0, 0, 10)
        worksheet.set_column(1, 1, 12)
        worksheet.set_column(2, 2, 12)
        worksheet.set_column(3, 3, 12)
        worksheet.set_column(4, 4, 12)
        worksheet.set_column(5, 5, 12)
        worksheet.set_column(6, 6, 12)
        worksheet.set_column(7, 7, 12)
        worksheet.set_column(8, 8, 12)

        data_headings = ['DATE', 'BILL AMOUNT', 'SGST', 'CGST', 'IGST','TOTAL TAX', 'TOTAL BILL']

        data = [list_sale_date,list_sale_bill_amount,list_sale_sgst,list_sale_cgst,list_sale_igst,list_sale_total_tax,list_sale_tot_bill_amount]

        list1_len = len(list_sale_date)
        list2_len = len(list_sale_bill_amount)
        list3_len = len(list_sale_sgst)
        list4_len = len(list_sale_cgst)
        list5_len = len(list_sale_igst)
        list6_len = len(list_sale_total_tax)
        list7_len = len(list_sale_tot_bill_amount)

        if datas['firm'] == 'New KrishnaArjuna Textiles':
            worksheet.merge_range('A1:J1', "  KOTA LAKSHMI RADHA SUVARCHALA , GST NO: 37CPQPK4284H1Z3", merge_format)
            worksheet.merge_range('A2:J2', "PROP : " + datas['firm'] + " , MGC MARKET, SHOP NO: 302,CHIRALA",
                                  merge_format2)
        else:
            worksheet.merge_range('A1:J1', "  KOTA PADMAJA RANI ,GST NO: 37BZAPK0778D1ZH ", merge_format)
            worksheet.merge_range('A2:J2', "PROP : " + datas['firm'] + " , MGC MARKET, SHOP NO: 304,CHIRALA",
                                  merge_format2)

        worksheet.merge_range('A3:J3', " DETAILS OF DAILY SALES DURING DATES " + from_date +" - " + to_date,
                              merge_format)
        #worksheet.merge_range('A5:J5', " DAILY SALE DETAILS ", merge_format2)

        worksheet.write('A5', data_headings[0], col_color)
        worksheet.write('B5', data_headings[1], col_color)
        worksheet.write('C5', data_headings[2], col_color)
        worksheet.write('D5', data_headings[3], col_color)
        worksheet.write('E5', data_headings[4], col_color)
        worksheet.write('F5', data_headings[5], col_color)
        worksheet.write('G5', data_headings[6], col_color)
        worksheet.write('H5', data_headings[7], col_color)

        worksheet.write_column('A7', data[0], col_color3)
        worksheet.write_column('B7', data[1], col_color3)
        worksheet.write_column('C7', data[2], col_color3)
        worksheet.write_column('D7', data[3], col_color3)
        worksheet.write_column('E7', data[4], col_color3)
        worksheet.write_column('F7', data[5], col_color3)
        worksheet.write_column('G7', data[6], col_color3)
        worksheet.write_column('H7', data[7], col_color3)

        n = 7;
        for e in data[2]:
            f = len(data[2])
            worksheet.write_formula(('B%s') % (f + 9), ('{=sum(B7:B%s)}') % (n), col_color_bal1)
            # worksheet.write_formula(('D%s')%(f+o),('{=sum(d5:d%s)}')%(n),col_color_bal1)
            n = n + 1

        n = 7;
        for e in data[2]:
            f = len(data[2])
            worksheet.write_formula(('C%s') % (f + 9), ('{=sum(c7:c%s)}') % (n), col_color_bal1)
            n = n + 1

        n = 7;
        for e in data[2]:
            f = len(data[2])
            worksheet.write_formula(('D%s') % (f + 9), ('{=sum(d7:d%s)}') % (n), col_color_bal1)
            n = n + 1

        n = 7;
        for e in data[5]:
            f = len(data[5])
            worksheet.write_formula(('E%s') % (f + 9), ('{=sum(e7:e%s)}') % (n), col_color_bal1)
            n = n + 1

        n = 7;
        for e in data[5]:
            f = len(data[5])
            worksheet.write_formula(('F%s') % (f + 9), ('{=sum(f7:f%s)}') % (n), col_color_bal1)
            n = n + 1

        n = 7;
        for e in data[5]:
            f = len(data[5])
            worksheet.write_formula(('G%s') % (f + 9), ('{=sum(g7:g%s)}') % (n), col_color_bal1)
            n = n + 1

        n = 7;
        for e in data[5]:
            f = len(data[5])
            worksheet.write_formula(('H%s') % (f + 9), ('{=sum(h7:h%s)}') % (n), col_color_bal1)
            n = n + 1

        workbook.close()
        output_data = out.getvalue()
        advice = ('Save this document to a .xlsx file.')
        self.write(cr, uid, ids, {'report_data': output_data}, context={})
        return {'type': 'ir.actions.act_url',
                'url': '/gst/export_gst_turnover_report?id=' + str(ids[0]) + '&db=' + str(cr.dbname) + '&uid=' + str(
                    uid), 'nodestroy': True, 'target': 'new'}
