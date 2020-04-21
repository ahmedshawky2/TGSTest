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
    _name = 'sale_automation'
    _description = "Sale Automation"
    _order = 'create_date desc'



    name = fields.Char(string="Name", store=True, required=True, index=True, track_visibility='onchange'
                       #,default=lambda self: self.env['ir.sequence'].next_by_code('sale_automation_name')
                       )

    status = fields.Selection([('New', 'New'), ('Success', 'Success'), ('Partial Success', 'Partial Success'),
                               ('Error', 'Error')], string="Status", store=True,
                              required=False, index=True, track_visibility='onchange', default='New')

    no_initial_rec = fields.Char(string="Number Of Records", store=True, index=True, track_visibility='onchange')

    no_success_rec = fields.Char(string="Number Of Success Orders", store=True, index=True, track_visibility='onchange')

    excel_file = fields.Binary(string='File for upload')

    confirm_so = fields.Boolean(string="Confirm SO", store=True, index=True,track_visibility='onchange')

    validate_delivery = fields.Boolean(string="Validate Delivery", store=True, index=True,track_visibility='onchange')

    create_invoice = fields.Boolean(string="Create Invoice", store=True, index=True,track_visibility='onchange')

    post_invoice = fields.Boolean(string="Post Invoice", store=True, index=True,track_visibility='onchange')

    invoice_register_payment = fields.Boolean(string="Invoice Register Payment", store=True, index=True,track_visibility='onchange')

    error = fields.Text(string="Error", store=True, required=False)

    sale_automation_log_count = fields.Integer("Orders", compute='_compute_sale_automation_logs_count')

    sale_automation_log_money_total = fields.Char("Total", compute='_compute_sale_automation_logs_money_total')

    date_submit = fields.Datetime(string='Submit Date', required=True, index=True, default=fields.Datetime.now, help="Bulk automation Date")

    def _compute_sale_automation_logs_count(self):
        for elem in self:
            elem.sale_automation_log_count = self.env['sale_automation_log'].search_count([('sale_automation', '=', elem.id)])

    def _compute_sale_automation_logs_money_total(self):
        for elem in self:
            total = 0.0
            sale_automation_log_money_total_rec = self.env['sale_automation_log'].search([('sale_automation', '=', elem.id)])
            _logger.info('sale_automation_log_money_total_rec minds ! "%s"' % (str(sale_automation_log_money_total_rec)))
            for rec in sale_automation_log_money_total_rec:
                total = total + float(rec[0]['payment_amount_final'])
                _logger.info('total minds ! "%s"' % (str(total)))
            _logger.info('sale_automation_log_money_total minds ! "%s"' % (str(total)))
            elem.sale_automation_log_money_total = str(total)


    def action_sale_automation_log_tree_view(self):
        action = self.env.ref('sale_automation.sale_automation_log_ACTION').read()[0]
        action['domain'] = [('sale_automation', '=', self.id)]
        return action

    @api.model
    def create(self, vals):

        vals['name'] = self.env['ir.sequence'].next_by_code('sale_automation_name')
        result = super(saleAutomation, self).create(vals)
        return result


    def testSA(self):

        inputx = BytesIO()
        _logger.info('inputx minds ! "%s"' % (str("inputx")))
        inputx.write(base64.decodestring(self.excel_file))
        book = xlrd.open_workbook(file_contents=inputx.getvalue())
        _logger.info('book minds ! "%s"' % (str(book)))

        # sheet = book.sheets()[0]
        sheet = book.sheet_by_index(0)
        _logger.info('sheet minds ! "%s"' % (str(sheet)))

        sameInvoice = None
        lastOrderCheck = None
        finalRes = "Please remove the below orders from the excel file: \n\n"
        finalResCount = 0
        duplicated = "External order id is duplicated in the excel file as below: \n\n"
        duplicatedCount = 0
        all = ""

        for row_no in range(sheet.nrows):
            if row_no > 0:

                for col in range(sheet.ncols):

                    if col == 0:
                        _logger.info('Cell sameInvoice ! "%s"' % ("Row: " + str(row_no) + "   Col: " + str(col) + "   Cell Data: " + str(sheet.cell(row_no, col).value)))
                        sameInvoice = str(int(sheet.cell(row_no, col).value))


                if sameInvoice != lastOrderCheck:
                    saleOrderSearch = self.env['sale.order'].search([('x_external_order_id', '=', sameInvoice)])
                    _logger.info('saleOrderSearch minds ! "%s"' % (str(saleOrderSearch)))

                    if saleOrderSearch:
                        finalRes = finalRes + "External order id: " + sameInvoice + " is assigned to Order: " + saleOrderSearch[0]['name'] + "\n"
                        finalResCount = finalResCount + 1

                    if sameInvoice in all:
                        duplicated = duplicated + "External order id: " + sameInvoice + "\n"
                        duplicatedCount = duplicatedCount + 1

                    all = all + sameInvoice

                lastOrderCheck = sameInvoice

        if finalResCount > 0:
            raise ValidationError(finalRes)
        elif duplicatedCount > 0:
            raise ValidationError(duplicated)
        else:
            raise ValidationError("Tested successfully ...")


    def runSA(self):

        try:

            inputx = BytesIO()
            _logger.info('inputx minds ! "%s"' % (str("inputx")))
            inputx.write(base64.decodestring(self.excel_file))
            book = xlrd.open_workbook(file_contents=inputx.getvalue())
            _logger.info('book minds ! "%s"' % (str(book)))

            # sheet = book.sheets()[0]
            sheet = book.sheet_by_index(0)
            _logger.info('sheet minds ! "%s"' % (str(sheet)))

            customerName = None
            customerExternalId = None
            customerMobile = None
            customerEmail = None
            warehouseName = None
            unitOfMeasure = None
            customerId = None
            product = None
            productId = None
            productProductId = None
            productUnitPrice = None
            productDesc = None
            qty = None
            unitPrice = None
            taxes = None
            desc = None
            salesPerson = None
            salesPersonUserId = None
            salesPersonPartnerId = None
            sameInvoice = None

            lastOrderCheck = None
            createdOrderId = None

            saleOrderLineCreatedId = None

            saleOrderName = None
            saleOrderDeliveryName = None
            saleOrderDeliveryId = None

            deliveryIdLog = None
            invoiceIdLog = None
            saleOrderIdLog = None
            saleAutomationIdLog = self.id

            totalInvAmountLog = None
            amountPaymentMoney = None
            amountPaymentPercent = None
            amountPaymentAfterApplyPercent = None
            accountJournal = None

            finalPaymentAmount = None

            productEmptyError = None


            no_succ_rec = 0

            checkPartialSuccess = False

            if self.invoice_register_payment == True:
                self.confirm_so = True
                self.validate_delivery = True
                self.create_invoice = True
                self.post_invoice = True

            if self.post_invoice == True:
                self.confirm_so = True
                self.validate_delivery = True
                self.create_invoice = True

            if self.create_invoice == True:
                self.confirm_so = True
                self.validate_delivery = True

            if self.validate_delivery == True:
                self.confirm_so = True



            confirm_so = self.confirm_so
            validate_delivery = self.validate_delivery
            create_invoice = self.create_invoice
            invoice_register_payment = self.invoice_register_payment
            post_invoice = self.post_invoice

            product_uom = None
            product_uom_id = None
            warehouseId = None

            self.no_initial_rec = sheet.nrows

            date_submit = self.date_submit

            for row_no in range(sheet.nrows):
                if row_no > 0:
                    deliveryIdLog = None
                    invoiceIdLog = None
                    try:
                        for col in range(sheet.ncols):

                            if col == 0:
                                _logger.info('Cell sameInvoice ! "%s"' % ("Row: " + str(row_no) + "   Col: " + str(col) + "   Cell Data: " + str(sheet.cell(row_no, col).value)))
                                sameInvoice = str(int(sheet.cell(row_no, col).value))

                            elif col == 1:
                                _logger.info('Cell customerExternalId ! "%s"' % (
                                            "Row: " + str(row_no) + "   Col: " + str(col) + "   Cell Data: " + str(sheet.cell(row_no, col).value)))

                                customerExternalId = str(int(sheet.cell(row_no, col).value))

                                if customerExternalId is None or customerExternalId == "":
                                    saleOrderIdLog = None
                                    raise ValidationError("Customer external id is empty for Row: " + str(row_no) + " & Column: " + str(col))

                                customer = self.env['res.partner'].search([('ref', '=', customerExternalId)])
                                _logger.info('customerId minds ! "%s"' % (str(customer)))

                                if customer:
                                    customerId = customer[0]['id']
                                    customerName = customer[0]['name']
                                    customerEmail = customer[0]['email']
                                    customerMobile = customer[0]['mobile']
                                else:
                                    saleOrderIdLog = None
                                    raise ValidationError("Customer external id: " + customerExternalId + " is not found for Row: " + str(row_no) + " & Column: " + str(col))

                            elif col == 5:
                                _logger.info('Cell product ! "%s"' % (
                                        "Row: " + str(row_no) + "   Col: " + str(col) + "   Cell Data: " + str(sheet.cell(row_no, col).value)))

                                product = str(sheet.cell(row_no, col).value)

                                productProduct = self.env['product.product'].search([('default_code', '=', product)])

                                if productProduct:
                                    productProductId = productProduct[0]['id']
                                    _logger.info('productProductId minds ! "%s"' % (str(productProductId)))

                                    productUnitPrice = productProduct[0]['list_price']
                                    _logger.info('productUnitPrice minds ! "%s"' % (str(productUnitPrice)))
                                    productDesc = productProduct[0]['display_name']
                                    _logger.info('productDesc minds ! "%s"' % (str(productDesc)))

                                else:
                                    saleOrderIdLog = None
                                    raise ValidationError("Product is empty or wrong for Row: " + str(row_no) + " & Column: " + str(col))


                            elif col == 6:
                                _logger.info('Cell qty ! "%s"' % ("Row: " + str(row_no) + "   Col: " + str(col) + "   Cell Data: " + str(
                                    sheet.cell(row_no, col).value)))
                                qty = str(sheet.cell(row_no, col).value)

                            elif col == 7:
                                _logger.info('Cell UOM ! "%s"' % ("Row: " + str(row_no) + "   Col: " + str(col) + "   Cell Data: " + str(
                                    sheet.cell(row_no, col).value)))

                                unitOfMeasure = str(sheet.cell(row_no, col).value)

                                if unitOfMeasure is None or unitOfMeasure == "":
                                    unitOfMeasure = "Units"

                                product_uom = self.env['uom.uom'].search([('name', '=', unitOfMeasure)])
                                _logger.info('product_uom minds ! "%s"' % (str(product_uom)))
                                if product_uom:
                                    product_uom_id = int(product_uom[0]['id'])
                                    _logger.info('product_uom_id minds ! "%s"' % (str(product_uom_id)))
                                else:
                                    saleOrderIdLog = None
                                    raise ValidationError("UOM: " + unitOfMeasure + " for Row: " + str(row_no) + " & Column: " + str(col))


                            elif col == 8:
                                _logger.info('Cell unitPrice ! "%s"' % ("Row: " + str(row_no) + "   Col: " + str(col) + "   Cell Data: " + str(
                                    sheet.cell(row_no, col).value)))
                                unitPrice = str(sheet.cell(row_no, col).value)

                                if unitPrice is None or unitPrice == "":
                                    unitPrice = productUnitPrice


                            elif col == 9:
                                _logger.info('Cell taxes ! "%s"' % ("Row: " + str(row_no) + "   Col: " + str(col) + "   Cell Data: " + str(sheet.cell(row_no, col).value)))
                                taxes = str(sheet.cell(row_no, col).value)

                                if taxes is not None and taxes != "":
                                    taxes = int(float(taxes))
                                    _logger.info('taxes minds ! "%s"' % (str(taxes)))

                            elif col == 10:
                                _logger.info('Cell desc ! "%s"' % ("Row: " + str(row_no) + "   Col: " + str(col) + "   Cell Data: " + str(sheet.cell(row_no, col).value)))
                                desc = str(sheet.cell(row_no, col).value)

                                if desc is None or desc == "":
                                    desc = productDesc

                            elif col == 11:
                                _logger.info('Cell Warehouse ! "%s"' % ("Row: " + str(row_no) + "   Col: " + str(col) + "   Cell Data: " + str(sheet.cell(row_no, col).value)))
                                warehouseName = str(sheet.cell(row_no, col).value)

                                if warehouseName is not None or warehouseName != "":
                                    warehouse = self.env['stock.warehouse'].search([('name', '=', warehouseName)])
                                    _logger.info('warehouse minds ! "%s"' % (str(warehouse)))
                                    if warehouse:
                                        warehouseId = int(warehouse[0]['id'])
                                        _logger.info('warehouseId minds ! "%s"' % (str(warehouseId)))
                                    else:
                                        saleOrderIdLog = None
                                        raise ValidationError("warehouse Name: " + warehouseName + " is not found for Row: " + str(row_no) + " & Column: " + str(col))
                                else:
                                    saleOrderIdLog = None
                                    raise ValidationError("Warehouse is empty for Row: " + str(row_no) + " & Column: " + str(col))

                            elif col == 12:
                                _logger.info('Cell salesPerson ! "%s"' % ("Row: " + str(row_no) + "   Col: " + str(col) + "   Cell Data: " + str(sheet.cell(row_no, col).value)))
                                salesPerson = str(sheet.cell(row_no, col).value)

                                if salesPerson is not None and salesPerson != "":
                                    salesPersonPartner = self.env['res.partner'].search([('name', '=', salesPerson)])

                                    if salesPersonPartner:
                                        salesPersonPartnerId = salesPersonPartner[0]['id']
                                        salesPersonUser = self.env['res.users'].search([('partner_id', '=', salesPersonPartnerId)])

                                        if salesPersonUser:
                                            salesPersonUserId = salesPersonUser[0]['id']

                            elif col == 13:
                                _logger.info('Cell accountJournal ! "%s"' % ("Row: " + str(row_no) + "   Col: " + str(col) + "   Cell Data: " + str(sheet.cell(row_no, col).value)))
                                accountJournal = str(sheet.cell(row_no, col).value)

                            elif col == 14:
                                _logger.info('Cell amountPaymentMoney ! "%s"' % (
                                        "Row: " + str(row_no) + "   Col: " + str(col) + "   Cell Data: " + str(sheet.cell(row_no, col).value)))
                                amountPaymentMoney = str(sheet.cell(row_no, col).value)

                            elif col == 15:
                                _logger.info('Cell amountPaymentMoney ! "%s"' % (
                                        "Row: " + str(row_no) + "   Col: " + str(col) + "   Cell Data: " + str(sheet.cell(row_no, col).value)))
                                amountPaymentPercent = str(sheet.cell(row_no, col).value)


                        if sameInvoice != lastOrderCheck:
                            saleOrder = self.env['sale.order'].create({
                                'partner_id': customerId,
                                'user_id': salesPersonUserId,
                                'date_order': date_submit,
                                'x_external_order_id': str(sameInvoice),
                                'warehouse_id': warehouseId,
                            })

                            createdOrderId = int(saleOrder)
                            saleOrderIdLog = int(saleOrder)
                            _logger.info('createdOrderId minds ! "%s"' % (str(createdOrderId)))

                        lastOrderCheck = sameInvoice

                        saleOrderLine = self.env['sale.order.line'].create({
                            'product_uom': product_uom_id,
                            'product_uom_qty': qty,
                            'order_partner_id': customerId,
                            'product_id': productProductId,
                            'order_id': createdOrderId,
                            'price_unit': unitPrice,
                            'name': desc,
                            # 'tax_id': taxes,
                        })

                        saleOrderLineCreatedId = int(saleOrderLine)
                        _logger.info('saleOrderLineCreatedId minds ! "%s"' % (str(saleOrderLineCreatedId)))

                        # _logger.info('row_no+1 minds ! "%s"' % (str(row_no+1)))
                        # _logger.info('sheet.nrows minds ! "%s"' % (str(sheet.nrows)))
                        # _logger.info('str(sheet.cell(row_no+1, 0).value) minds ! "%s"' % (str(sheet.cell(row_no+1, 0).value)))
                        # _logger.info('lastOrderCheck minds ! "%s"' % (str(lastOrderCheck)))
                        if row_no + 1 < sheet.nrows and str(int(sheet.cell(row_no + 1, 0).value)) != lastOrderCheck:
                            saleOrderSearch = self.env['sale.order'].search([('id', '=', createdOrderId)])
                            _logger.info('saleOrderSearch minds ! "%s"' % (str(saleOrderSearch)))
                            if saleOrderSearch and confirm_so == True:
                                self.pool.get('sale.order').action_confirm(saleOrderSearch)

                                saleOrderName = saleOrderSearch[0]['name']
                                _logger.info('saleOrderName minds ! "%s"' % (str(saleOrderName)))

                                saleOrderSearch[0]['date_order'] = date_submit

                                if saleOrderName is not None and saleOrderName != "":
                                    stockPickingSearch = self.env['stock.picking'].search(
                                        [('origin', '=', saleOrderName)])
                                    _logger.info('stockPickingSearch minds ! "%s"' % (str(stockPickingSearch)))

                                    if stockPickingSearch:
                                        saleOrderDeliveryName = stockPickingSearch[0]['name']
                                        _logger.info(
                                            'saleOrderDeliveryName minds ! "%s"' % (str(saleOrderDeliveryName)))

                                        if saleOrderDeliveryName is not None and saleOrderDeliveryName != "" and validate_delivery == True:
                                            saleOrderDeliveryId = stockPickingSearch[0]['id']
                                            deliveryIdLog = stockPickingSearch[0]['id']

                                            stockPickingSearch[0]['scheduled_date'] = date_submit

                                            _logger.info(
                                                'saleOrderDeliveryId minds ! "%s"' % (str(saleOrderDeliveryId)))

                                            stockMoveSearch = self.env['stock.move'].search(
                                                [('picking_id', '=', saleOrderDeliveryId)])
                                            _logger.info('stockMoveSearch minds ! "%s"' % (str(stockMoveSearch)))

                                            for stockMoveLine in stockMoveSearch:
                                                _logger.info('stockMoveLine minds ! "%s"' % (str(stockMoveLine)))

                                                stockMoveLineSearch = self.env['stock.move.line'].search(
                                                    [('move_id', '=', stockMoveLine[0]['id'])])
                                                _logger.info(
                                                    'stockMoveLineSearch minds ! "%s"' % (str(stockMoveLineSearch)))

                                                if stockMoveLineSearch:
                                                    stockMoveLineSearch[0]['state'] = 'assigned'
                                                    stockMoveLineSearch[0]['qty_done'] = stockMoveLineSearch[0][
                                                        'product_uom_qty']

                                            _logger.info('stock.picking ==> button_validate start')
                                            self.pool.get('stock.picking').button_validate(stockPickingSearch)
                                            _logger.info('stock.picking ==> button_validate end')

                                            stockPickingSearch[0]['date_done'] = date_submit

                                            if create_invoice == True:
                                                _logger.info('sale.advance.payment.inv ==> create_invoices start')
                                                # self.pool.get('sale.advance.payment.inv').create_invoices(saleOrderSearch)
                                                payment = self.env['sale.advance.payment.inv'].with_context(
                                                    active_ids=[createdOrderId]).create({
                                                    'advance_payment_method': 'delivered'
                                                })
                                                payment.create_invoices()
                                                _logger.info('sale.advance.payment.inv ==> create_invoices end')

                                                accountInvoiceSearch = self.env['account.move'].search(
                                                    [('invoice_origin', '=', saleOrderName)])
                                                _logger.info(
                                                    'accountInvoiceSearch minds ! "%s"' % (str(accountInvoiceSearch)))

                                                if accountInvoiceSearch:
                                                    _logger.info('accountInvoiceSearch minds ! "%s"' % (
                                                        str(accountInvoiceSearch[0]['id'])))

                                                    invoiceIdLog = accountInvoiceSearch[0]['id']
                                                    totalInvAmountLog = accountInvoiceSearch[0]['amount_total']
                                                    accountInvoiceSearch[0]['invoice_date'] = date_submit
                                                    accountInvoiceSearch[0]['invoice_date_due'] = date_submit
                                                    if post_invoice == True:
                                                        _logger.info('account.move ==> action_post start')
                                                        self.pool.get('account.move').action_post(
                                                            accountInvoiceSearch)
                                                        _logger.info('account.move ==> action_post end')

                                                        accountJournalSearch = self.env['account.journal'].search(
                                                            [('name', '=', accountJournal)])
                                                        _logger.info('accountJournal minds ! "%s"' % (str(accountJournalSearch)))


                                                        if invoice_register_payment == True and accountJournalSearch is not None and accountJournalSearch != "":
                                                            _logger.info(
                                                                'account.payment ==> action_validate_invoice_payment start')
                                                            # accountInvoiceSearch.invoice_ids = [accountInvoiceSearch[0]['id']]
                                                            # self.pool.get('account.payment').action_validate_invoice_payment(invoice_ids=[accountInvoiceSearch[0]['id']])

                                                            finalPaymentAmount = totalInvAmountLog

                                                            if amountPaymentPercent is not None and amountPaymentPercent != "":
                                                                if 0 < float(amountPaymentPercent) < 1:
                                                                    amountPaymentAfterApplyPercent = totalInvAmountLog * amountPaymentPercent
                                                                    finalPaymentAmount = amountPaymentAfterApplyPercent
                                                                    _logger.info('finalPaymentAmount 0 < amountPaymentPercent < 1 minds ! "%s"' % (str(finalPaymentAmount)))
                                                                elif float(amountPaymentPercent) >= 1:
                                                                    finalPaymentAmount = totalInvAmountLog
                                                                    _logger.info(
                                                                        'finalPaymentAmount amountPaymentPercent >= 1 minds ! "%s"' % (
                                                                            str(finalPaymentAmount)))
                                                                else:
                                                                    if float(amountPaymentMoney) >= float(totalInvAmountLog):
                                                                        finalPaymentAmount = totalInvAmountLog
                                                                        _logger.info(
                                                                            'finalPaymentAmount amountPaymentMoney >= totalInvAmountLog minds ! "%s"' % (
                                                                                str(finalPaymentAmount)))
                                                                    elif float(amountPaymentMoney) < float(totalInvAmountLog):
                                                                        finalPaymentAmount = amountPaymentMoney
                                                                        _logger.info(
                                                                            'finalPaymentAmount amountPaymentMoney < totalInvAmountLog minds ! "%s"' % (
                                                                                str(finalPaymentAmount)))

                                                            else:
                                                                if amountPaymentMoney is not None and amountPaymentMoney != "":
                                                                    if float(amountPaymentMoney) >= float(totalInvAmountLog):
                                                                        finalPaymentAmount = totalInvAmountLog
                                                                        _logger.info(
                                                                            'finalPaymentAmount else amountPaymentMoney >= totalInvAmountLog minds ! "%s"' % (
                                                                                str(finalPaymentAmount)))
                                                                    elif float(amountPaymentMoney) < float(totalInvAmountLog):
                                                                        finalPaymentAmount = amountPaymentMoney
                                                                        _logger.info(
                                                                            'finalPaymentAmount else amountPaymentMoney < totalInvAmountLog minds ! "%s"' % (
                                                                                str(finalPaymentAmount)))


                                                            accountPayment = self.env['account.payment'].with_context(
                                                                active_ids=[accountInvoiceSearch[0]['id']],
                                                                active_id=accountInvoiceSearch[0]['id'],
                                                                invoice_ids=[accountInvoiceSearch[0]['id']]).create({
                                                                'payment_type': 'inbound',
                                                                'partner_type': 'customer',
                                                                'payment_method_id': 1,
                                                                'journal_id': accountJournalSearch[0]['id'],
                                                                #'amount': accountInvoiceSearch[0]['amount_total'],
                                                                'amount': finalPaymentAmount,
                                                            })
                                                            # inv = dict({"invoice_ids":accountInvoiceSearch[0]['id']})
                                                            # _logger.info('inv minds ! "%s"' % (str(inv.invoice_ids)))
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
                                                            # self.pool.get('account.payment').action_validate_invoice_payment(
                                                            # self.env['account.payment'].search([('id', '=', int(accountPayment))]))
                                                            _logger.info('account.payment ==> action_validate_invoice_payment end')

                            no_succ_rec = no_succ_rec + 1

                            saleAutomationId = self.env['sale_automation_log'].create({
                                'sale_automation': saleAutomationIdLog,
                                'product_qty': qty,
                                'customer_id': customerId,
                                'product_id': productProductId,
                                'sale_order_id': saleOrderIdLog,
                                'product_unit_price': unitPrice,
                                'product_desc': desc,
                                'product_taxes': taxes,
                                'sales_person': salesPersonUserId,
                                'product_same_inv': sameInvoice,
                                'delivery_id': deliveryIdLog,
                                'inv_id': invoiceIdLog,
                                'confirm_so': confirm_so,
                                'validate_delivery': validate_delivery,
                                'create_invoice': create_invoice,
                                'post_invoice': post_invoice,
                                'invoice_register_payment': invoice_register_payment,
                                'account_journal': accountJournal,
                                'payment_amount_money': amountPaymentMoney,
                                'payment_amount_percent': amountPaymentPercent,
                                'payment_amount_final': finalPaymentAmount,
                                'status': 'Success',
                                'date_submit': date_submit,
                                'x_external_order_id': str(sameInvoice),
                                'warehouse_id': warehouseId,
                                'product_uom': product_uom_id,
                            })


                        if row_no + 1 == sheet.nrows:
                            saleOrderSearch = self.env['sale.order'].search([('id', '=', createdOrderId)])
                            _logger.info('saleOrderSearch minds ! "%s"' % (str(saleOrderSearch)))
                            if saleOrderSearch and confirm_so == True:
                                self.pool.get('sale.order').action_confirm(saleOrderSearch)

                                saleOrderName = saleOrderSearch[0]['name']
                                _logger.info('saleOrderName minds ! "%s"' % (str(saleOrderName)))

                                saleOrderSearch[0]['date_order'] = date_submit

                                if saleOrderName is not None and saleOrderName != "":
                                    stockPickingSearch = self.env['stock.picking'].search(
                                        [('origin', '=', saleOrderName)])
                                    _logger.info('stockPickingSearch minds ! "%s"' % (str(stockPickingSearch)))

                                    if stockPickingSearch:
                                        saleOrderDeliveryName = stockPickingSearch[0]['name']
                                        _logger.info(
                                            'saleOrderDeliveryName minds ! "%s"' % (str(saleOrderDeliveryName)))

                                        if saleOrderDeliveryName is not None and saleOrderDeliveryName != "" and validate_delivery == True:
                                            saleOrderDeliveryId = stockPickingSearch[0]['id']
                                            deliveryIdLog = stockPickingSearch[0]['id']
                                            stockPickingSearch[0]['scheduled_date'] = date_submit
                                            _logger.info(
                                                'saleOrderDeliveryId minds ! "%s"' % (str(saleOrderDeliveryId)))

                                            stockMoveSearch = self.env['stock.move'].search(
                                                [('picking_id', '=', saleOrderDeliveryId)])
                                            _logger.info('stockMoveSearch minds ! "%s"' % (str(stockMoveSearch)))

                                            for stockMoveLine in stockMoveSearch:
                                                _logger.info('stockMoveLine minds ! "%s"' % (str(stockMoveLine)))

                                                stockMoveLineSearch = self.env['stock.move.line'].search(
                                                    [('move_id', '=', stockMoveLine[0]['id'])])
                                                _logger.info(
                                                    'stockMoveLineSearch minds ! "%s"' % (str(stockMoveLineSearch)))

                                                if stockMoveLineSearch:
                                                    stockMoveLineSearch[0]['state'] = 'assigned'
                                                    stockMoveLineSearch[0]['qty_done'] = stockMoveLineSearch[0][
                                                        'product_uom_qty']

                                            _logger.info('stock.picking ==> button_validate start')
                                            self.pool.get('stock.picking').button_validate(stockPickingSearch)
                                            _logger.info('stock.picking ==> button_validate end')

                                            stockPickingSearch[0]['date_done'] = date_submit

                                            if create_invoice == True:
                                                _logger.info('sale.advance.payment.inv ==> create_invoices start')
                                                # self.pool.get('sale.advance.payment.inv').create_invoices(saleOrderSearch)
                                                payment = self.env['sale.advance.payment.inv'].with_context(
                                                    active_ids=[createdOrderId]).create({
                                                    'advance_payment_method': 'delivered'
                                                })
                                                payment.create_invoices()
                                                _logger.info('sale.advance.payment.inv ==> create_invoices end')

                                                accountInvoiceSearch = self.env['account.move'].search(
                                                    [('invoice_origin', '=', saleOrderName)])
                                                _logger.info(
                                                    'accountInvoiceSearch minds ! "%s"' % (str(accountInvoiceSearch)))

                                                if accountInvoiceSearch:
                                                    _logger.info('accountInvoiceSearch minds ! "%s"' % (
                                                        str(accountInvoiceSearch[0]['id'])))

                                                    invoiceIdLog = accountInvoiceSearch[0]['id']
                                                    totalInvAmountLog = accountInvoiceSearch[0]['amount_total']
                                                    accountInvoiceSearch[0]['invoice_date'] = date_submit
                                                    accountInvoiceSearch[0]['invoice_date_due'] = date_submit
                                                    if post_invoice == True:
                                                        _logger.info('account.move ==> action_post start')
                                                        self.pool.get('account.move').action_post(
                                                            accountInvoiceSearch)
                                                        _logger.info('account.move ==> action_post end')

                                                        accountJournalSearch = self.env['account.journal'].search(
                                                            [('name', '=', accountJournal)])
                                                        _logger.info(
                                                            'accountJournal minds ! "%s"' % (str(accountJournalSearch)))

                                                        if invoice_register_payment == True and accountJournalSearch is not None and accountJournalSearch != "":
                                                            _logger.info(
                                                                'account.payment ==> action_validate_invoice_payment start')
                                                            # accountInvoiceSearch.invoice_ids = [accountInvoiceSearch[0]['id']]
                                                            # self.pool.get('account.payment').action_validate_invoice_payment(invoice_ids=[accountInvoiceSearch[0]['id']])

                                                            finalPaymentAmount = totalInvAmountLog

                                                            if amountPaymentPercent is not None and amountPaymentPercent != "":
                                                                if 0 < float(amountPaymentPercent) < 1:
                                                                    amountPaymentAfterApplyPercent = totalInvAmountLog * amountPaymentPercent
                                                                    finalPaymentAmount = amountPaymentAfterApplyPercent
                                                                    _logger.info(
                                                                        'finalPaymentAmount 0 < amountPaymentPercent < 1 minds ! "%s"' % (
                                                                            str(finalPaymentAmount)))
                                                                elif float(amountPaymentPercent) >= 1:
                                                                    finalPaymentAmount = totalInvAmountLog
                                                                    _logger.info(
                                                                        'finalPaymentAmount amountPaymentPercent >= 1 minds ! "%s"' % (
                                                                            str(finalPaymentAmount)))
                                                                else:
                                                                    if float(amountPaymentMoney) >= float(totalInvAmountLog):
                                                                        finalPaymentAmount = totalInvAmountLog
                                                                        _logger.info(
                                                                            'finalPaymentAmount amountPaymentMoney >= totalInvAmountLog minds ! "%s"' % (
                                                                                str(finalPaymentAmount)))
                                                                    elif float(amountPaymentMoney) < float(totalInvAmountLog):
                                                                        finalPaymentAmount = amountPaymentMoney
                                                                        _logger.info(
                                                                            'finalPaymentAmount amountPaymentMoney < totalInvAmountLog minds ! "%s"' % (
                                                                                str(finalPaymentAmount)))

                                                            else:
                                                                if amountPaymentMoney is not None and amountPaymentMoney != "":
                                                                    if float(amountPaymentMoney) >= float(totalInvAmountLog):
                                                                        finalPaymentAmount = totalInvAmountLog
                                                                        _logger.info(
                                                                            'finalPaymentAmount else amountPaymentMoney >= totalInvAmountLog minds ! "%s"' % (
                                                                                str(finalPaymentAmount)))
                                                                    elif float(amountPaymentMoney) < float(totalInvAmountLog):
                                                                        finalPaymentAmount = amountPaymentMoney
                                                                        _logger.info(
                                                                            'finalPaymentAmount else amountPaymentMoney < totalInvAmountLog minds ! "%s"' % (
                                                                                str(finalPaymentAmount)))

                                                            accountPayment = self.env['account.payment'].with_context(
                                                                active_ids=[accountInvoiceSearch[0]['id']],
                                                                active_id=accountInvoiceSearch[0]['id'],
                                                                invoice_ids=[accountInvoiceSearch[0]['id']]).create({
                                                                'payment_type': 'inbound',
                                                                'partner_type': 'customer',
                                                                'payment_method_id': 1,
                                                                'journal_id': accountJournalSearch[0]['id'],
                                                                # 'amount': accountInvoiceSearch[0]['amount_total'],
                                                                'amount': finalPaymentAmount,
                                                            })
                                                            # inv = dict({"invoice_ids":accountInvoiceSearch[0]['id']})
                                                            # _logger.info('inv minds ! "%s"' % (str(inv.invoice_ids)))
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
                                                            # self.pool.get('account.payment').action_validate_invoice_payment(
                                                            # self.env['account.payment'].search([('id', '=', int(accountPayment))]))
                                                            _logger.info(
                                                                'account.payment ==> action_validate_invoice_payment end')

                            no_succ_rec = no_succ_rec + 1

                            saleAutomationId = self.env['sale_automation_log'].create({
                                'sale_automation': saleAutomationIdLog,
                                'product_qty': qty,
                                'customer_id': customerId,
                                'product_id': productProductId,
                                'sale_order_id': saleOrderIdLog,
                                'product_unit_price': unitPrice,
                                'product_desc': desc,
                                'product_taxes': taxes,
                                'sales_person': salesPersonUserId,
                                'product_same_inv': str(sameInvoice),
                                'delivery_id': deliveryIdLog,
                                'inv_id': invoiceIdLog,
                                'confirm_so': confirm_so,
                                'validate_delivery': validate_delivery,
                                'create_invoice': create_invoice,
                                'post_invoice': post_invoice,
                                'invoice_register_payment': invoice_register_payment,
                                'account_journal': accountJournal,
                                'payment_amount_money': amountPaymentMoney,
                                'payment_amount_percent': amountPaymentPercent,
                                'payment_amount_final': finalPaymentAmount,
                                'status': 'Success',
                                'date_submit': date_submit,
                                'x_external_order_id': str(sameInvoice),
                                'warehouse_id': warehouseId,
                                'product_uom': product_uom_id,
                            })


                    except Exception as e:
                        _logger.info(u'ERROR: {}'.format(e))
                        checkPartialSuccess = True
                        self.status = 'Partial Success'
                        saleAutomationId = self.env['sale_automation_log'].create({
                            'sale_automation': saleAutomationIdLog,
                            'product_qty': qty,
                            'customer_id': customerId,
                            'product_id': productProductId,
                            'sale_order_id': saleOrderIdLog,
                            'product_unit_price': unitPrice,
                            'product_desc': desc,
                            'product_taxes': taxes,
                            'sales_person': salesPersonUserId,
                            'product_same_inv': str(sameInvoice),
                            'delivery_id': deliveryIdLog,
                            'inv_id': invoiceIdLog,
                            'confirm_so': confirm_so,
                            'validate_delivery': validate_delivery,
                            'post_invoice': post_invoice,
                            'create_invoice': create_invoice,
                            'invoice_register_payment': invoice_register_payment,
                            'account_journal': accountJournal,
                            'payment_amount_money': amountPaymentMoney,
                            'payment_amount_percent': amountPaymentPercent,
                            'payment_amount_final': finalPaymentAmount,
                            'status': 'Error',
                            'error': u'ERROR: {}'.format(e),
                            'date_submit': date_submit,
                            'x_external_order_id': str(sameInvoice),
                            'warehouse_id': warehouseId,
                            'product_uom': product_uom_id,
                        })
                        pass
                        # raise ValidationError(u'ERROR: {}'.format(e))

            self.no_success_rec = no_succ_rec
            if checkPartialSuccess == False:
                self.status = 'Success'
        except Exception as e:
            _logger.info(u'ERROR: {}'.format(e))
            self.status = 'Error'
            self.error = u'ERROR: {}'.format(e)
            self.no_success_rec = no_succ_rec

        #except ValidationError as e:
            #_logger.info(u'ERROR: {}'.format(e))
            #self.status = 'Error'
            #self.error = u'ERROR: {}'.format(e)
            #self.no_success_rec = no_succ_rec


    def checkSA(self):
        error = 0
        success = 0

        saleAutomationLog = self.env['sale_automation_log'].search([('sale_automation', '=', int(self.id))])

        for sal in saleAutomationLog:
            if sal[0]['status'] == "Error":
                error = error + 1
            elif sal[0]['status'] == "Success":
                success = success + 1

        if error == 0:
            self.status = "Success"
            self.no_success_rec = self.sale_automation_log_count
        else:
            self.no_success_rec = success

