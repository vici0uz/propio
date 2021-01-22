from odoo import fields, models, api, _
from odoo.exceptions import UserError
from clint.textui import colored as col
from datetime import datetime, timedelta



# class maquinaria_wizard(models.TransientModel):
#     _name = 'maquinaria.wizard'

#     def _get_default_tipo(self):
#         print(col.red('ALAN DEBUG: ' + str(self.env.context['tipo'])))
#         return self.env.context['tipo']

#     maquina_id = fields.Many2one(comodel_name='maquinaria.maquina', ondelete='restrict')

#     trabajo_destino = fields.Many2one(comodel_name='maquinaria.destino', string='Lugar')
#     operador = fields.Many2one(comodel_name='res.partner')
#     fecha_trabajo = fields.Date(default=fields.Date.context_today, string="Fecha")


#     # Apertura
#     odometro = fields.Integer()
#     odometro_imagen = fields.Binary(string='Odometro inicial', attachment=True)


#     horas_trabajadas = fields.Float()
#     notas = fields.Text(string='Description')

#     tipo = fields.Selection([('open', 'Abierto'), ('closed', 'Cerrado')], string='Tipo', default=_get_default_tipo)



#     @api.multi
#     def guardar_datos(self):
#         for record in self:
#             if self.env.context['current_id']:
#                 maquina = self.env['maquinaria.maquina'].browse(self.env.context['current_id'])
#                 if self.env.context['tipo'] == 'closed':
#                     # CIERRE
#                     # print(col.red('ALAN DEBUG: ' + str('me pasan que sí papu')))
#                     if record.odometro_final < maquina.ultimo_odometro:
#                         raise UserError('¡El odometro no puede ser inferior al anterior registro')
#                         ultimo_turno = self.env['maquinaria.trabajo.linea'].search([])[-1]
#                         vals = {
#                             'odometro_final': record.odometro,
#                             'odometro_final_imagen': record.odometro_imagen,
#                             'cerrado': True
#                         }
#                         ultimo_turno.write(vals)
#                 else:
#                     linea_data = {
#                         'odometro_inicial': record.odometro,
#                         'odometro_inicial_imagen': record.odometro_imagen,
#                         'fecha_trabajo': record.fecha_trabajo,
#                         'operador': record.operador.id,
#                         'trabajo_destino': record.trabajo_destino.id
#                     }
#                 maquina.browse(self.env.context['current_id']).write({
#                     'ultimo_odometro': record.odometro,
#                     'ultimo_lugar': record.trabajo_destino.id,
#                     'ultimo_operador': record.operador.id,
#                     'ultima_foto_odometro': record.odometro_imagen,
#                     'trabajo_lineas_ids': [(0, 0, linea_data)]
#                     })

class formulario_pagar(models.TransientModel):
    _name = 'maquinaria.wizard'

    @api.multi
    def _get_turnos_ids(self):
        print(col.red('ALAN DEBUG: ' + str('llamado trabajos')))
        turnos = self.env.context['jeje']
        return turnos

    @api.depends('trabajo_ids')
    @api.multi
    def _calcular_horas(self):
        print(col.red('ALAN DEBUG: ' + str("llamado horas")))
        horas = 0
        minutos = 0
        fecha = datetime.min
        for trabajo in self.trabajo_ids:
            fecha1 = datetime.strptime(trabajo.hora_inicio, '%Y-%m-%d %H:%M:%S')
            fecha2 = datetime.strptime(trabajo.hora_final,  '%Y-%m-%d %H:%M:%S')

            res = fecha2 - fecha1
            fech = (datetime.min + res).time()
            print(col.red('ALAN DEBUG: ' + str(fech)))
            fecha += res
        print(col.red('ALAN DEBUG: ' + str(fecha)))
        print(col.red('ALAN DEBUG: ' + str(type(fecha))))
        self.horas_trabajadas = fecha.hour

    @api.multi
    def guardar_datos(self):
        for record in self:
            for trabajo in record.trabajo_ids:
                trabajo.write({'pagado': True, 'fecha_pago': fields.Date.today()})
                trabajo.registrar_pago()

    trabajo_ids = fields.Many2many(comodel_name='maquinaria.trabajo.linea', relation='wizard_rel', column1='uno', column2='dos', default=_get_turnos_ids)
    horas_trabajadas = fields.Float(compute='_calcular_horas')
