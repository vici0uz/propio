from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    type = fields.Selection(selection_add=[('cook', 'Cook')])
    avaliable_4_cooking = fields.Boolean(string='Avaliable', default=True)
