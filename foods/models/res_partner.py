from odoo import fields, models, api, _


class res_partner(models.Model):
    _inherit = 'res.partner'

    cocina_orden_ids = fields.One2many(comodel_name='cocina.orden', inverse_name='partner_id', string='Orders')
