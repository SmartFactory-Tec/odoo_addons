from odoo import models
import requests

# Extends the stock module product model with actions for updating the WMS
class Product(models.Model):
    _inherit = 'product.product'

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

    def _create_model_on_wms(self):
        for product in self:
            print(product)

        return True