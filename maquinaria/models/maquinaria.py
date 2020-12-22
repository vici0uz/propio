from odoo import fields, models, api, _
from odoo.exceptions import UserError
from clint.textui import colored as col
from datetime import datetime, timedelta


class maquina(models.Model):
    _name = 'maquinaria.maquina'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    active = fields.Boolean(default=True)
    responsable = fields.Many2one(comodel_name='res.partner')
    name = fields.Char(compute='_set_name', store=True)
    modelo = fields.Many2one(comodel_name='maquinaria.maquina.modelo')
    trabajo_lineas_ids = fields.One2many(comodel_name='maquinaria.trabajo.linea', inverse_name='maquina_id')
    no_serie = fields.Char(string='Nro de serie', required=True)

    # Computados
    ultimo_trabajo = fields.Many2one(comodel_name='maquinaria.trabajo.linea', compute='devel', store=True)
    ultimo_odometro = fields.Float(default=0.0)
    ultimo_lugar = fields.Many2one(comodel_name='maquinaria.destino')
    ultimo_operador = fields.Many2one(comodel_name='res.partner')
    ultima_foto_odometro = fields.Binary()

    @api.multi
    def devel(self):
        for record in self:
            ultimo_trabajo = record.trabajo_lineas_ids[-1]
            record.ultimo_trabajo = ultimo_trabajo
            if record.ultimo_trabajo:
                if record.ultimo_odometro < record.ultimo_trabajo.odometro_inicial:
                    record.ultimo_odometro = record.ultimo_trabajo.odometro_inicial
                    record.ultima_foto_odometro = record.ultimo_trabajo.odometro_inicial_imagen
                    record.ultimo_lugar = record.ultimo_trabajo.trabajo_destino.id
                if record.ultimo_odometro < record.ultimo_trabajo.odometro_final:
                    record.ultimo_odometro = record.ultimo_trabajo.odometro_final
                    record.ultima_foto_odometro = record.ultimo_trabajo.odometro_final_imagen



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
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.multi
    @api.depends('maquina_id', 'operario', 'trabajo_destino')
    def _set_name(self):
        for record in self:
            if not(record.operador):
                print(col.red('ALAN DEBUG: ' + str('joder operador')))
            if not(record.maquina_id.name):
                print(col.red('ALAN DEBUG: ' + str('joser maquina')))
            if not(record.trabajo_destino):
                print(col.red('ALAN DEBUG: ' + str('joder lugar')))
            record.name = record.operador.name + '/ ' + record.maquina_id.name + ' - ' +record.trabajo_destino.name

    # name = fields.Char(compute='_set_name', store=True)
    name = fields.Char()
    maquina_id = fields.Many2one(comodel_name='maquinaria.maquina', ondelete='restrict')
    trabajo_destino = fields.Many2one(comodel_name='maquinaria.destino', string='Lugar', ondelete='restrict')
    # operador = fields.Many2one(comodel_name='res.partner', ondelete='restrict', string='Operador')

    operario = fields.Many2one(comodel_name='res.partner', ondelete='restrict', string='Operario')
    fecha_trabajo = fields.Date(default=fields.Date.context_today, string="Fecha")
    cerrado = fields.Boolean(default=False)
    status = fields.Selection([('abierto', 'Abierto'), ('cerrado', 'Cerrado')], default='abierto')

    # Apertura
    odometro_inicial = fields.Float(digits=(16, 1))
    odometro_inicial_imagen = fields.Binary(string='Odometro inicial', attachment=True)

    # Final
    odometro_final = fields.Float(digits=(16, 1))
    odometro_final_imagen = fields.Binary(string='Odometro final', attachment=True)
    horas_trabajadas = fields.Float(compute='_calcular_horas')
    horas_trabajadas_str = fields.Char(compute='_calcular_horas', string="Horas trabajadas")
    notas = fields.Text(string='Description')

    # Nuevos

    tiene_observacion = fields.Boolean()
    observacion = fields.Text()
    descripcion = fields.Text()
    combustible = fields.Float()
    hora_inicio = fields.Datetime()
    hora_final = fields.Datetime()

    km_diferencia = fields.Float(compute='_calcular_km', string="Cuenta odometro")

    @api.multi
    def _calcular_km(self):
        for record in self:
            if (record.odometro_inicial and record.odometro_final):
                res = (record.odometro_final - record.odometro_inicial)
                record.km_diferencia = res

    @api.depends('hora_inicio', 'hora_final')
    @api.multi
    def _calcular_horas(self):
        for record in self:
            if (record.hora_inicio and record.hora_final):
                fecha1 = datetime.strptime(record.hora_inicio, '%Y-%m-%d %H:%M:%S')
                fecha2 = datetime.strptime(record.hora_final,  '%Y-%m-%d %H:%M:%S')

                res = fecha2 - fecha1
                horas = datetime.strptime(str(res), '%H:%M:%S')
                hora_str = "{hora}.{minuto}".format(hora=horas.hour, minuto=horas.minute)
                hora_decimal = float(hora_str)
                record.horas_trabajadas = hora_decimal
                record.horas_trabajadas_str = "{hora}:{minuto}".format(hora=horas.hour, minuto=horas.minute)
