import frappe

STUDENT_ROLE = "Student Portal"
PARENT_ROLE = "Parent Portal"


def _create_website_user(email: str, first_name: str, last_name: str = ""):
    # If user exists, reuse
    if frappe.db.exists("User", email):
        return frappe.get_doc("User", email)

    user = frappe.get_doc({
        "doctype": "User",
        "email": email,
        "first_name": first_name or email,
        "last_name": last_name or "",
        "enabled": 1,
        "user_type": "Website User",
        "send_welcome_email": 0,   # 👈 turn off (optional)
    })

    user.insert(ignore_permissions=True)

    # ✅ Most reliable: send "set password" email
    try:
        user.send_password_reset()
    except Exception:
        # if mail not configured, it won't crash your save
        frappe.log_error(frappe.get_traceback(), "Portal user password reset failed")

    return user


def _add_role(user, role_name: str):
    if not frappe.db.exists("Has Role", {"parent": user.name, "role": role_name}):
        user.add_roles(role_name)


def _add_user_permission(user: str, allow_doctype: str, for_value: str):
    # user should be the User.name (usually the email)
    if frappe.db.exists("User Permission", {
        "user": user,
        "allow": allow_doctype,
        "for_value": for_value
    }):
        return

    frappe.get_doc({
        "doctype": "User Permission",
        "user": user,
        "allow": allow_doctype,
        "for_value": for_value,
        "apply_to_all_doctypes": 0
    }).insert(ignore_permissions=True)


# -------------------------
# Hooks
# -------------------------

def create_student_portal_user(doc, method=None):
    if not getattr(doc, "email", None):
        return

    if getattr(doc, "student_user", None):
        return

    user = _create_website_user(
        email=doc.email,
        first_name=getattr(doc, "first_name", "") or getattr(doc, "student_name", "") or "Student",
        last_name=getattr(doc, "last_name", "") or ""
    )

    _add_role(user, STUDENT_ROLE)

    doc.db_set("student_user", user.name)

    # Student can only see their Student record
    _add_user_permission(user.name, "Student", doc.name)


def create_parent_portal_user(doc, method=None):
    if not getattr(doc, "email", None):
        return

    if getattr(doc, "user", None):
        return

    user = _create_website_user(
        email=doc.email,
        first_name=getattr(doc, "fullname", "") or getattr(doc, "parent_name", "") or "Parent",
        last_name=""
    )

    _add_role(user, PARENT_ROLE)

    doc.db_set("user", user.name)

    # Parent can only see their Parent record
    _add_user_permission(user.name, "Parent", doc.name)

    # OPTIONAL (recommended): Parent can also read each child student record
    # This makes dashboards much easier.
    if getattr(doc, "children", None):
        for row in doc.children:
            if row.student:
                _add_user_permission(user.name, "Student", row.student)