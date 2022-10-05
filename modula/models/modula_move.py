from typing import List, Type

from odoo import models, exceptions, api
import requests
import logging

_logger = logging.getLogger(__name__)

# ModulaMove model extended to include validation and synchronization with the Modula WMS
# When the moves quantity done equals the quantity requested, the move is completed

modula_location_name = 'Modula Slim'


class ModulaMove(models.Model):
    _inherit = 'stock.move'

    # When a change is performed on child move lines, run this
    def process_qty_done_change(self):
        # TODO add limiter to move_line to impede modification of an already completed move
        self.ensure_one()

    def _process_state_change(self, vals):
        # When a move line changes into 'assigned', it is ready for picking
        state = vals['state']
        if state == 'assigned':
            self._process_assigned_moves(vals)
        if state == 'done':
            self._process_done_moves(vals)

    def _process_assigned_moves(self, vals):
        # Filter entries and exits for modula only
        entries = self.filtered(lambda move: move.location_dest_id.name == modula_location_name)
        exits = self.filtered(lambda move: move.location_id.name == modula_location_name)

        # Generate json request for both entries and exits
        entry_api_request = list(map(lambda move: {
            "Orden": move.id,
            "Articulo": move.product_id.default_code,
            "Cantidad": move.product_qty,
        }, entries))

        exit_api_request = list(map(lambda move: {
            "Orden": move.id,
            "Articulo": move.product_id.default_code,
            "Cantidad": move.product_qty,
        }, exits))

        # Send entries and exits if they're not empty
        if len(entry_api_request) != 0:
            response = requests.post('http://10.22.229.191/Modula/api/Entradas', json=entry_api_request)
            if response.status_code != 200:
                raise exceptions.ValidationError('Modula API error: ' + str(response.content))

        if len(exit_api_request) != 0:
            response = requests.post('http://10.22.229.191/Modula/api/Salidas', json=exit_api_request)
            if response.status_code != 200:
                raise exceptions.ValidationError('Modula API error: ' + str(response.content))

    def _process_done_moves(self, vals):
        _logger.debug("Showing done moves")

        if len(self) == 0: return

        for move in self:
            _logger.debug(move.product_id.name)

        self.ensure_one()

        move = self[0]

        # Request information about the current picking
        response = requests.get('http://10.22.229.191/Modula/api/Picking')
        body = response.json()
        # TODO what if no current picking

        self._quantity_done_compute()

        # If the current item in picking is not the one being updated, error
        if body['Item'] != move.product_id.default_code:
            raise exceptions.UserError('Can not update item not currently in picking!')

        # If the current quantity wouldn't be completed by this picking, ignore
        if (body['Cantidad'] > move.quantity_done):
            return

        # If user tries to complete an order with more than expected, error
        if (body['Cantidad'] < move.quantity_done):
            raise exceptions.UserError('Done quantity is bigger than picking capacity!')

        # Everything confirmed, confirm the picking
        requests.post('http://10.22.229.191/Modula/api/ConfirmarPicking')

    def write(self, vals):
        if ('state' in vals):
            self._process_state_change(vals)

        super(ModulaMove, self).write(vals)

        return True
