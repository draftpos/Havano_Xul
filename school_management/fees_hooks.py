import frappe

def create_item(doc, method):

    item = frappe.get_doc({
        "doctype": "Item",
        "item_code": doc.fees_name,
        "item_name": doc.fees_name,
        "item_group": "School Fees",
        "is_sales_item": 1,
        "is_stock_item": 0
    })

    item.insert(ignore_permissions=True)

    frappe.db.set_value("Fees Type", doc.name, "item", item.name)
