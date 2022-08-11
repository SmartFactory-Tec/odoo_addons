from typing import List, Type
from odoo import models
from odoo.addons.stock.models.stock_move import StockMove
import requests


# ModulaMove model extended to include validation and synchronization with the Modula WMS

location_name = 'Modula Slim'
class ModulaMove(models.Model):
    _inherit = 'stock.move'

    # Send the move lines to modula
    def _send_modula_entries(self, moves: Type[StockMove]):
        modula_moves = moves.filtered(lambda move: move.location_dest_id.name == location_name and move.state == 'assigned')

        entry_requests = list(map(lambda move: {
            "Orden": move.id,
            "Articulo": move.product_id.default_code,
            "Cantidad": move.product_qty,
        }, modula_moves))

        print("entry request")
        print(entry_requests)

        if len(entry_requests) != 0:
            response = requests.post('http://10.22.229.191/Modula/api/Entradas', json=entry_requests)
            print(response.content)

    # Send the move lines to modula
    def _send_modula_exits(self, moves: Type[StockMove]):
        modula_moves = moves.filtered(
            lambda move: move.location_id.name == location_name and move.state == 'assigned')

        exit_requests = list(map(lambda move: {
            "Orden": move.id,
            "Articulo": move.product_id.default_code,
            "Cantidad": move.product_qty,
        }, modula_moves))

        print("exit request")
        print(exit_requests)
        if len(exit_requests) != 0:
            response = requests.post('http://10.22.229.191/Modula/api/Salidas', json=exit_requests)
            print(response.content)

    def _confirm_modula_entry(self, moves: Type[StockMove]):
        modula_moves = moves.filtered(lambda move: move.location_dest_id.name == location_name and move.state == 'done')

    def create(self, vals_list):
        created_moves = super(ModulaMove, self).create(vals_list)

        self._send_modula_entries(created_moves)
        self._send_modula_exits(created_moves)

        return created_moves

    def write(self, vals):
        # First do the update
        super(ModulaMove, self).write(vals)

        # Then request an entry picking into Modula for any qualifying moves
        self._send_modula_entries(self)
        # Finally request exit pickings into Modula for any qualifying moves
        self._send_modula_exits(self)

        return True
