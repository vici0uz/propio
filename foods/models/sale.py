from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    type = fields.Selection([('voucher', 'Voucher'), ('order', 'Sale Order')], default='order', string='Document type')
    date_order = fields.Datetime(default=lambda self: fields.Datetime.now())
