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
    ultimo_trabajo = fields.Many2one(comodel_name='maquinaria.trabajo.linea', compute='set_stats', store=True)
    ultimo_odometro = fields.Float(default=0.0, compute='set_stats', store=True)
    ultimo_lugar = fields.Many2one(comodel_name='maquinaria.destino', compute='set_stats', store=True)
    ultimo_operador = fields.Many2one(comodel_name='res.partner', compute='set_stats', store=True)
    ultima_foto_odometro = fields.Binary(compute='set_stats', store=True)

    # NUevos
    carga_combustible_ids = fields.One2many(comodel_name='maquinaria.combustible.carga', inverse_name='maquina_id')
    intervalo_mantenimiento = fields.Integer()
    siguiente_manteniento = fields.Integer()
    estado_mantenimiento = fields.Selection([('pendiente', 'Pendiente'), ('en_curso', 'Mantenimiento en curso'), ('ok', 'Mantinimiento al día')])
    mantenimiento_ids = fields.One2many(comodel_name='maquinaria.mantenimiento', inverse_name='maquina_id')

    @api.depends('trabajo_lineas_ids')
    @api.multi
    def set_stats(self):
        for record in self:
            if record.trabajo_lineas_ids:
                ultimo_trabajo = record.trabajo_lineas_ids[-1]
                record.ultimo_trabajo = ultimo_trabajo.id
                if record.ultimo_trabajo:
                    if record.ultimo_odometro < record.ultimo_trabajo.odometro_inicial:
                        record.ultimo_odometro = record.ultimo_trabajo.odometro_inicial
                        record.ultima_foto_odometro = record.ultimo_trabajo.odometro_inicial_imagen
                        record.ultimo_lugar = record.ultimo_trabajo.trabajo_destino.id
                        record.ultimo_operador = record.ultimo_trabajo.operario.id
                    if record.ultimo_odometro < record.ultimo_trabajo.odometro_final:
                        record.ultimo_odometro = record.ultimo_trabajo.odometro_final
                        record.ultima_foto_odometro = record.ultimo_trabajo.odometro_final_imagen
                        record.ultimo_operador = record.ultimo_trabajo.operario.id
                        record.ultimo_lugar = record.ultimo_trabajo.trabajo_destino.id

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
            record.name = record.operario.name + '/ ' + record.maquina_id.name + ' - ' +record.trabajo_destino.name

    name = fields.Char(compute='_set_name', store=True)
    # name = fields.Char()
    maquina_id = fields.Many2one(comodel_name='maquinaria.maquina', ondelete='restrict')
    trabajo_destino = fields.Many2one(comodel_name='maquinaria.destino', string='Lugar', ondelete='restrict')
    # operador = fields.Many2one(comodel_name='res.partner', ondelete='restrict', string='Operador')

    operario = fields.Many2one(comodel_name='res.partner', string='Operario', compute='set_operario', store=True)
    fecha_trabajo = fields.Date(string="Fecha")
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

    pagado = fields.Boolean(default=False)
    fecha_pago = fields.Datetime()
    pagador_id = fields.Many2one(comodel_name='res.partner')

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

    @api.depends('create_uid')
    @api.multi
    def set_operario(self):
        for record in self:
            user = self.env['res.users'].browse(record.create_uid.id)
            record.operario = user.partner_id.id

    @api.multi
    def pagar(self):
        operario = self[0].operario.id
        for record in self:
            if record.operario.id != operario:
                raise UserError("Solo puede pagar a un operario a la vez!")
            message = ("Pagado el %s, por %s") % (fields.Date.today(), self.env.user.name)
            record.message_post(body=message, type="notification", subtype="mt_comment")


class maquinaria_combustible_carga(models.Model):
    _name = 'maquinaria.combustible.carga'

    maquina_id = fields.Many2one(comodel_name='maquinaria.maquina', string='Maquina')
    operario_id = fields.Many2one(comodel_name='res.partner', string='Operario', compute='set_operario', store=True)
    cantidad = fields.Float()
    fecha_carga = fields.Date(string="Fecha")
    fecha_hora = fields.Datetime()

    @api.multi
    @api.depends('create_uid')
    def set_operario(self):
        print(col.red('ALAN DEBUG: ' + str('llamado operario')))
        for record in self:
            user = self.env['res.users'].browse(record.create_uid.id)
            record.operario_id = user.partner_id.id


class maquinaria_mantenimiento(models.Model):
    _name = 'maquinaria.mantenimiento'

    maquina_id = fields.Many2one(comodel_name='maquinaria.maquina')
    fecha_mantenimiento = fields.Datetime()
