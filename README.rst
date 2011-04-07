This is migration branch
=========================

Quick guide how to migarte from branch 0.2.1 to branch 0.4
-------------------------------------------------------------


1. Checkout basket application to branch ``migrate-0.2.1-0.4``.

2. Run ::
	
	manage.py migrate basket --delete-ghost-migrations

3. Checkout basket application to branch ``0.4``.



In details
-----------

Branch 0.4 branch assumes use plug-ins for order details, order tracking, 
payment or shipping. In previous branches all information models were located in 
``basket`` app.

Changes with Order model:

	* session ForeignKey converted session_key CharField
	
Changes with Status, OrderStatus models:

	* database-stored statuses are deleted. 
	* now basket app has 5 defined statuses for order: pending, new, 
	  process, closed and error 
	* all orderstatus instances are converted to status taking into account 
	  old status
	* old data, previously saved in ``form_data`` field will be rendered
	  as comment into first required status `pending`.