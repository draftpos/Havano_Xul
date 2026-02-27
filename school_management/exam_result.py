import frappe
from frappe.model.document import Document

class ExamResult(Document):

    def validate(self):
        self.assign_grades()

    def assign_grades(self):
        for row in self.subjects:   # your child table fieldname
            if row.marks is not None:
                grading = frappe.get_all(
                    "Grading",
                    filters={
                        "min_score": ["<=", row.marks],
                        "max_score": [">=", row.marks]
                    },
                    fields=["grade_letter"]
                )

                if grading:
                    row.grade = grading[0].grade_letter
                else:
                    row.grade = None