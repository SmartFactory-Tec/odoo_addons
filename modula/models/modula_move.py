from typing import List, Type

import odoo.api
from odoo import models, exceptions
from odoo.addons.stock.models.stock_move import StockMove
import requests


# ModulaMove model extended to include validation and synchronization with the Modula WMS
# When the moves quantity done equals the quantity requested, the move is completed

modula_location_name = 'Modula Slim'
class ModulaMove(models.Model):
    _inherit = 'stock.move'

    def _process_state_change(self, vals):
        # When a move line changes into 'assigned', it is ready for picking
        state = vals['state']
        if state == 'assigned':
            self._process_assigned_moves(vals)

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

    def write(self, vals):
        if ('state' in vals):
            self._process_state_change(vals)

        super(ModulaMove, self).write(vals)

        return True
