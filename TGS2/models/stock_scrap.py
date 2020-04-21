# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo import exceptions
from odoo.exceptions import ValidationError
import string


import logging
_logger = logging.getLogger(__name__)


class lov (models.Model):
    _inherit = 'stock.scrap'
    x_scrap_reason = fields.Selection([('Reason1', 'Reason1'),('Reason2','Reason2')], string='Scrap Reason')
   