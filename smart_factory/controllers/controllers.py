# -*- coding: utf-8 -*-
# from odoo import http


# class SmartFactory(http.Controller):
#     @http.route('/smart_factory/smart_factory', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/smart_factory/smart_factory/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('smart_factory.listing', {
#             'root': '/smart_factory/smart_factory',
#             'objects': http.request.env['smart_factory.smart_factory'].search([]),
#         })

#     @http.route('/smart_factory/smart_factory/objects/<model("smart_factory.smart_factory"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('smart_factory.object', {
#             'object': obj
#         })
