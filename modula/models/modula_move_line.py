from odoo import models, exceptions
import requests
import logging

_logger = logging.getLogger(__name__)

modula_location_name = 'Modula Slim'

class ModulaMoveLine(models.Model):
    _inherit = 'stock.move.line'

    def _process_qty_done_change(self, vals):
        # Get the moves that involve modula
        modula_moves_lines = self.filtered(
            lambda move: move.location_id.name == modula_location_name or move.location_dest_id == modula_location_name)

        # If there are no modula moves, ignore
        if len(modula_moves_lines) == 0:
            return

        # If there is more than 1 modula move, error, as you can't update two pickings at the same time.
        if (len(modula_moves_lines) > 1):
            raise exceptions.UserError('You can only update one picking at a time!')

        move = modula_moves_lines[0].move_id

        # Request information about the current picking
        response = requests.get('http://10.22.229.191/Modula/api/Picking')
        body = response.json()
        # TODO what if no current picking

        # If the current item in picking is not the one being updated, error
        if body['Item'] != move.product_id.default_code:
            raise exceptions.UserError('Can not update item not currently in picking!')

        qty_done = vals['qty_done']

        # If the current quantity wouldn't be completed by this picking, ignore
        if (body['Cantidad'] > qty_done):
            return

        # If user tries to complete an order with more than expected, error
        if (body['Cantidad'] < qty_done):
            raise exceptions.UserError('Done quantity is bigger than picking capacity!')

        # If user tries to modify an order that is already completed, error
        if (move.quantity_done == body['Cantidad']):
            raise exceptions.UserError('This move is already completed!')

        # Everything confirmed, confirm the picking
        requests.post('http://10.22.229.191/Modula/api/ConfirmarPicking')

    def write(self, vals):
        _logger.debug(vals)
        if ('qty_done' in vals):
            self._process_qty_done_change(vals)

        super(ModulaMoveLine, self).write(vals)

        return True