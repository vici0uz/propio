from odoo import api, fields, models, _
from odoo.exceptions import UserError
from clint.textui import colored as col


class SaleOrder(models.Model):
    _inherit = "sale.order"

    type = fields.Selection([('voucher', 'Voucher'), ('order', 'Sale Order')], default='order', string='Document type')
    date_order = fields.Datetime(default=lambda self: fields.Datetime.now())
    hora_de_entrega = fields.Float(string='Hora de entrega')


    @api.model
    def create(self, vals):
        if vals.get('type') == 'voucher':
            if vals.get('name', _('New')) == _('New'):
                if 'company_id' in vals:
                    vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code('sale.order.voucher') or _('New')
                else:
                    vals['name'] = self.env['ir.sequence'].next_by_code('sale.order.voucher') or _('New')
        result = super(SaleOrder, self).create(vals)
        return result
