from odoo import models, fields, api


class Partner(models.Model):
    _inherit = 'res.partner'

    property_ids = fields.One2many("estate.property", "buyer_id", string="Bought Properties",
        domain=['|',('state','=','sold'),('state','=','offer_accepted')])
    
    