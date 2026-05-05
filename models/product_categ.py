# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class ProductCateg(models.Model):
    _name = 'product.categ'


    name = fields.Char('Tên', required=True)
