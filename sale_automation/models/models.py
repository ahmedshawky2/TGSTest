# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import xlrd
from io import StringIO
from io import BytesIO
import base64
import logging
_logger = logging.getLogger(__name__)