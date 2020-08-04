from odoo import fields, models, api
import odoo.addons.decimal_precision as dp


class res_partner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'
    # _description = 'Partner'

    cid = fields.Char(string='Certificate number', size=32)


    _sql_constraint = [
            ('cid', 'unique(cid)',
                'The Certification Number of the partner must be unique'),
            ('vat', 'unique(vat)', 'VAT must be unique')
        ]
