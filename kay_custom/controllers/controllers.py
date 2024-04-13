# -*- coding: utf-8 -*-
from openerp import http

# class KayCustom(http.Controller):
#     @http.route('/kay_custom/kay_custom/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/kay_custom/kay_custom/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('kay_custom.listing', {
#             'root': '/kay_custom/kay_custom',
#             'objects': http.request.env['kay_custom.kay_custom'].search([]),
#         })

#     @http.route('/kay_custom/kay_custom/objects/<model("kay_custom.kay_custom"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('kay_custom.object', {
#             'object': obj
#         })