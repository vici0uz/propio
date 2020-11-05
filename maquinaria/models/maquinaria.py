from odoo import fields, models, api, _
from odoo.exceptions import UserError
from clint.textui import colored as col


class maquina(models.Model):
    _name = 'maquinaria.maquina'

    active = fields.Boolean(default=True)
    responsable = fields.Many2one(comodel_name='res.partner')
    name = fields.Char(compute='_set_name', store=True)
    modelo = fields.Many2one(comodel_name='maquinaria.maquina.modelo')
    trabajo_lineas_ids = fields.One2many(comodel_name='maquinaria.trabajo.linea', inverse_name='maquina_id')
    no_serie = fields.Char(string='Nro de serie', required=True)

    # Computados
    ultimo_odometro = fields.Integer()
    ultimo_lugar = fields.Many2one(comodel_name='maquinaria.destino')
    ultimo_operador = fields.Many2one(comodel_name='res.partner')
    ultima_foto_odometro = fields.Binary()

    @api.multi
    @api.depends('modelo', 'no_serie')
    def _set_name(self):
        for record in self:
            if record.no_serie and record.modelo:
                record.name = record.modelo.name + '/ ' + record.no_serie

    @api.multi
    def launch_wizard(self):
        for record in self:
            view = self.env.ref('maquinaria.wizard')
            return {
                'type': 'ir.actions.act_window',
                'name': 'Registrar trabajo',
                'res_model': 'maquinaria.wizard',
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': view.id,
                'target': 'new',
                'context': {
                    'current_id': self.id,
                }
            }


class maquina_marca(models.Model):
    _name = 'maquinaria.maquina.marca'

    name = fields.Char(string='Nombre', required=True)


class maquina_modelo(models.Model):
    _name = 'maquinaria.maquina.modelo'

    name = fields.Char(string='Name', compute='_get_model_name', store=True)
    model_name = fields.Char(string='Modelo')
    marca_id = fields.Many2one(comodel_name='maquinaria.maquina.marca', ondelete='restrict')

    @api.depends('marca_id', 'model_name')
    @api.multi
    def _get_model_name(self):
        for record in self:
            if record.marca_id and record.model_name:
                record.name = record.marca_id.name + '/ ' + record.model_name


class maquina_destino(models.Model):
    _name = 'maquinaria.destino'

    name = fields.Char(string='Name')


class maquinaria_trabajo(models.Model):
    _name = 'maquinaria.trabajo.linea'

    maquina_id = fields.Many2one(comodel_name='maquinaria.maquina', ondelete='restrict')
    odometro = fields.Integer()
    odometro_imagen = fields.Binary(string='Foto del Odometro', attachment=True)
    trabajo_destino = fields.Many2one(comodel_name='maquinaria.destino', string='Lugar')
    operador = fields.Many2one(comodel_name='res.partner')
    fecha_trabajo = fields.Date(default=fields.Date.context_today, string="Fecha")


class maquinaria_wizard(models.TransientModel):
    _name = 'maquinaria.wizard'

    maquina_id = fields.Many2one(comodel_name='maquinaria.maquina', ondelete='restrict')
    odometro = fields.Integer()
    odometro_imagen = fields.Binary(string='Foto del Odometro', attachment=True)
    trabajo_destino = fields.Many2one(comodel_name='maquinaria.destino', string='Lugar')
    operador = fields.Many2one(comodel_name='res.partner')
    fecha_trabajo = fields.Date(default=fields.Date.context_today, string="Fecha")

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

# class res_partner(models.Model):
#     _inherit = 'res.partner'

#     horas_trabajadas =
