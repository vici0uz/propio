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
            # print(col.red('ALAN DEBUG: ' + str(self.env.context['tipo'])))
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
                    # 'default_tipo': 'open'
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
    trabajo_destino = fields.Many2one(comodel_name='maquinaria.destino', string='Lugar', ondelete='restrict')
    operador = fields.Many2one(comodel_name='res.partner', ondelete='restrict')
    fecha_trabajo = fields.Date(default=fields.Date.context_today, string="Fecha")
    cerrado = fields.Boolean(default=False)
    status = fields.Selection([('abierto', 'Abierto'), ('cerrado', 'Cerrado')], default='abierto')

    # Apertura
    odometro_inicial = fields.Float()
    odometro_inicial_imagen = fields.Binary(string='Odometro inicial', attachment=True)

    # Final
    odometro_final = fields.Float()
    odometro_final_imagen = fields.Binary(string='Odometro final', attachment=True)
    horas_trabajadas = fields.Float()
    notas = fields.Text(string='Description')

    # Nuevos

    tiene_observacion = fields.Boolean()
    observacion = fields.Text()
    descripcion = fields.Text()
    combustible = fields.Float()
    hora_inicio = fields.Datetime()
    hora_final = fields.Datetime()
