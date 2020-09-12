from odoo import fields, api, models, _
from clint.textui import colored as col


class cocina_orden(models.Model):
    _name = 'cocina.orden'

    sequence = fields.Integer(string='Order')
    name = fields.Char(string='Name')
    hora_de_entrega = fields.Float(string='Hora de entrega')
    tiempo_transcurrido = fields.Float(string='Tiempo transcurrido')
    tiempo_restante = fields.Float(string='Tiempo restante')
    completado = fields.Boolean(string='Completado')
    order_id = fields.Many2one(comodel_name='sale.order', string='Order', required=True)
    partner_id = fields.Many2one(comodel_name='res.partner', string='Partner', required=True)
    linea_ids = fields.One2many(comodel_name='cocina.orden.linea', inverse_name='cocina_orden_id')


class cocina_orden_linea(models.Model):
    _name = 'cocina.orden.linea'

    product_id = fields.Many2one(comodel_name='product.product', string='Product', required=True)
    qty = fields.Float(string='Quantity')
    cocina_orden_id = fields.Many2one(comodel_name='cocina.orden')
    uom_id = fields.Many2one(string='Quantity', comodel_name='uom.uom')


class cocina_receta(models.Model):
    _name = 'cocina.receta'

    name = fields.Char(string='Name')
    product_tmpl_id = fields.Many2one(comodel_name='product.template')
    linea_ids = fields.One2many(comodel_name='cocina.receta.linea', inverse_name='cocina_receta_id')


class cocina_receta_linea(models.Model):
    _name = 'cocina.receta.linea'

    cocina_receta_id = fields.Many2one(comodel_name='cocina.receta')
    product_tmpl_id = fields.Many2one(comodel_name='product.template')
    uom_id = fields.Many2one(string='Quantity', comodel_name='uom.uom')
