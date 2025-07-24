from odoo import models, api, exceptions, Command, _

class EstateProperty(models.Model):
    _inherit = 'estate.property'

    def __create_invoice(self):
        for record in self:
            # Creates an Invoice for 6% of the original price and an added flat administrative fee
            move = self.env['account.move'].sudo().create({
                'partner_id': record.buyer_id.id,
                'move_type': 'out_invoice',
                'line_ids':[
                    Command.create({
                        'name': _("Percentage for: ") + record.name,
                        'quantity': 1,
                        'price_unit': record.selling_price * 6/100
                    }),
                    Command.create({
                        'name': _('Administrative Fees'),
                        'quantity': 1,
                        'price_unit': 100.00
                    })
                ]
            })

    def action_sell_property(self):
        # Cheks if the user can actually update the property, before allowing them to create an invoice
        self.check_access('write')
        self.__create_invoice()
        return super().action_sell_property()
