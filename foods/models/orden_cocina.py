from odoo import fields, api, models, _
from clint.textui import colored as col


class cocina_orden(models.Model):
    _name = 'cocina.orden'

    sequence = fields.Integer(string='Order')
    name = fields.Char(string='Name')
    hora_de_entrega = fields.Float(string='Hora de entrega')
    tiempo_transcurrido = fields.Float(string='Tiempo transcurrido')
    tiempo_restante = fields.Float(string='Tiempo restante')
    completado = fields.Boolean(string='Completado', default=False)
    order_id = fields.Many2one(comodel_name='sale.order', string='Order')
    partner_id = fields.Many2one(comodel_name='res.partner', string='Partner', required=True)
    linea_ids = fields.One2many(comodel_name='cocina.orden.linea', inverse_name='cocina_orden_id')
    prioridad = fields.Selection([('1', '1'), ('2', '2'), ('3', '3')], string='Prioridad')

    @api.model
    def create(self, vals):
        if not vals.get('name'):
            vals['name'] = self.env['ir.sequence'].next_by_code('cocina.orden.secuencia')
        orden = super(cocina_orden, self).create(vals)
        return orden

    @api.model
    def _prepare_from_pos(self, orden_data):
        PosSession = self.env['pos.session']
        session = PosSession.browse(orden_data["pos_session_id"])
        return{
            "partner_id": orden_data['partner_id'],
        }

    @api.model
    def crear_orden_desde_pos(self, orden_data):
        OrdenCocinaLinea = self.env['cocina.orden.linea']

        orden_vals = self._prepare_from_pos(orden_data)

        orden_cocina = self.create(orden_vals.copy())

        for linea in orden_data["lines"]:
            if self.env['product.product'].browse(linea[2].get('product_id')).type == 'cook':
                orden_linea_vals = OrdenCocinaLinea._preparar_desde_pos(orden_cocina, linea[2])
                orden_cocina_linea = OrdenCocinaLinea.create(orden_linea_vals.copy())
        return {
            "orden_cocina_id": orden_cocina.id,
        }


class cocina_orden_linea(models.Model):
    _name = 'cocina.orden.linea'

    product_id = fields.Many2one(comodel_name='product.product', string='Product', required=True)
    qty = fields.Float(string='Quantity')
    cocina_orden_id = fields.Many2one(comodel_name='cocina.orden')
    uom_id = fields.Many2one(string='Quantity', comodel_name='uom.uom')

    @api.model
    def _preparar_desde_pos(self, orden_cocina, linea_data):
        ProductProduct = self.env["product.product"]
        product = ProductProduct.browse(linea_data["product_id"])
        return {
            "cocina_orden_id": orden_cocina.id,
            "product_id": linea_data['product_id'],
            "qty": linea_data['qty']
        }

class cocina_receta(models.Model):
    _name = 'cocina.receta'

    active = fields.Boolean(string='Active', default=True)
    name = fields.Char(string='Name')
    product_tmpl_id = fields.Many2many(comodel_name='product.template', relation='product_tmpl_receta_rel', column1='product_id', column2='receta_id', string='Productos')
    linea_ids = fields.One2many(comodel_name='cocina.receta.linea', inverse_name='cocina_receta_id')


class cocina_receta_linea(models.Model):
    _name = 'cocina.receta.linea'

    cocina_receta_id = fields.Many2one(comodel_name='cocina.receta', string='Receta')
    product_tmpl_id = fields.Many2one(comodel_name='product.product')
    qty = fields.Float(string='Cantidad')
    uom_id = fields.Many2one(string='Unidad de medida', comodel_name='uom.uom')
