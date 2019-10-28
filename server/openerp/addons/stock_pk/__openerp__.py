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
    "name": "Payments",
    "author": "Pavan Kumar Kota(A product of pK)",
    "version": "1.0",
	"category" : "Payments(pK)",
    "depends": ['base','am_pk'],
	'data': ['stock_bill_pk.xml','security/stock_pk_security.xml','security/ir.model.access.csv'],
    #'data': ['credits.xml','security/credits_security.xml','security/ir.model.access.csv',],
    "description": "The base module for stock and billing",
    "installable": True,
    'css':['static/src/css/stock_pk.css'],
   
}
