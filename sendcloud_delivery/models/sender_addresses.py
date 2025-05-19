from odoo import models, fields, api, tools, _


class SenderAddress(models.Model):
    _name = "sender.address"

    address_id = fields.Integer('Sender Address ID')
    name = fields.Char('Company Name')
    contact_name = fields.Char('Contact Name')
    email = fields.Char('Email')
    telephone = fields.Char('Telephone')
    street = fields.Char('Street')
    house_number = fields.Char('House Number')
    postal_code = fields.Char('Postal Code')
    city = fields.Char('City')
    country = fields.Char('Country')
    vat_number = fields.Char('Vat Number')
    eori_number = fields.Char('Eori Number')
    default_address = fields.Boolean('Default Address')
    shipping_partner_id = fields.Many2one('shipping.partner','Shipping Partner')
