import frappe

def create_customer(doc, method):
    frappe.msgprint("Customer hook fired")  # temporary debug

    customer = frappe.get_doc({
        "doctype": "Customer",
        "customer_name": f"{doc.first_name} {doc.last_name}",
        "customer_type": "Individual",

        # if you REALLY want to put class into customer_group (not recommended):
        "customer_group": doc.get("class"),

        # your custom field on Customer (make sure it exists):
        "custom_student_section": doc.get("section"),
    })

    customer.insert(ignore_permissions=True)