# -*- coding: utf-8 -*-
from odoo import http

# class SaleAutomation(http.Controller):
#     @http.route('/sale_automation/sale_automation/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sale_automation/sale_automation/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sale_automation.listing', {
#             'root': '/sale_automation/sale_automation',
#             'objects': http.request.env['sale_automation.sale_automation'].search([]),
#         })

#     @http.route('/sale_automation/sale_automation/objects/<model("sale_automation.sale_automation"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sale_automation.object', {
#             'object': obj
#         })