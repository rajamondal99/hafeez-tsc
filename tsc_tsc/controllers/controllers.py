# -*- coding: utf-8 -*-
from openerp import http

# class TscTsc(http.Controller):
#     @http.route('/tsc_tsc/tsc_tsc/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/tsc_tsc/tsc_tsc/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('tsc_tsc.listing', {
#             'root': '/tsc_tsc/tsc_tsc',
#             'objects': http.request.env['tsc_tsc.tsc_tsc'].search([]),
#         })

#     @http.route('/tsc_tsc/tsc_tsc/objects/<model("tsc_tsc.tsc_tsc"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('tsc_tsc.object', {
#             'object': obj
#         })