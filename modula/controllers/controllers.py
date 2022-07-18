# -*- coding: utf-8 -*-
# from odoo import http


# class Modula(http.Controller):
#     @http.route('/modula/modula', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/modula/modula/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('modula.listing', {
#             'root': '/modula/modula',
#             'objects': http.request.env['modula.modula'].search([]),
#         })

#     @http.route('/modula/modula/objects/<model("modula.modula"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('modula.object', {
#             'object': obj
#         })
