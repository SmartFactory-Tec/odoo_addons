import requests

from odoo import http
from odoo.http import request, Response, Request

class ModulaController(http.Controller):

    @http.route('/modula/input_request', auth='public', type='http', methods=['post'], csrf=False)
    def product_request(self, code, qty):
        auth = request.httprequest.authorization
        request.session.authenticate('odoo', auth.username, auth.password)

        product = request.env['product.product'].search([('default_code', '=', code)])

        if len(product) == 0:
            return Response(status=404)

        if len(product) > 1:
            return Response(status=500)

        product.ensure_one()

        print(product[0].qty_available)
        if product[0].qty_available < float(qty):
            return Response(409)

        src_location_id = request.env['stock.location'].search([('complete_name', '=', 'SF/Existencias')])[0].id
        dest_location_id = request.env['stock.location'].search([('complete_name', '=', 'SF/Existencias/Modula Slim')])[0].id

        picking = request.env['stock.picking'].create([{
            'move_type': 'one',
            'picking_type_id': request.env.ref('modula.sf_to_modula_move_t').id,
            'location_id': src_location_id,
            'location_dest_id': dest_location_id,
        }])

        move = request.env['stock.move'].create([{
            'name': '',
            'picking_id': picking[0].id,
            'product_id': product[0].id,
            'product_uom': product[0].uom_id.id,
            'product_uom_qty': qty,
            'location_id': src_location_id,
            'location_dest_id': dest_location_id
        }])

        move_line = request.env['stock.move.line'].create([{
            'location_id': src_location_id ,
            'location_dest_id': dest_location_id,
            'product_id': product[0].id,
            'product_uom_id': product[0].uom_id.id,
            'product_uom_qty': qty,
            'picking_id': picking[0].id,
        }])

        move[0]._action_confirm()

        print(picking[0].id)
        return Response(str(picking[0].id), status=200)
#
    @http.route('/modula/tray_status', auth='public', type='http',methods=['get'])
    def tray_status(self, **kw):
        auth = request.httprequest.authorization
        request.session.authenticate('odoo', auth.username, auth.password)

        response = requests.get('http://10.22.229.191/Modula/api/Picking')
        if len(response.text) == 0:
            return Response('not in picking', status=503)

        return Response(status=200)


    @http.route('/modula/request_confirmation', auth='none', type='http',methods=['post'], csrf=False)
    def request_confirmation(self, picking_id):
        auth = request.httprequest.authorization
        request.session.authenticate('odoo', auth.username, auth.password)

        picking = request.env['stock.picking'].browse(int(picking_id))

        picking.button_validate()

        transfer = request.env['stock.immediate.transfer'].create({
            'pick_ids': [picking_id],
            'immediate_transfer_line_ids': [{
                'to_immediate': True,
                'picking_id': picking_id,
            }]
        })

        transfer.process()

        return Response(status=200)