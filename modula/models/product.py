from odoo import models
import requests

# Extends the stock module product model with actions for interfacing with the Modula WMS
class Product(models.Model):
    _inherit = 'product.product'

    # Register the Product into the WMS when created
    def create(self, vals_list):
        products = super().create(vals_list)

        request_contents = []

        # TODO figure out what the Articulo (ID) is inside the Product Model
        for product in products:
            request_contents.append({
                'Articulo': product.id,
                'Descripcion': product.name,
                'Umi': product.uom_po_id.name,
            })

        requests.post('http://10.22.229.191/Modula/api/Articulos', json=request_contents)

        return products