# -*- coding: utf-8 -*-
from openerp import http

# class TscCustomization(http.Controller):
#     @http.route('/tsc_customization/tsc_customization/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/tsc_customization/tsc_customization/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('tsc_customization.listing', {
#             'root': '/tsc_customization/tsc_customization',
#             'objects': http.request.env['tsc_customization.tsc_customization'].search([]),
#         })

#     @http.route('/tsc_customization/tsc_customization/objects/<model("tsc_customization.tsc_customization"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('tsc_customization.object', {
#             'object': obj
#         })