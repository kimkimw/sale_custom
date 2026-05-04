# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class SaleKpiReport(models.Model):
    _name = 'sale.kpi.report'
    _description = 'Báo cáo công việc hằng ngày (KPI)'
    _order = 'date desc, id desc'
    _rec_name = 'partner_id'

    name = fields.Char('STT', default=lambda self: _('Mới'), copy=False, readonly=True)
    sequence = fields.Integer('STT', default=10)
    date = fields.Datetime('Ngày', default=fields.Datetime.today, required=True, tracking=True)
    partner_id = fields.Many2one('res.partner', string='Tên Khách Hàng', required=True)
    partner_phone = fields.Char('Số điện thoại', related='partner_id.phone', store=True)

    product_id = fields.Many2one('product.product', string='Sản phẩm', required=False)
    product_ids = fields.Many2many('product.product', string='Sản phẩm', required=False)
    product_template_id = fields.Many2one(
        'product.template', string='Sản phẩm', related='product_id.product_tmpl_id', store=True)

    form_type = fields.Selection([
        ('f1', 'Photo TĐ 1 mặt'),
        ('f2', 'Photo TĐ 2 mặt'),
        ('i1', 'In TĐ 1 mặt'),
        ('i2', 'In TĐ 2 mặt'),
        ('i3', 'In màu 1 mặt'),
        ('i4', 'In màu 2 mặt'),
        ('ad', 'In quảng cáo'),
        ('other', 'Khác'),
    ], string='Hình thức', default='i3')

    description = fields.Char('Diễn giải')

    quantity = fields.Float('Số lượng', default=1.0, required=True)
    turn_count = fields.Integer('Số lượt', default=1, required=True)
    unit_price = fields.Float('Đơn giá')
    total_amount = fields.Monetary(
        'Thành tiền', compute='_compute_total_amount', store=True)

    currency_id = fields.Many2one(
        'res.currency', string='Tiền tệ',
        default=lambda self: self.env.company.currency_id)

    note = fields.Char('Ghi chú')

    state = fields.Selection([
        ('draft', 'Nháp'),
        ('confirmed', 'Đã xác nhận'),
        ('wrong', 'Sai đơn hàng'),
    ], string='Trạng thái', default='draft', tracking=True, copy=False)

    user_id = fields.Many2one(
        'res.users', string='Nhân viên',
        default=lambda self: self.env.user, required=True)

    sale_order_id = fields.Many2one('sale.order', string='Đơn hàng liên quan')

    def unlink(self):
        if self.state != 'draft':
            raise ValidationError('Không thể xóa dòng đã xác nhận hoặc sai')
        return super().unlink()


    @api.depends('quantity', 'unit_price')
    def _compute_total_amount(self):
        for rec in self:
            rec.total_amount = (rec.quantity or 0.0) * (rec.unit_price or 0.0)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.unit_price = self.product_id.lst_price

    def action_confirm(self):
        for rec in self:
            if rec.state == 'confirmed':
                raise UserError(_('Đơn đã được xác nhận.'))
            rec.state = 'confirmed'

    def action_mark_wrong(self):
        for rec in self:
            rec.state = 'wrong'

    def action_reset_draft(self):
        for rec in self:
            rec.state = 'draft'

    @api.model_create_multi
    def create(self, vals_list):
        return super().create(vals_list)
