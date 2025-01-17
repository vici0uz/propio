from odoo import fields, models, api, _
from odoo.exceptions import UserError
from clint.textui import colored as col

class maquinaria_wizard(models.TransientModel):
    _name = 'maquinaria.wizard'

    maquina_id = fields.Many2one(comodel_name='maquinaria.maquina', ondelete='restrict')

    trabajo_destino = fields.Many2one(comodel_name='maquinaria.destino', string='Lugar')
    operador = fields.Many2one(comodel_name='res.partner')
    fecha_trabajo = fields.Date(default=fields.Date.context_today, string="Fecha")


    # Apertura
    odometro_inicial = fields.Integer()
    odometro_inicial_imagen = fields.Binary(string='Odometro inicial', attachment=True)

    # Final
    odometro_final = fields.Integer()
    odometro_final_imagen = fields.Binary(string='Odometro final', attachment=True)
    horas_trabajadas = fields.Float()
    notas = fields.Text(string='Description')

    @api.multi
    def guardar_datos(self):
        for record in self:
            if self.env.context['current_id']:
                maquina = self.env['maquinaria.maquina'].browse(self.env.context['current_id'])
                if record.odometro < maquina.ultimo_odometro:
                    raise UserError('¡El odometro no puede ser inferior al anterior trabajo!')
                linea_data = {
                    'odometro': record.odometro,
                    'odometro_imagen': record.odometro_imagen,
                    'fecha_trabajo': record.fecha_trabajo,
                    'operador': record.operador.id,
                    'trabajo_destino': record.trabajo_destino.id
                }
                maquina.browse(self.env.context['current_id']).write({
                    'ultimo_odometro': record.odometro,
                    'ultimo_lugar': record.trabajo_destino.id,
                    'ultimo_operador': record.operador.id,
                    'ultima_foto_odometro': record.odometro_imagen,
                    'trabajo_lineas_ids': [(0, 0, linea_data)]
                    })
