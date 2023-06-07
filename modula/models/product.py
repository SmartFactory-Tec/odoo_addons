from odoo import models, fields, exceptions
import requests
import logging
_logger = logging.getLogger(__name__)

# Extends the stock module product model with actions for interfacing with the Modula WMS
class Product(models.Model):
    _inherit = 'product.product'


    # Register the Product into the WMS when created
    def create(self, vals_list):

        request_contents = []

        for vals in vals_list:
            # Values are not directly stored on the product, get the template associated with it
            template = self.env['product.template'].browse(vals['product_tmpl_id'])
            request_contents.append({
                'Articulo': template.default_code,
                'Descripcion': template.name,
                'Umi': 'PZ',
            })

        # Create the product objects
        products = super(Product, self).create(vals_list)

        _logger.debug("Request contents:")
        _logger.debug(request_contents)

        # Try to call the modula API
        response = requests.post('http://10.22.229.191/Modula/api/Articulos', json=request_contents)

        if (response.status_code != 200):
            # TODO find out if a better error type can be implemented
            raise exceptions.ValidationError("Modula request error:\n" + str(response.content))

        # Store the new products
        return products
    
    def action_transfer_to_sf(self):
        sf_location = self.env['stock.location'].search([('complete_name', '=', 'SF/Stock')])
        if sf_location:
            warehouse = self.env['stock.warehouse'].search([], limit=1)
            if warehouse:
                picking_type = self.env.ref('stock.picking_type_internal')
                picking_vals = {
                    'picking_type_id': picking_type.id,
                    'location_id': warehouse.lot_stock_id.id,
                    'location_dest_id': sf_location[0].id,
                }
                picking = self.env['stock.picking'].create(picking_vals)

                move_vals = {
                    'name': self.name,
                    'product_id': self.id,
                    'product_uom_qty': 1,
                    'location_id': warehouse.lot_stock_id.id,
                    'location_dest_id': sf_location[0].id,
                    'picking_id': picking.id,
                }
                move = self.env['stock.move'].create(move_vals)

                picking.action_confirm()
                picking.action_assign()
                move._action_done()

                return True
        return False