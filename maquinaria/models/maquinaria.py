from odoo import fields, models, api, _
from clint.textui import colored as col


class maquina(models.Model):
    _name = 'maquinaria.maquina'

    responsable = fields.Many2one(comodel_name='res.partner')
    operador = fields.Many2one(comodel_name='res.partner')
    # marca = fields.Many2one(comodel_name='maquinaria.maquina.marca')
    modelo = fields.Many2one(comodel_name='maquinaria.maquina.modelo')
    lugar_de_trabajo = fields.Many2one(comodel_name='maquinaria.destino')
    trabajo_lineas_ids = fields.One2many(comodel_name='maquinaria.trabajo.linea', inverse_name='maquina_id')


class maquina_marca(models.Model):
    _name = 'maquinaria.maquina.marca'

    name = fields.Char(string='Name')


class maquina_modelo(models.Model):
    _name = 'maquinaria.maquina.modelo'

    name = fields.Char(string='Name')
    marca_id = fields.Many2one(comodel_name='maquinaria.maquina.marca')


class maquina_destino(models.Model):
    _name = 'maquinaria.destino'

    name = fields.Char(string='Name')


class maquinaria_trabajo(models.Model):
    _name = 'maquinaria.trabajo.linea'

    maquina_id = fields.Many2one(comodel_name='maquinaria.maquina')
    odometro = fields.Integer()
    odometro_imagen = fields.Binary(string='Odometro')
    trabajo_destino = fields.Many2one(comodel_name='maquinaria.destino')
