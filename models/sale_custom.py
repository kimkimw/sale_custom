# -*- coding: utf-8 -*-
from datetime import datetime
from email.policy import default

from reportlab.graphics.transform import inverse

from odoo import models, fields, api


class Sale_Custom(models.Model):
    # _name = "sale.custom"
    _inherit = 'sale.order'

    phone_number = fields.Char('Số điện thoại', related='partner_id.phone')
    advance_payment = fields.Monetary('Tiền ứng trước')
    tax_custom = fields.Float('Tổng Thuế')
    is_tax_8 = fields.Boolean('Thuế 8%')
    is_tax_10 = fields.Boolean('Thuế 10%')
    address = fields.Char('Địa chỉ', related='partner_id.street')
    address_new = fields.Char('Địa chỉ', store=True)

    order_date = fields.Date('Ngày đặt hàng', default=datetime.now())
    total_price_custom = fields.Float('Tổng tiền thanh toán', compute='_compute_total_price_custom',store=True)

    is_print_mark = fields.Boolean('Con dấu')

    def confirm_order_custom(self):
        for rec in self:
            rec.state = 'sale'

    def un_confirm_order(self):
        for rec in self:
            rec.state = 'draft'

    @api.onchange('is_tax_8', 'is_tax_10')
    def onchange_tax_custom(self):
        amount_untaxed = sum(line.price_total for line in self.order_line)

        if self.is_tax_8 and not self.is_tax_10:
            self.tax_custom = amount_untaxed * 0.08
        elif self.is_tax_10 and not self.is_tax_8:
            self.tax_custom = amount_untaxed * 0.10
        else:
            self.tax_custom = 0

    @api.depends('order_line.price_total', 'tax_custom')
    def _compute_total_price_custom(self):
        for rec in self:
            rec.total_price_custom = sum(line.price_total for line in rec.order_line) + rec.tax_custom
        # if self.is_tax_8 or self.is_tax_10:
        #     self.amount_total += self.tax_custom
        # else:
        #     self.amount_total = sum(line.price_total for line in self.order_line)
        # self.tax_totals['amount_untaxed'] = self.amount_total
        # self.tax_totals['amount_total'] = self.amount_total
        # self.tax_totals['amount_untaxed'] = self.amount_total

    @api.onchange('partner_id')
    def _onchange_partner_id_address(self):
        # for rec in self:
            self.address_new = self.partner_id.street

    @api.onchange('partner_id')
    def onchange1(self):
        self.partner_id = self.partner_id

    def _get_order_lines_to_report(self):
        down_payment_lines = self.order_line.filtered(lambda line:
                                                      line.is_downpayment
                                                      and not line.display_type
                                                      and not line._get_downpayment_state()
                                                      )

        def show_line(line):
            if not line.is_downpayment:
                return True
            elif line.display_type and down_payment_lines:
                return True  # Only show the down payment section if down payments were posted
            elif line in down_payment_lines:
                return True  # Only show posted down payments
            else:
                return False

        return self.order_line.filtered(show_line)

    def number_to_text(self, number):
        units = ["", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín"]
        scales = ["", "nghìn", "triệu", "tỷ", "nghìn tỷ", "triệu tỷ", "tỷ tỷ"]

        def read_three_digits(num, is_first_block=False):
            hundred = num // 100
            ten = (num % 100) // 10
            unit = num % 10
            result = ""

            # Chỉ thêm "không trăm" nếu không phải khối đầu tiên
            if hundred != 0:
                result += f"{units[hundred]} trăm"
                if ten == 0 and unit != 0:
                    result += " linh"
            elif not is_first_block and (ten != 0 or unit != 0):
                result += "không trăm"
                if ten == 0 and unit != 0:
                    result += " linh"

            if ten != 0 and ten != 1:
                result += f" {units[ten]} mươi"
                if unit == 1:
                    result += " mốt"
                elif unit == 5:
                    result += " lăm"
                elif unit != 0:
                    result += f" {units[unit]}"
            elif ten == 1:
                result += " mười"
                if unit == 5:
                    result += " lăm"
                elif unit != 0:
                    result += f" {units[unit]}"
            elif ten == 0 and unit != 0:
                result += f" {units[unit]}"
            return result.strip()

        if number == 0:
            return "không đồng"

        parts = []
        blocks = []
        while number > 0:
            blocks.insert(0, number % 1000)
            number //= 1000

        num_blocks = len(blocks)

        for idx, block in enumerate(blocks):
            if block != 0:
                is_first = (idx == 0)
                prefix = read_three_digits(block, is_first_block=is_first)
                scale = scales[num_blocks - idx - 1]
                if scale:
                    prefix += f" {scale}"
                parts.append(prefix)

        return " ".join(parts).strip() + " đồng"


class Sale_Order_Line(models.Model):
    _inherit = 'sale.order.line'

    specifications = fields.Selection(
        [('f1', 'Photo TĐ 1 mặt'), ('f2', 'Photo TĐ 2 mặt'), ('i1', 'In TĐ 1 mặt'), ('i2', 'In TĐ 2 mặt'),
         ('i3', 'In màu 1 mặt'), ('i4', 'In màu 2 mặt')], default='i3')

    paper_set = fields.Integer(string='Số Bộ', default='1', store=True)
    paper_qty = fields.Integer(string='Số tờ', default=1, store=True)
    remark = fields.Char(string='Diễn giải', store=True)
    unit_type = fields.Char('Đơn vị tính', related='product_template_id.unit_type')

    @api.onchange('paper_set', 'paper_qty')
    def onchange_qty(self):
        self.write({
            'product_uom_qty': self.paper_qty * self.paper_set
        })
