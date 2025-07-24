
from datetime import datetime
from dateutil.relativedelta import relativedelta


from odoo import fields, models, api, exceptions, tools, _



class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Real Estate Property"
    _order = "id desc"

    _sql_constraints = [
        ('positive_expected_price','CHECK(expected_price>0)','The property expected price must be strictly positive'),
        ('positive_selling_price','CHECK(selling_price>=0)','The property selling price must be positive')
    ]

    name = fields.Char(required=True)
    description = fields.Text()
    company_id = fields.Many2one("res.company",
        string="Agency",
        required=True,
        default=lambda self: self.env.user.company_id.id
    )

    property_type_id = fields.Many2one("estate.property.type", string="Property Type")
    property_tag_ids = fields.Many2many("estate.property.tag", string="Property Tags")

    buyer_id = fields.Many2one("res.partner",
        string="Buyer",
        readonly=True,
        copy=False
    )
    salesperson_id = fields.Many2one("res.users",
        string="Salesperson",
        domain="[('company_ids', 'any', [('id', '=', company_id)])]",
        default=lambda self: self.env.user
    )

    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Offers")

    postcode = fields.Char()
    date_availability = fields.Date(
        copy=False,
        default=fields.Date.today() + relativedelta(months=3)
    )
    expected_price = fields.Float(required=True)
    best_price = fields.Float(compute="_compute_best_price")
    selling_price = fields.Float(
        readonly=True,
        copy=False
    )
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer(default=0)
    garden_orientation = fields.Selection(
        string='Garden Orientation',
        selection=[
            ('north', 'North'),
            ('south', 'South'),
            ('east', 'East'),
            ('west', 'West')],
        help="Towards which direction the garden is facing"
    )

    total_area = fields.Integer(compute="_compute_total_area")

    # mistakenly called state, used status instead, can't fix
    # needs to be deleted
    #####
    #####
    #####
    #####
    status = fields.Selection(
        required=True,
        readonly=True,
        copy=False,
        selection=[
            ('new','New'),
            ('offer_received','Offer Received'),
            ('offer_accepted','Offer Accepted'),
            ('sold','Sold'),
            ('cancelled','Cancelled')
        ],
        default='new'
    )
    #####
    #####
    #####
    #####

    state = fields.Selection(
        required=True,
        readonly=True,
        copy=False,
        selection=[
            ('new','New'),
            ('offer_received','Offer Received'),
            ('offer_accepted','Offer Accepted'),
            ('sold','Sold'),
            ('cancelled','Cancelled')
        ],
        default='new'
    )


    # if a property is sold or cancelled, its values should not be modified
    is_readonly = fields.Boolean(compute="_compute_is_readonly")

    active = fields.Boolean('Active', default=True)


    # -------------------------------------------------------------------------
    # COMPUTE METHODS
    # -------------------------------------------------------------------------

    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        for record in self:
                record.total_area = record.living_area + record.garden_area
      
    
    @api.depends("offer_ids")
    def _compute_best_price(self):
        for record in self:
            if record.offer_ids:
                    #altra opzione
                    #max(record.offer_ids, key=lambda o:o.price).price
                    record.best_price = max(record.offer_ids.mapped('price'))
            else:
                record.best_price = 0

    @api.depends("state")
    def _compute_is_readonly(self):
        for record in self:
            record.is_readonly = record.state == 'sold' or record.state == 'cancelled'


    # -------------------------------------------------------------------------
    # ONCHANGE METHODS
    # -------------------------------------------------------------------------

    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = 'north'
        else:
            self.garden_area = 0
            self.garden_orientation = ''


    # -------------------------------------------------------------------------
    # CONSTRAINS METHODS
    # -------------------------------------------------------------------------

    @api.constrains('selling_price','expected_price')
    def _selling_price_lower_limit(self):
        for record in self:
            if not tools.float_utils.float_is_zero(record.selling_price, precision_digits=2):
                if tools.float_utils.float_compare(record.expected_price * 90/100, record.selling_price, precision_digits=2) == 1:
                    raise exceptions.ValidationError(_("The selling price need to be at least 90% of the expected price"))




    # -------------------------------------------------------------------------
    # CRUD METHODS
    # -------------------------------------------------------------------------

    def unlink(self):
        for record in self:
            if record.state != 'cancelled' and record.state != 'new':
                raise exceptions.UserError(_("Can't delete property that is not New or Cancelled"))
        return super().unlink()

    # -------------------------------------------------------------------------
    # ACTION METHODS
    # -------------------------------------------------------------------------

    def action_sell_property(self):
        for record in self:
            if record.state != 'sold' and record.state != 'cancelled':
                if record.state != 'offer_accepted':
                    raise exceptions.UserError(_("Can't sell property without an accepted offer"))
                else:
                    record.state = 'sold'
            else:
                raise exceptions.UserError(_("Can't change state of property"))
        return True

    def action_cancel_property(self):
        for record in self:
            if record.state != 'sold' and record.state != 'cancelled':
                record.state = 'cancelled'
            else:
                raise exceptions.UserError(_("Can't change state of property"))
        return True

