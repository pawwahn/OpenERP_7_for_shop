import openerp
from openerp.addons.web.controllers.main import manifest_list, module_boot, html_template
import openerp.addons.web.http as http
import logging
from openerp.addons.web.controllers.main import content_disposition
from openerp import pooler
import base64

''' author : Pavan Kota '''
class rf_report(http.Controller):
    _cp_path = '/rfpk'

    @http.httprequest
    def export_xls(self, req, id, db, uid, model, s_action=None, **kw):
        path = req.httprequest.path[1:].split('/')
        cr = pooler.get_db(db).cursor()
        pool = pooler.get_pool(db)
        model = pool.get(str(model))
        obj = model.browse(cr, uid, int(id))
        if obj:
            logging.info("*****************")
            filecontent = base64.b64decode(obj.data)
            logging.info(filecontent)
            filename = obj.name + '.xls'
            if filecontent and filename:
                return req.make_response(filecontent,
                                         headers=[('Content-Type', 'application/octet-stream'),
                                                  ('Content-Disposition', content_disposition(filename, req))])
        return req.not_found()

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
    def download_errors(self, req, id, db, uid,model,s_action=None, **kw):
        logging.info("*************************>>>>>>>>>>>>>>>")
        logging.info("called **********>>>>>>>>>>>")
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
