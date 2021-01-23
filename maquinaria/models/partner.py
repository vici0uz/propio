from odoo import fields, models, api, _
from odoo.exceptions import UserError
from clint.textui import colored as col

class res_partner(models.Model):
    _inherit = 'res.partner'

    trabajo_ids = fields.Many2one(comodel_name='maquinaria.trabajo.linea', inverse_name='partner_id', string='Trabajos')
    trabajos_sin_pagar = fields.Integer(compute='_count_trabajos', default=0)

    @api.depends('trabajo_ids.pagado')
    @api.multi
    def _count_trabajos(self):
        for record in self:
            trabajos = self.env['maquinaria.trabajo.linea'].search(['&', '&', ('cerrado', '=', True), ('pagado', '=', False), ('operario', '=', record.id)])
            count = len(trabajos)
            if count != 0:
                record.trabajos_sin_pagar = count

    @api.multi
    def action_ver_trabajos_operario(self):
        for record in self:
            vista = {
                'type': 'ir.actions.act_window',
                'name': 'Trabajos',
                'target': 'self',
                'res_model': 'maquinaria.trabajo.linea',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'domain': [('cerrado', '=', True)],
                'context': {
                    'search_default_operario': record.id,
                    'search_default_filter_no_pagado': 1
                }
            }

            return vista
