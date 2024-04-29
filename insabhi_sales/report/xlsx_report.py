from openerp.addons.report_xlsx.report.report_xlsx import ReportXlsx


class SalesReportWriter(ReportXlsx):

    def generate_xlsx_report(self, workbook, data, objects):
        report_name = "Sale Order Report"
        sheet = workbook.add_worksheet(report_name[:31])

        sheet.set_column(0, 5, 26)

        header = [
            "Date",
            "SO Number",
            "Customer Name",
            "Total Cost",
            "Total Sales",
            "Total Margin",
        ]
        j = 0
        bold = workbook.add_format({"bold": True})
        sheet.write_row(0, 0, header, bold)
        sheet.freeze_panes(1, 0)

        for obj in objects:
            lines = obj.order_line
            total_cost = sum(x.purchase_price * x.product_uom_qty for x in lines)
            total_margin = sum(x.margin for x in lines)
            total = sum((x.price_unit * x.product_uom_qty) for x in lines)
            k = 0
            j += 1
            sheet.write(j, k, obj.date_order.split(' ')[0] if obj.date_order else "")
            sheet.write(j, k + 1, obj.name)
            sheet.write(j, k + 2, obj.partner_id.name)
            sheet.write(j, k + 3, total_cost)
            sheet.write(j, k + 4, total)
            sheet.write(j, k + 5, total_margin)


SalesReportWriter('report.insabhi_sales.report_sales_report','sale.order')


