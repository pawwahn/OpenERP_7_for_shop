import openerp
from openerp.addons.web.controllers.main import manifest_list, module_boot, html_template
import openerp.addons.web.http as http
import logging
from openerp.addons.web.controllers.main import content_disposition
from openerp import pooler
import base64

''' author : Pavan Kota '''
class gst_report(http.Controller):
    _cp_path = '/gst'
    
    @http.httprequest
    def export_gst_report(self, req, id, db, uid, s_action=None, **kw):
        path = req.httprequest.path[1:].split('/')
        cr = pooler.get_db(db).cursor()
        pool = pooler.get_pool(db)
        model = pool.get('gst.header.sales')
        obj=model.browse(cr, int(uid),  int(id))
        cr.execute('select report_data,firm,month,fin_year from gst_header_sales ghs, gst_financial_years gfy where ghs.financial_year=gfy.id and ghs.id=%s',(id,))
        vals = cr.dictfetchall()
        if vals:
            filecontent = vals[0]['report_data']
            if vals[0]['firm']=='New KrishnaArjuna Textiles':
                filename = 'NKT_'+vals[0]['month']+'_'+vals[0]['fin_year'][2:5]+vals[0]['fin_year'][7:9]+"_SALES_REPORT.xlsx"
            else:
                filename = 'SSH_'+vals[0]['month']+'_'+vals[0]['fin_year'][2:5]+vals[0]['fin_year'][7:9]+"_SALES_REPORT.xlsx"
            if filecontent and filename:
                return req.make_response(filecontent,
                    headers=[('Content-Type', 'application/octet-stream'),
                            ('Content-Disposition', content_disposition(filename,req))])
        return req.not_found()
		

    @http.httprequest
    def export_gst_purchase_report(self, req, id, db, uid, s_action=None, **kw):
        path = req.httprequest.path[1:].split('/')
        cr = pooler.get_db(db).cursor()
        pool = pooler.get_pool(db)
        model = pool.get('gst.header.purchase')
        obj=model.browse(cr, int(uid),  int(id))
        cr.execute('select report_data,firm,month,fin_year from gst_header_purchase ghp, gst_financial_years gfy where ghp.financial_year=gfy.id and ghp.id=%s',(id,))
        vals = cr.dictfetchall()
        if vals:
            filecontent = vals[0]['report_data']
            if vals[0]['firm']=='New KrishnaArjuna Textiles':
                filename = 'NKT_'+vals[0]['month']+'_'+vals[0]['fin_year'][2:5]+vals[0]['fin_year'][7:9]+"_PURCHASE_REPORT.xlsx"
            else:
                filename = 'SSH_'+vals[0]['month']+'_'+vals[0]['fin_year'][2:5]+vals[0]['fin_year'][7:9]+"_PURCHASE_REPORT.xlsx"
            if filecontent and filename:
                return req.make_response(filecontent,
                    headers=[('Content-Type', 'application/octet-stream'),
                            ('Content-Disposition', content_disposition(filename,req))])
        return req.not_found()
		
    @http.httprequest
    def export_gst_purchase_sales_report(self, req, id, db, uid,type, s_action=None, **kw):
        path = req.httprequest.path[1:].split('/')
        cr = pooler.get_db(db).cursor()
        pool = pooler.get_pool(db)
        model = pool.get('gst.sales.purchase.report')
        obj=model.browse(cr, int(uid),  int(id))
        cr.execute('select report_data from gst_sales_purchase_report where id =%s',(id,))
        vals = cr.dictfetchall()
        if vals:
            filecontent = vals[0]['report_data']
            if type=='purchase':
                filename = "Purchase Summary Report.xlsx"
            else:
                filename = "Sales Summary Report.xlsx"
            if filecontent and filename:
                return req.make_response(filecontent,
                    headers=[('Content-Type', 'application/octet-stream'),
                            ('Content-Disposition', content_disposition(filename,req))])
        return req.not_found()

    @http.httprequest
    def export_gst_turnover_report(self, req, id, db, uid, s_action=None, **kw):
        path = req.httprequest.path[1:].split('/')
        cr = pooler.get_db(db).cursor()
        pool = pooler.get_pool(db)
        model = pool.get('gst.turnover.report')
        obj=model.browse(cr, int(uid),  int(id))
        cr.execute('select report_data,firm,fin_year from gst_turnover_report gtr,gst_financial_years gfy where gtr.financial_year=gfy.id and gtr.id =%s',(id,))
        vals = cr.dictfetchall()
        if vals:
            filecontent = vals[0]['report_data']
            if vals[0]['firm']=='New KrishnaArjuna Textiles':
                filename = "NKT_"+vals[0]['fin_year'][2:5]+vals[0]['fin_year'][7:9]+"_Turnover Report.xlsx"
            else:
                filename = "SSH_"+vals[0]['fin_year'][2:5]+vals[0]['fin_year'][7:9]+"_Turnover Report.xlsx"
            if filecontent and filename:
                return req.make_response(filecontent,
                    headers=[('Content-Type', 'application/octet-stream'),
                            ('Content-Disposition', content_disposition(filename,req))])
        return req.not_found()
