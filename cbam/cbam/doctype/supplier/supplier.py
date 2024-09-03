# The `Supplier` class in the Python code creates a new user in the system based on supplier
# information when the status is "Sent to Supplier".
# Copyright (c) 2024, phamos GmbH and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Supplier(Document):
	def validate(self):
		pass

	def after_insert(self):
		self.add_linked_goods_to_childtable()
		if self.status == "Sent to Supplier":
			self.create_new_supplier_user()

	def on_update(self):
		self.create_new_employee()
		self.add_main_employee_to_cht()
		self.add_linked_goods_to_childtable()

	def before_save(self):
		if self.is_data_confirmed == True:
			self.status = "Confirmed by Supplier"

	def create_new_supplier_user(self):
		new_user = frappe.new_doc("User")
		new_user.email = self.company_email
		new_user.first_name = self.supplier_name
		new_user.append("role_profiles", {
			"name": "ibr1s5ocqu",
			"role_profile": "Supplier"
		})
		new_user.insert()

	def add_linked_goods_to_childtable(self):
		good_list = frappe.get_list("Good", pluck="name")
		for good in good_list:
			linked_supplier = frappe.get_value("Good", good, "supplier")
			if linked_supplier == self.name:
				self.append("goods", {
					"good_number": good
				})

	def create_new_employee(self):
		is_employee_registered = frappe.get_list("Supplier Employee", filters={'email': self.main_contact_employee_email} , fields=["name"], pluck="name")
		if not is_employee_registered:
			new_employee = frappe.new_doc("Supplier Employee")
			new_employee.status = "Raw Data"
			new_employee.supplier_company = self.name
			new_employee.last_name = self.main_contact_employee_last_name
			new_employee.first_name = self.main_contact_employee_first_name
			new_employee.email = self.main_contact_employee_email
			new_employee.phone_number = self.main_contact_employee_phone_number
			new_employee.position = self.main_contact_employee_position
			new_employee.insert()

	def add_main_employee_to_cht(self):
		main_contact = frappe.get_list("Supplier Employee", filters={'email': self.main_contact_employee_email} , fields=["name"], pluck="name")
		employee_list = [child.employee_email for child in self.employees if child.employee_email == self.main_contact_employee_email]
		if self.main_contact_employee_email not in employee_list:
			self.append("employees", {
				"employee_number": main_contact[0],
				"is_main_contact": 1
			})
			self.save()