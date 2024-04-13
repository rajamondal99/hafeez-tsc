# -*- coding: utf-8 -*-
from openerp import http

# class FastraReports(http.Controller):
#     @http.route('/fastra_reports/fastra_reports/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/fastra_reports/fastra_reports/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('fastra_reports.listing', {
#             'root': '/fastra_reports/fastra_reports',
#             'objects': http.request.env['fastra_reports.fastra_reports'].search([]),
#         })

#     @http.route('/fastra_reports/fastra_reports/objects/<model("fastra_reports.fastra_reports"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('fastra_reports.object', {
#             'object': obj
#         })