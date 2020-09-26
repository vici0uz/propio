from odoo import api, fields, models, _
from odoo.exceptions import UserError
from clint.textui import colored as col


class SaleOrder(models.Model):
    _inherit = "sale.order"

    type = fields.Selection([('voucher', 'Voucher'), ('order', 'Sale Order')], default='order', string='Document type')
    date_order = fields.Datetime(default=lambda self: fields.Datetime.now())
    hora_de_entrega = fields.Float(string='Hora de entrega')
    cocina_orden_id = fields.Many2one(comodel_name='cocina.orden')

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

    @api.multi
    def crear_orden_cocina(self):
        for record in self:
            if not record.cocina_orden_id:
                vals = {
                    'name': self.env['ir.sequence'].next_by_code('cocina.orden.secuencia'),
                    'partner_id': record.partner_id.id,
                    'hora_de_entrega': record.hora_de_entrega,
                    'order_id': record.id
                }
                new_order = self.env['cocina.orden'].create(vals)
                record.write({'cocina_orden_id': new_order.id})
            else:
                record.cocina_orden_id.unlink()

    @api.multi
    def mostrar_orden(self):
        for record in self:
            if record.cocina_orden_id:
                view = self.env.ref('foods.orden_cocina_form')
                ventana = {
                    'type': 'ir.actions.act_window',
                    'name': 'Orden',
                    'res_model': 'cocina.orden',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'view_id': view.id,
                    'target': 'new',
                    'context': {'current_id': record.cocina_orden_id.id}
                }

                return ventana
