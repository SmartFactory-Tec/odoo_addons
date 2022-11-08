import requests

from odoo import http
from odoo.http import request, Response, Request

class ModulaController(http.Controller):

    @http.route('/modula/input_request', auth='public', type='http', methods=['post'], csrf=False)
    def product_request(self, code, qty):
        qty = float(qty)
        auth = request.httprequest.authorization
        request.session.authenticate('test', auth.username, auth.password)

        product = request.env['product.product'].search([('default_code', '=', code)])

        if len(product) == 0:
            return Response(status=404)

        if len(product) > 1:
            return Response(status=500)

        product.ensure_one()

        print(product[0].qty_available)
        if product[0].qty_available < qty:
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
            'reserved_uom_qty': qty,
            'picking_id': picking[0].id,
        }])

        quants = product.stock_quant_ids

        quants[0].write({
            'reserved_quantity': quants[0].reserved_quantity + qty,
        })

        move[0]._action_confirm()

        print(picking[0].id)
        return Response(str(picking[0].id), status=200)
#
    @http.route('/modula/tray_status', auth='public', type='http',methods=['get'])
    def tray_status(self, **kw):
        auth = request.httprequest.authorization
        request.session.authenticate('test', auth.username, auth.password)

        response = requests.get('http://10.22.229.191/Modula/api/Picking')
        if len(response.text) == 0:
            return Response('not in picking', status=503)

        return Response(status=200)


    @http.route('/modula/request_confirmation', auth='none', type='http',methods=['post'], csrf=False)
    def request_confirmation(self, picking_id):
        auth = request.httprequest.authorization
        request.session.authenticate('test', auth.username, auth.password)

        picking = request.env['stock.picking'].browse(int(picking_id))

        picking.button_validate()

        transfer = request.env['stock.immediate.transfer'].with_env(picking.env).create({
            'pick_ids': [pick.id for pick in picking ],
        })

        request.env['stock.immediate.transfer.line'].create({
            'to_immediate': True,
            'picking_id': picking_id,
            'immediate_transfer_id': transfer.id,
        })

        transfer[0].process()

        return Response(status=200)