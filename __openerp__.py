# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2016-2022 Tiny SPRL (<http://tiny.be>).
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
    "name": "Gestion KIU",
    "version": "1.0.1",
    "author": "Cesar Chirinos",
    'sequence': 10,
    'summary': 'Gestion KIU',
    "category": "Generic Modules/Others",
    "website": "http://www.tegnus.net",
    'images': ['images/tegnus-logo.jpg'],
    "description": "Gestion KIU",
    "depends": ['base','report_webkit'],
    "update_xml" : [
        'kiu_view.xml',
        'auto_kiu_view.xml'
    ],
    "active": False,
    "installable": True
}
