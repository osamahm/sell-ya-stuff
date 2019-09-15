First: 

	pip install bottle

Then download the source distribution of web2py.  Unzip it in any directory. 

	http://www.web2py.com/examples/static/web2py_src.zip

Then:
	
	cd web2py/applications
  
  and insert this project as a folder
  

To start web2py, do:

	python2 web2py.py -e

The final -e in the above line will redirect all logs to the shell, which is convenient for debugging

	
Stick to controllers/api.py
		 models/tables.py
		 static/js/default.index.js
		 views/default/index.html

Program Flow is such:
	
	start at tables.py
		each product has a table entry with details about the product
		each product also has an associated review table which consists of review members/rating/content
		Shopping cart has its own table. but references a product that can be within it, certain attributes of the shopping cart are also stated
		
	move to api.py
		get_product_list(): - returns product_list for main page to the javascript
		set_stars(): - receives vars attributes from javascript and updates the database entry with updated values
		get_user(): - returns user_email to javascript to stay updated
		save_user_review(): - receives vars attributes from js and updates entry where the product and the review_email are the same, and updates the review_content within the database.
		get_user_review(): - if you're logged in grab all reviews of a product that are not your own and return to the javascript
		add_to_shopping_cart(): - updates the shopping cart table with javascript stuff
		get_shopping_cart(): - match product_table id to shopping_cart product_id & if shopping_cart.in_shopping_cart is True, select the data ordering it by publish time in shopping cart, returns dict to js to display 
		get_quantity(): - returns products within a shopping cart, the total price accumulated of said products, and the total quantities of said products
		
		increment_quantity(): - queries based off passed in javascript params and then big brains a update on shopping_cart by matching and then incrementing the quantity in database based off checks from javascript and also using the previous query's stock quantity (such that its within the stock range of the item itself). also updates the shopping_cart_index in database
		decrement_quantity(): - same thing basically, validate time, validate person, validate in_shopping_cart status and then decrement the quantity if it ain't zero, update shopping_cart_index
		clear_cart(): - query entire cart, set in_shopping_cart flag to false, and delete everything in the shopping cart associated with the current user's email
		
		
		
