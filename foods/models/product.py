from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _name = 'product.template'
    _inherit = 'product.template'

    type = fields.Selection(selection_add=[('cook', 'Cook')])
    avaliable_4_cooking = fields.Boolean(string='Avaliable', default=True)
    recetas_ids = fields.Many2many(comodel_name='receta.cocina', relation='product_tmpl_receta_rel', column1='receta_id', column2='product_id', string='Recetas')
