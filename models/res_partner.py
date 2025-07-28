from odoo import models, api


class Partner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        domain = args

        # Nếu có giá trị name được nhập, tìm kiếm theo tên và các trường khác (phone, mobile)
        if name:
            domain = [
                '|',
                ('name', operator, name),  # Tìm theo tên
                ('phone', operator, name)
            ] + args

        # Thực hiện tìm kiếm với điều kiện đã thiết lập
        partners = self.search(domain, limit=limit)

        # Trả về kết quả tìm kiếm
        return [(partner.id, partner.display_name) for partner in partners]

    def _compute_display_name(self):
        for rec in self:
            if self.env.context.get('show_phone'):
                if rec.phone:
                    rec.display_name = f"{rec.name} - {rec.phone}"
                else:
                    rec.display_name = rec.name

            else:
                if self._rec_name:
                    convert = self._fields[self._rec_name].convert_to_display_name
                    for record in self:
                        record.display_name = convert(record[self._rec_name], record)
                else:
                    for record in self:
                        record.display_name = f"{record._name},{record.id}"
