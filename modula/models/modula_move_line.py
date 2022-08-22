from odoo import models, exceptions, api
import logging

_logger = logging.getLogger(__name__)

modula_location_name = 'Modula Slim'


class ModulaMoveLine(models.Model):
    _inherit = 'stock.move.line'

    def write(self, vals):
        if 'qty_done' in vals:
            self.update_modula_parent_move()

        super(ModulaMoveLine, self).write(vals)

    def update_modula_parent_move(self):
        modula_move_lines = self.filtered(lambda
                                              move_line: move_line.location_id.name == modula_location_name or move_line.location_dest_id.name == modula_location_name)
        if len(modula_move_lines) == 0:
            return

        move_id = modula_move_lines[0].move_id
        if any(map(lambda moveLine: moveLine.move_id != move_id, modula_move_lines)):
            raise exceptions.ValidationError('Can only modify modula move lines for one move')

        move_id.process_qty_done_change()
