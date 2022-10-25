from odoo import http


class ModulaController(http.Controller):
    @http.route('/modula/product_request', auth='public', methods=['post'])
    def product_request(self, **kw):
        return http.request.make_response('')
#
    @http.route('/modula/tray_status', auth='public', methods=['get'])
    def tray_status(self, **kw):
        return http.request.make_response('')

    @http.route('/modula/request_confirmation', auth='public', methods=['post'])
    def request_confiramtion(self, **kw):
        return http.request.make_response('')