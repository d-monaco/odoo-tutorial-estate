
from odoo import fields, models

class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Real Estate Property Tags"
    _order = "name"

    _sql_constraints = [
        ('unique_tag_name','UNIQUE(name)','Cannot have two tags with the same name')
    ]

    name = fields.Char(required=True)
    color = fields.Integer()
