# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import models, fields, api



class ProductTemplate(models.Model):
    _inherit = 'product.template'

    unit_type = fields.Char('Đơn vị tính')


