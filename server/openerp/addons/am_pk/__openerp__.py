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
    "name": "Credits",
    "author": "Pavan Kumar Kota(A product of pK)",
    "version": "1.0",
	"category" : "Credits(pK)",
    "depends": ['base','cashback','web'],
    #"depends": ['base'],
	'data': ['security/credits_security.xml','security/ir.model.access.csv','credits.xml'],
    #'data': ['credits.xml'],
    #'update_xml' : ['report/bill_details_report_view.xml'],
    "description": "The base module for stock and billing",
    "installable": True,
    'css':['static/src/css/credits.css','static/src/css/jquery-ui.css'],
    'qweb': ['static/src/xml/project.xml'],
    'js':[
        'static/src/js/main.js',
        'static/src/js/base_widget.js',
        'static/src/js/graph.js',
    ] 	
	
   
}
