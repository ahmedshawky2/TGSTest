# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import xlrd
from io import StringIO
from io import BytesIO
import base64
import logging
_logger = logging.getLogger(__name__)


class saleAutomation(models.Model):
    _name = 'sale_automation_log'
    _description = "Sale Automation Log"
    _order = 'create_date desc'



    sale_automation = fields.Many2one(comodel_name="sale_automation", string="Sale Automation", store=True, required=True, index=True)

    status = fields.Selection([('New', 'New'), ('Success', 'Success'),('Error', 'Error')], string="Status", store=True,
                              required=False, index=True, track_visibility='onchange', default='New')

    customer_id = fields.Many2one(comodel_name="res.partner", string="Customer", store=True, required=False, index=True)

    product_id = fields.Many2one(comodel_name="product.product", string="Product", store=True, required=False, index=True)

    warehouse_id = fields.Many2one(comodel_name="stock.warehouse", string="Warehouse", store=True, required=False, index=True)

    product_qty = fields.Char(string="Product Qty", store=True, required=False, index=True)

    product_uom = fields.Many2one(comodel_name="uom.uom", string="Product UOM", store=True, required=False, index=True)

    product_unit_price = fields.Char(string="Product Unit Price", store=True, required=False, index=True)

    product_taxes = fields.Char(string="Product Taxes", store=True, required=False, index=True)

    product_desc = fields.Char(string="Product Description", store=True, required=False)

    sales_person = fields.Many2one(comodel_name="res.users", string="Sales Person", store=True, required=False, index=True)

    product_same_inv = fields.Char(string="Product Same Invoice", store=True, required=False, index=True)

    account_journal = fields.Char(string="Account Journal", store=True, required=False, index=True)

    payment_amount_money = fields.Char(string="Payment Amount Money", store=True, required=False, index=True)

    payment_amount_percent = fields.Char(string="Payment Amount Percent", store=True, required=False, index=True)

    payment_amount_final = fields.Char(string="Payment Amount Final", store=True, required=False, index=True)

    sale_order_id = fields.Many2one(comodel_name="sale.order", string="Sales Order", store=True, required=False, index=True)

    delivery_id = fields.Many2one(comodel_name="stock.picking", string="Delivery", store=True, required=False, index=True)

    inv_id = fields.Many2one(comodel_name="account.move", string="Invoice", store=True, required=False, index=True)

    error = fields.Text(string="Error", store=True, required=False)

    confirm_so = fields.Boolean(string="Confirm SO", store=True, index=True, track_visibility='onchange')

    validate_delivery = fields.Boolean(string="Validate Delivery", store=True, index=True, track_visibility='onchange')

    create_invoice = fields.Boolean(string="Create Invoice", store=True, index=True, track_visibility='onchange')

    post_invoice = fields.Boolean(string="Post Invoice", store=True, index=True, track_visibility='onchange')

    invoice_register_payment = fields.Boolean(string="Invoice Register Payment", store=True, index=True,
                                              track_visibility='onchange')

    date_submit = fields.Datetime(string='Submit Date', required=False, index=True, default=fields.Datetime.now,
                                  help="Bulk automation Date")

    x_external_order_id = fields.Char(string="External Order Id", store=True, required=False, index=True,
                                      track_visibility="onchange")


    def reRunSALog(self):

        try:
            if self.status == "Success":
                return False;


            saleOrderName = ""
            saleOrderDeliveryName = ""
            saleOrderDeliveryStatus = ""
            saleOrderDeliveryId = ""

            amountPaymentMoney = ""
            if self.payment_amount_money != False:
                amountPaymentMoney = self.payment_amount_money

            amountPaymentPercent = ""
            if self.payment_amount_percent != False:
                amountPaymentPercent = self.payment_amount_percent

            accountJournal = ""
            if self.account_journal != False:
                accountJournal = self.account_journal


            if self.confirm_so == True:
                saleOrderSearch = self.env['sale.order'].search([('id', '=', int(self.sale_order_id))])
                _logger.debug('saleOrderSearch minds ! "%s"' % (str(saleOrderSearch)))
                saleOrderName = saleOrderSearch[0]['name']

                if saleOrderSearch and saleOrderSearch[0]['state'] != "done" and saleOrderSearch[0]['state'] != "sale" and saleOrderSearch[0]['state'] != "cancel":
                    self.pool.get('sale.order').action_confirm(saleOrderSearch)
                    self.status = 'Success'

            if self.validate_delivery == True and saleOrderName != "":
                stockPickingSearch = self.env['stock.picking'].search([('origin', '=', saleOrderName)])
                _logger.debug('stockPickingSearch minds ! "%s"' % (str(stockPickingSearch)))
                saleOrderDeliveryName = stockPickingSearch[0]['name']
                saleOrderDeliveryStatus = stockPickingSearch[0]['state']
                saleOrderDeliveryId = stockPickingSearch[0]['id']
                stockPickingSearch[0]['scheduled_date'] = self.date_submit
                self.delivery_id = saleOrderDeliveryId
                self.status = 'Success'
                _logger.debug('saleOrderDeliveryStatus minds ! "%s"' % (str(saleOrderDeliveryStatus)))

                if saleOrderDeliveryStatus == "confirmed":
                    _logger.debug('stock.picking ==> action_assign start')
                    stockPickingSearch.action_assign()
                    _logger.debug('stock.picking ==> action_assign end')
                    self.status = 'Success'

                stockPickingSearch = self.env['stock.picking'].search([('origin', '=', saleOrderName)])
                _logger.debug('stockPickingSearch minds ! "%s"' % (str(stockPickingSearch)))
                saleOrderDeliveryName = stockPickingSearch[0]['name']
                saleOrderDeliveryStatus = stockPickingSearch[0]['state']
                saleOrderDeliveryId = stockPickingSearch[0]['id']
                self.delivery_id = saleOrderDeliveryId
                self.status = 'Success'
                _logger.debug('saleOrderDeliveryStatus minds ! "%s"' % (str(saleOrderDeliveryStatus)))

                if saleOrderDeliveryStatus != "cancel" and saleOrderDeliveryStatus != "done" and saleOrderDeliveryStatus != "confirmed":
                    stockMoveSearch = self.env['stock.move'].search([('picking_id', '=', saleOrderDeliveryId)])
                    _logger.debug('stockMoveSearch minds ! "%s"' % (str(stockMoveSearch)))

                    for stockMoveLine in stockMoveSearch:
                        _logger.debug('stockMoveLine minds ! "%s"' % (str(stockMoveLine)))

                        stockMoveLineSearch = self.env['stock.move.line'].search([('move_id', '=', stockMoveLine[0]['id'])])
                        _logger.debug('stockMoveLineSearch minds ! "%s"' % (str(stockMoveLineSearch)))

                        if stockMoveLineSearch:
                            stockMoveLineSearch[0]['state'] = 'assigned'
                            stockMoveLineSearch[0]['qty_done'] = stockMoveLineSearch[0]['product_uom_qty']
                            _logger.debug('stockMoveLineSearch minds ! "%s"' % (str(stockMoveLineSearch)))

                    _logger.debug('stock.picking ==> button_validate start')
                    stockPickingSearch.button_validate()
                    self.pool.get('stock.picking').button_validate(stockPickingSearch)
                    _logger.debug('stock.picking ==> button_validate end')
                    stockPickingSearch[0]['date_done'] = self.date_submit
                    self.status = 'Success'


            if self.create_invoice == True:
                _logger.debug('self.inv_id minds ! "%s"' % (str(int(self.inv_id))))
                if int(self.inv_id) != 0 and self.post_invoice == True:
                    accountInvoiceSearch = self.env['account.move'].search([('id', '=', int(self.inv_id))])
                    _logger.debug('accountInvoiceSearch minds ! "%s"' % (str(accountInvoiceSearch)))

                    accountJournalSearch = self.env['account.journal'].search([('name', '=', accountJournal)])
                    _logger.debug('accountInvoiceSearch minds ! "%s"' % (str(accountInvoiceSearch[0]['id'])))
                    invoiceIdLog = accountInvoiceSearch[0]['id']
                    totalInvAmountLog = accountInvoiceSearch[0]['amount_total']
                    accountInvoiceSearch[0]['invoice_date'] = self.date_submit
                    accountInvoiceSearch[0]['invoice_date_due'] = self.date_submit

                    if accountInvoiceSearch and accountInvoiceSearch['state'] == "draft":

                        _logger.debug('account.move ==> action_post start')
                        self.pool.get('account.move').action_post(accountInvoiceSearch)
                        _logger.debug('account.move ==> action_post end')
                        _logger.debug('accountJournal minds ! "%s"' % (str(accountJournalSearch)))
                        self.status = 'Success'

                    if self.invoice_register_payment == True and accountJournalSearch is not None and accountJournalSearch != "":
                        _logger.debug('account.payment ==> action_validate_invoice_payment start')

                        finalPaymentAmount = totalInvAmountLog
                        _logger.debug('finalPaymentAmount minds ! "%s"' % (str(finalPaymentAmount)))

                        if amountPaymentPercent is not None and amountPaymentPercent != "":
                            if 0 < float(amountPaymentPercent) < 1:
                                amountPaymentAfterApplyPercent = totalInvAmountLog * amountPaymentPercent
                                finalPaymentAmount = amountPaymentAfterApplyPercent
                                _logger.debug('finalPaymentAmount 0 < amountPaymentPercent < 1 minds ! "%s"' % (str(finalPaymentAmount)))
                            elif float(amountPaymentPercent) >= 1:
                                finalPaymentAmount = totalInvAmountLog
                                _logger.debug('finalPaymentAmount amountPaymentPercent >= 1 minds ! "%s"' % (str(finalPaymentAmount)))
                            else:
                                if float(amountPaymentMoney) >= float(totalInvAmountLog):
                                    finalPaymentAmount = totalInvAmountLog
                                    _logger.debug('finalPaymentAmount amountPaymentMoney >= totalInvAmountLog minds ! "%s"' % (str(finalPaymentAmount)))
                                elif float(amountPaymentMoney) < float(totalInvAmountLog):
                                    finalPaymentAmount = amountPaymentMoney
                                    _logger.debug('finalPaymentAmount amountPaymentMoney < totalInvAmountLog minds ! "%s"' % (str(finalPaymentAmount)))

                        else:
                            if amountPaymentMoney is not None and amountPaymentMoney != "":
                                if float(amountPaymentMoney) >= float(totalInvAmountLog):
                                    finalPaymentAmount = totalInvAmountLog
                                    _logger.debug('finalPaymentAmount else amountPaymentMoney >= totalInvAmountLog minds ! "%s"' % (str(finalPaymentAmount)))
                                elif float(amountPaymentMoney) < float(totalInvAmountLog):
                                    finalPaymentAmount = amountPaymentMoney
                                    _logger.debug('finalPaymentAmount else amountPaymentMoney < totalInvAmountLog minds ! "%s"' % (str(finalPaymentAmount)))

                        accountPayment = self.env['account.payment'].with_context(
                            active_ids=[accountInvoiceSearch[0]['id']],
                            active_id=accountInvoiceSearch[0]['id'],
                            invoice_ids=[accountInvoiceSearch[0]['id']]).create({
                            'payment_type': 'inbound',
                            'partner_type': 'customer',
                            'payment_method_id': 1,
                            'journal_id': accountJournalSearch[0]['id'],
                            'amount': finalPaymentAmount,
                        })
                        if accountPayment.payment_type == 'transfer':
                            sequence_code = 'account.payment.transfer'
                        else:
                            if accountPayment.partner_type == 'customer':
                                if accountPayment.payment_type == 'inbound':
                                    sequence_code = 'account.payment.customer.invoice'
                                if accountPayment.payment_type == 'outbound':
                                    sequence_code = 'account.payment.customer.refund'
                            if accountPayment.partner_type == 'supplier':
                                if accountPayment.payment_type == 'inbound':
                                    sequence_code = 'account.payment.supplier.refund'
                                if accountPayment.payment_type == 'outbound':
                                    sequence_code = 'account.payment.supplier.invoice'
                        accountPayment.name = self.env['ir.sequence'].with_context(
                            ir_sequence_date=accountPayment.payment_date).next_by_code(
                            sequence_code)
                        accountPayment.invoice_ids = [accountInvoiceSearch[0]['id']]
                        accountPayment.post()
                        _logger.debug('account.payment ==> action_validate_invoice_payment end')
                        self.status = 'Success'


                else:
                    _logger.debug('sale.advance.payment.inv ==> create_invoices start')
                    _logger.debug('int(self.sale_order_id) minds ! "%s"' % (str(int(self.sale_order_id))))
                    payment = self.env['sale.advance.payment.inv'].with_context(active_ids=[int(self.sale_order_id)]).create({'advance_payment_method': 'delivered'})
                    payment.create_invoices()
                    _logger.debug('sale.advance.payment.inv ==> create_invoices end')

                    if self.post_invoice == True:

                        accountInvoiceSearch = self.env['account.move'].search([('invoice_origin', '=', saleOrderName)])
                        _logger.debug('accountInvoiceSearch minds ! "%s"' % (str(accountInvoiceSearch)))
                        self.inv_id = accountInvoiceSearch[0]['id']

                        accountJournalSearch = self.env['account.journal'].search([('name', '=', accountJournal)])
                        _logger.debug('accountInvoiceSearch minds ! "%s"' % (str(accountInvoiceSearch[0]['id'])))
                        invoiceIdLog = accountInvoiceSearch[0]['id']
                        totalInvAmountLog = accountInvoiceSearch[0]['amount_total']
                        accountInvoiceSearch[0]['invoice_date'] = self.date_submit
                        accountInvoiceSearch[0]['invoice_date_due'] = self.date_submit

                        if accountInvoiceSearch and accountInvoiceSearch['state'] == "draft":

                            _logger.debug('account.move ==> action_post start')
                            self.pool.get('account.move').action_post(accountInvoiceSearch)
                            _logger.debug('account.move ==> action_post end')

                            _logger.debug('accountJournal minds ! "%s"' % (str(accountJournalSearch)))
                            self.status = 'Success'

                        if self.invoice_register_payment == True and accountJournalSearch is not None and accountJournalSearch != "":
                            _logger.debug('account.payment ==> action_validate_invoice_payment start')

                            finalPaymentAmount = totalInvAmountLog
                            _logger.debug('finalPaymentAmount minds ! "%s"' % (str(finalPaymentAmount)))

                            if amountPaymentPercent is not None and amountPaymentPercent != "":
                                if 0 < float(amountPaymentPercent) < 1:
                                    amountPaymentAfterApplyPercent = totalInvAmountLog * amountPaymentPercent
                                    finalPaymentAmount = amountPaymentAfterApplyPercent
                                    _logger.debug('finalPaymentAmount 0 < amountPaymentPercent < 1 minds ! "%s"' % (
                                        str(finalPaymentAmount)))
                                elif float(amountPaymentPercent) >= 1:
                                    finalPaymentAmount = totalInvAmountLog
                                    _logger.debug('finalPaymentAmount amountPaymentPercent >= 1 minds ! "%s"' % (str(finalPaymentAmount)))
                                else:
                                    if float(amountPaymentMoney) >= float(totalInvAmountLog):
                                        finalPaymentAmount = totalInvAmountLog
                                        _logger.debug('finalPaymentAmount amountPaymentMoney >= totalInvAmountLog minds ! "%s"' % (str(finalPaymentAmount)))
                                    elif float(amountPaymentMoney) < float(totalInvAmountLog):
                                        finalPaymentAmount = amountPaymentMoney
                                        _logger.debug('finalPaymentAmount amountPaymentMoney < totalInvAmountLog minds ! "%s"' % (str(finalPaymentAmount)))

                            else:
                                if amountPaymentMoney is not None and amountPaymentMoney != "":
                                    if float(amountPaymentMoney) >= float(totalInvAmountLog):
                                        finalPaymentAmount = totalInvAmountLog
                                        _logger.debug('finalPaymentAmount else amountPaymentMoney >= totalInvAmountLog minds ! "%s"' % (str(finalPaymentAmount)))
                                    elif float(amountPaymentMoney) < float(totalInvAmountLog):
                                        finalPaymentAmount = amountPaymentMoney
                                        _logger.debug('finalPaymentAmount else amountPaymentMoney < totalInvAmountLog minds ! "%s"' % (str(finalPaymentAmount)))

                            accountPayment = self.env['account.payment'].with_context(
                                active_ids=[accountInvoiceSearch[0]['id']],
                                active_id=accountInvoiceSearch[0]['id'],
                                invoice_ids=[accountInvoiceSearch[0]['id']]).create({
                                'payment_type': 'inbound',
                                'partner_type': 'customer',
                                'payment_method_id': 1,
                                'journal_id': accountJournalSearch[0]['id'],
                                'amount': finalPaymentAmount,
                            })
                            if accountPayment.payment_type == 'transfer':
                                sequence_code = 'account.payment.transfer'
                            else:
                                if accountPayment.partner_type == 'customer':
                                    if accountPayment.payment_type == 'inbound':
                                        sequence_code = 'account.payment.customer.invoice'
                                    if accountPayment.payment_type == 'outbound':
                                        sequence_code = 'account.payment.customer.refund'
                                if accountPayment.partner_type == 'supplier':
                                    if accountPayment.payment_type == 'inbound':
                                        sequence_code = 'account.payment.supplier.refund'
                                    if accountPayment.payment_type == 'outbound':
                                        sequence_code = 'account.payment.supplier.invoice'
                            accountPayment.name = self.env['ir.sequence'].with_context(
                                ir_sequence_date=accountPayment.payment_date).next_by_code(
                                sequence_code)
                            accountPayment.invoice_ids = [accountInvoiceSearch[0]['id']]
                            accountPayment.post()
                            _logger.debug('account.payment ==> action_validate_invoice_payment end')
                            self.status = 'Success'

        except Exception as e:
            _logger.debug(u'ERROR: {}'.format(e))
            self.status = 'Error'
            self.error = u'ERROR: {}'.format(e)