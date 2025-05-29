from odoo import models, api, exceptions, Command


class EstateProperty(models.Model):
    _inherit = 'estate.property'


    def action_sell_property(self):
        for record in self:
            # Creates an Invoice with a 6% price increase and an added flat administrative fee
            move = self.env['account.move'].create({
                'partner_id': record.buyer_id.id,
                'move_type': 'out_invoice',
                'line_ids':[
                    Command.create({
                        'name': record.name + " deduction",
                        'quantity': 1,
                        'price_unit': record.selling_price * 6/100
                    }),
                    Command.create({
                        'name': 'Administrative Fees',
                        'quantity': 1,
                        'price_unit': 100.00
                    })
                ]
            })

        return super().action_sell_property()
