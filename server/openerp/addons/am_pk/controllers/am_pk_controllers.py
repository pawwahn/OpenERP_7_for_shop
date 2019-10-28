import openerp
from openerp.addons.web.controllers.main import manifest_list, module_boot, html_template
import openerp.addons.web.http as http
import logging
from openerp.addons.web.controllers.main import content_disposition
from openerp import pooler
import base64

''' author : Pavan Kota '''
class am_pk_report(http.Controller):
    _cp_path = '/am_pk'
    
    @http.httprequest
    def export_exit_report(self, req, id, db, uid, s_action=None, **kw):
        path = req.httprequest.path[1:].split('/')
        cr = pooler.get_db(db).cursor()
        pool = pooler.get_pool(db)
        model = pool.get('exit.report.detail')
        obj=model.browse(cr, int(uid),  int(id))
        
        if obj:
            filecontent = base64.b64decode(obj.data)
            filename = obj.name+'.xls'
            if filecontent and filename:
                cr.close()
                return req.make_response(filecontent,
                    headers=[('Content-Type', 'application/octet-stream'),
                            ('Content-Disposition', content_disposition(filename, req))])
        cr.close()
        return req.not_found() 

    @http.httprequest
    def export_attrition_report(self, req, id, db, uid, s_action=None, **kw):
        path = req.httprequest.path[1:].split('/')
        cr = pooler.get_db(db).cursor()
        pool = pooler.get_pool(db)
        model = pool.get('attrition.report')
        #obj=model.browse(cr, int(uid),  int(id))
        cr.execute('select report_data from attrition_report where id =%s',(id,))
        vals = cr.dictfetchall()
        if vals:
            print '************* inside vals', vals
            print vals[0]['report_data']
            
            filecontent = vals[0]['report_data']
            print '**************** file content',filecontent
            filename = "Attrition_Report.xlsx"
            if filecontent and filename:
                return req.make_response(filecontent,
                    headers=[('Content-Type', 'application/octet-stream'),
                            ('Content-Disposition', content_disposition(filename,req))])
        return req.not_found()

    @http.httprequest
    def export_income_report(self, req, id, db, uid, s_action=None, **kw):
        path = req.httprequest.path[1:].split('/')
        cr = pooler.get_db(db).cursor()
        pool = pooler.get_pool(db)
        model = pool.get('to.recieve.report')
        #obj=model.browse(cr, int(uid),  int(id))
        cr.execute('select report_data from to_recieve_report where id =%s',(id,))
        vals = cr.dictfetchall()
        if vals:
            print '************* inside vals', vals
            print vals[0]['report_data']
            
            filecontent = vals[0]['report_data']
            print '**************** file content',filecontent
            filename = "To_Receive_Amount_Report.xlsx"
            if filecontent and filename:
                return req.make_response(filecontent,
                    headers=[('Content-Type', 'application/octet-stream'),
                            ('Content-Disposition', content_disposition(filename,req))])
        return req.not_found()		

    @http.httprequest
    def download(self, req, id, db, uid,model,s_action=None, **kw):
        cr = pooler.get_db(db).cursor()
        pool = pooler.get_pool(db)
        model = pool.get(model)
        obj=model.browse(cr, uid,  int(id))
        if obj:
              filecontent = base64.b64decode(str(obj.upload_file))
              filename = obj.file_name
              if filecontent and filename:
                  return req.make_response(filecontent,
                      headers=[('Content-Type', 'application/octet-stream'),
                              ('Content-Disposition', content_disposition(filename,req))])
        return req.not_found()
