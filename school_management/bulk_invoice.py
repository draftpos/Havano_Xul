import frappe

def create_bulk_invoices(doc, method):

    customers = frappe.get_all(
        "Customer",
        filters={"customer_group": doc.customer_group},
        pluck="name"
    )

    for cust in customers:

        invoice = frappe.new_doc("Sales Invoice")
        invoice.customer = cust
        invoice.posting_date = doc.posting_date

        for row in doc.items:
            invoice.append("items", {
                "item_code": row.item,
                "qty": row.qty,
                "rate": row.rate
            })

        invoice.insert(ignore_permissions=True)
        invoice.submit()
