
from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import fields, models, api, exceptions, tools, _
from odoo.tools import float_utils

class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Real Estate Property Offer"
    _order = "price desc"

    _sql_constraints = [
        ('positive_price','CHECK(price>0)','The offer price must be stricktly positive')
    ]

    price = fields.Float()

    # mistakenly called state, used status instead, can't fix
    # needs to be deleted
    #####
    #####
    #####
    #####
    status = fields.Selection(
        readonly=True,
        copy=False,
        selection=[
            ('accepted', 'Accepted'),
            ('refused', 'Refused'),
            ]
        )
    #####
    #####
    #####
    #####
    
    state = fields.Selection(
        readonly=True,
        copy=False,
        selection=[
            ('accepted', 'Accepted'),
            ('refused', 'Refused'),
            ]
        )
    
    partner_id = fields.Many2one('res.partner', required=True)
    property_id = fields.Many2one('estate.property', required=True)
    
    validity = fields.Integer(default=7)
    date_deadline = fields.Date(compute="_compute_date_deadline", inverse="_inverse_date_deadline")

    property_type_id = fields.Many2one(related='property_id.property_type_id')

    # -------------------------------------------------------------------------
    # COMPUTE METHODS
    # -------------------------------------------------------------------------

    @api.depends('validity','create_date')
    def _compute_date_deadline(self):
        for record in self:
            if record.create_date:
                record.date_deadline = record.create_date + relativedelta(days=record.validity)
            else:
                record.date_deadline = fields.Date.today() + relativedelta(days=record.validity)

    def _inverse_date_deadline(self):
        for record in self:
            if record.create_date:
                record.validity = (record.date_deadline - record.create_date.date()).days

    # -------------------------------------------------------------------------
    # CRUD METHODS
    # -------------------------------------------------------------------------

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            target_property = self.env['estate.property'].browse(vals['property_id'])
            if float_utils.float_compare(
                target_property.best_price,
                vals['price'],
                precision_digits=2) == 1:
                    raise exceptions.UserError(_("Can't create offers lower than current highest offer"))
            target_property.state = 'offer_received'
            output = super().create(vals)
        return output   
            

    # -------------------------------------------------------------------------
    # ACTION METHODS
    # -------------------------------------------------------------------------

    def action_accept_offer(self):
        for record in self:
            if record.property_id.selling_price == 0:
                record.state = 'accepted'
                record.property_id.buyer_id = record.partner_id
                record.property_id.selling_price = record.price
                record.property_id.state = 'offer_accepted'
            else:
                raise exceptions.UserError(_("Can't accept offer, property already has accepted offer"))
        return True

    def action_refuse_offer(self):
        for record in self:
            if record.state != 'accepted':
                record.state = 'refused'
            else:
                raise exceptions.UserError(_("Can't change state of offer"))
        return True
