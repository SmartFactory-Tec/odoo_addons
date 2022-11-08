import json

import requests

from odoo import http
from odoo.http import request, Response

class ModulaController(http.Controller):

    def _do_basic_auth(self):
        auth = request.httprequest.authorization
        request.session.authenticate('test', auth.username, auth.password)

    @http.route('/modula/input_request', auth='public', type='http', methods=['post'], csrf=False)
    def input_request(self, code, qty):
        self._do_basic_auth()

        qty = float(qty)

        # TODO find out a way to find stock locations without depending on localization setting
        src_location_id = request.env['stock.location'].search([('complete_name', '=', 'SF/Existencias')])[0].id
        dest_location_id = request.env['stock.location'].search([('complete_name', '=', 'SF/Existencias/Modula Slim')])[0].id

        return self._do_transfer(code, float(qty), src_location_id, dest_location_id)

    @http.route('/modula/output_request', auth='public', type='http', methods=['post'], csrf=False)
    def output_request(self, code, qty):
        self._do_basic_auth()

        qty = float(qty)

        # TODO find out a way to find stock locations without depending on localization setting
        src_location_id = request.env['stock.location'].search([('complete_name', '=', 'SF/Existencias/Modula Slim')])[0].id
        dest_location_id = request.env['stock.location'].search([('complete_name', '=', 'SF/Existencias')])[0].id

        return self._do_transfer(code, float(qty), src_location_id, dest_location_id)



    def _do_transfer(self, product_code, qty, origin_id, dest_id):
        product = request.env['product.product'].search([('default_code', '=', product_code)])

        if len(product) == 0:
            # if the given code was not found, 404
            return Response('could not find product with given code', status=404)

        if len(product) > 1:
            # sanity check, if more than one product with same code was found
            return Response(status=500)

        picking = request.env['stock.picking'].create([{
            'move_type': 'one',
            'picking_type_id': request.env.ref('modula.sf_to_modula_move_t').id,
            'location_id': origin_id,
            'location_dest_id': dest_id,
        }])[0]

        request.env['stock.move'].create([{
            'name': '',
            'picking_id': picking.id,
            'product_id': product.id,
            'product_uom': product.uom_id.id,
            'product_uom_qty': qty,
            'location_id': origin_id,
            'location_dest_id': dest_id,
        }])

        picking[0].action_confirm()
        picking[0].action_assign()

        if picking[0].state != 'assigned':
            # not enough products were found, delete the picking and error out
            picking.unlink()
            return Response('unable to reserve quantity requested', status=409)

        return Response(str(picking[0].id), status=200)


#
    @http.route('/modula/tray_status', auth='public', type='http',methods=['get'])
    def picking_status(self, picking_id):
        self._do_basic_auth()

        picking = request.env['stock.picking'].browse([int(picking_id)])

        response = requests.get('http://10.22.229.191/Modula/api/Picking')

        if len(response.text) == 0:
            return Response(json.dumps({
                'status': 'not in picking'
            }), status=200)

        body = response.json()

        if body['Item'] != picking.move_ids[0].product_id.default_code or body['Cantidad'] != picking.move_ids[0].product_uom_qty:
            return Response(json.dumps({
                'status': 'other product in picking',
                'product': body['Item']
            }), status=200)

        return Response(json.dumps({
            'status': 'in picking',
            'qty': body['Cantidad'],
            'tray_id': body['Baia'], # (sic)
            'pos_x': body['PosX'],
            'pos_y': body['PosY'],
            'dim_x': body['DimX'],
            'dim_y': body['DimY'],
        }), status=200)


    @http.route('/modula/request_confirmation', auth='none', type='http',methods=['post'], csrf=False)
    def request_confirmation(self, picking_id):
        self._do_basic_auth()

        picking = request.env['stock.picking'].browse([int(picking_id)])

        action = picking.button_validate()

        for key in action.keys():
            print(key)

        transfer = request.env['stock.immediate.transfer']

        transfer = transfer.create([{
            'pick_ids': [picking.id],
        }])

        transfer_line = request.env['stock.immediate.transfer.line']

        transfer_line.create([{
            'to_immediate': True,
            'immediate_transfer_id': transfer[0].id,
            'picking_id': picking[0].id,
        }])

        transfer[0].with_context(action['context']).process()

        return Response(status=200)