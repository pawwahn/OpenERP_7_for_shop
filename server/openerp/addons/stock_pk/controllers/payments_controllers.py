import openerp
from openerp.addons.web.controllers.main import manifest_list, module_boot, html_template
import openerp.addons.web.http as http
import logging
from openerp.addons.web.controllers.main import content_disposition
from openerp import pooler
import base64

''' author : Pavan Kota '''
class stock_pk_report(http.Controller):
    _cp_path = '/stock_pk'	

    @http.httprequest
    def download(self, req, id, db, uid,model,s_action=None, **kw):
        logging.info("download function called ################")
        pat = req.httprequest.path[1:].split('/')
        cr = pooler.get_db(db).cursor()
        pool = pooler.get_pool(db)
        model = pool.get('paid.bill.attachments.detail')
        obj=model.browse(cr, int(uid),  int(id))
        if obj:
              logging.info("#### inside object##########")
              filecontent = base64.b64decode(str(obj.attachment))
              #filecontent = obj['attachment']
              #filename = obj['attachment_text']
              filename = obj.attachment_text
              if filecontent and filename:
                  logging.info("#$######### inside file content and file name")
                  logging.info(filecontent)
                  logging.info(filename)
                  return req.make_response(filecontent,
                      headers=[('Content-Type', 'application/octet-stream'),
                              ('Content-Disposition', content_disposition(filename,req))])
        cr.close()
        return req.not_found()
