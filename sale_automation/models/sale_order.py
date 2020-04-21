# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import xlrd
from io import StringIO
from io import BytesIO
import base64
import logging
_logger = logging.getLogger(__name__)


class saleOrderExtension(models.Model):
    _inherit = "sale.order"

    x_external_order_id = fields.Char(string="External Order Id", store=True, required=False, index=True, track_visibility="onchange")


    _sql_constraints = [
        ('x_external_order_id_uniq', 'unique (x_external_order_id)',
         'External order id is already exists under an existing order. \nplease insert another external order id.')]