# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2012 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    "name": "GST",
    "author": "Pavan Kumar Kota(A product of pK)",
    "version": "1.0",
	"category" : "GST",
    "depends": ['base'],
	'data': ['gst_view.xml','gst_purchase_view.xml','report/gst_sales_purchase_report_view.xml',
            'security/gst_security.xml','security/ir.model.access.csv',],
    "description": "The base module to submit GST to the Government.",
    #'css':['static/src/css/cashback.css','static/src/css/jquery-ui.css'],
	'css': ['static/src/css/gst.css'],
    "installable": True,
   
}
