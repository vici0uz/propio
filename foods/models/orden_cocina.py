from odoo import fields, api, model, _
from clint.textui import colored as col

class cocina_orden(model.Models):
    _name = 'cocina.orden'

    order_id = fields.Many2one(comodel_name='sale.order', string='Order', required=True)
    partner_id = fields.Many2one(comodel_name='res.partner', string='Partner', required=True)
    linea_ids = fields.One2many(comodel_name='cocina.orden.linea', inverse_name='cocina_orden_id')


class cocina_orden_linea(model.Models):
    _name = 'cocina.orden.linea'

    product_id = fields.Many2one(comodel_name='product.product', string='Product', required=True)
    qty = fields.Float(string='Quantity')
    uom_id = fields.Many2one
    cocina_orden_id = fields.Many2one(comodel_name='cocina.orden')


class cocina_receta(model.Models):
    _name = 'cocina.receta'

    product_tmpl_id = fields.Many2one(comodel_name='product.template')
    linea_ids = fields.One2many(comodel_name='cocina.receta.linea', inverse_name='cocina_receta_id')


class cocina_receta_linea(model.Models):
    _inherit =
