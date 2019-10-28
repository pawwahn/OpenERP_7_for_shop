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
    "name": "Rate Finder",
    "author": "Pavan Kumar Kota(A product of pK)",
    "version": "1.0",
	"category" : "Rate Finder",
    "depends": ['base'],
    'css':['static/src/css/ssh_rate_finder.css'],
	'data': ['ssh_rate_finder.xml','security/ssh_rate_finder_security.xml','security/ir.model.access.csv',],
    "description": "The base module to find the rates of the products in the stores.",
    "installable": True,
   
}
