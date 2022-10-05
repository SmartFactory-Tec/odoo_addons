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