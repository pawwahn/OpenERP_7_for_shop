import openerp
from openerp.addons.web.controllers.main import manifest_list, module_boot, html_template
import openerp.addons.web.http as http
import logging
from openerp.addons.web.controllers.main import content_disposition
from openerp import pooler
import base64

''' author : Pavan Kota '''
class cashback_summary_report(http.Controller):
    _cp_path = '/cashback'	

    @http.httprequest
    def export_cashback_report(self, req, id, db, uid, s_action=None, **kw):
        logging.info("----------------------------------->>>>")
        logging.info(id)
        path = req.httprequest.path[1:].split('/')
        cr = pooler.get_db(db).cursor()
        pool = pooler.get_pool(db)
        model = pool.get('cashback.summary')
        #obj=model.browse(cr, int(uid),  int(id))
        cr.execute('select report_data from cashback_summary where id =%s',(id,))
        vals = cr.dictfetchall()
        if vals:
            print '************* inside vals', vals
            print vals[0]['report_data']
            
            filecontent = vals[0]['report_data']
            print '**************** file content',filecontent
            filename = "Cashback_Summary_Report.xlsx"
            if filecontent and filename:
                return req.make_response(filecontent,
                    headers=[('Content-Type', 'application/octet-stream'),
                            ('Content-Disposition', content_disposition(filename,req))])
        return req.not_found()
