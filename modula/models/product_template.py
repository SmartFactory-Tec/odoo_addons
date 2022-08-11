from odoo import models, fields, exceptions
from odoo.addons.uom.models.uom_uom import UoM
import requests
import logging
_logger = logging.getLogger(__name__)

# Extends the stock module product model with actions for interfacing with the Modula WMS
class ProductTemplate(models.Model):
    _inherit = 'product.template'


    # Register the Product into the WMS when created
    def create(self, vals_list):
        products = super(ProductTemplate, self).create(vals_list)

        request_contents = []

        for vals in vals_list:
            _logger.debug(vals)

        for product in products:
            _logger.debug(product.description)
            request_contents.append({
                'Articulo': product,
                'Descripcion': product.name,
                'Umi': product.uom_id.name,
            })



        _logger.debug("Request contents:")
        _logger.debug(request_contents)

        response = requests.post('http://10.22.229.191/Modula/api/Articulos', json=request_contents)

        if (response.status_code != 200):
            # TODO find out if a better error type can be implemented
            raise exceptions.ValidationError("Modula request error:\n" + str(response.content))

        return products