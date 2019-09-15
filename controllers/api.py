# Here go your api methods.

def get_product_list():
	results = []
	if auth.user is None:


		#query everythang
		all_products = db().select(db.product_table.ALL, db.review_table.ALL,
			left = [db.review_table.on((db.review_table.product_id == db.product_table.id))],
			orderby=~db.product_table.publish_time
			)


		# i was getting duplicates so i created a flag to check for duplicates
		prev_prod_id = None

		for item in all_products:

			# set current product id
			current_prod_id = item.product_table.id

			# if its equal to the previous, duplicate, discard
			if current_prod_id == prev_prod_id:
				continue
			
			# start running total of reviews over
			running_total = 0

			# grab all reviews from product that are rated
			reviews = db((db.review_table.product_id == item.product_table.id) & (db.review_table.review_stars > 0)).select()

			# summation of all ratings for item
			for review in reviews:
				running_total += review.review_stars

			# set average rating via formula
			if running_total != 0 and len(reviews) != 0:
				item.average_star_rating = int(running_total/len(reviews))

			else:
				item.average_star_rating = None

			# append to dictionary to pass in
			results.append(dict(
				id = item.product_table.id,
				item_name = item.product_table.item_name,
				selling_price = item.product_table.selling_price,
				item_description = item.product_table.item_description,
				rating = None,
				average_star_rating = item.average_star_rating,
				stock_quantity = item.product_table.stock_quantity,
				))

			# set the prev_prod_id to hold the current, as we're done with it 
			prev_prod_id = current_prod_id

	else:


		#query everything as long as the product id's match and the logged in user is valid
		all_items = db().select(
			db.product_table.ALL, db.review_table.ALL,
			left = [db.review_table.on((db.review_table.product_id == db.product_table.id) & (db.review_table.review_email == auth.user.email))],
			orderby= ~db.product_table.publish_time
			)

		for item in all_items:


			# re-initliaze running_total per item
			running_total = 0

			# grab all reviews from product that are rated
			reviews = db((db.review_table.product_id == item.product_table.id) & (db.review_table.review_stars > 0)).select()

			# summation of all ratings for item
			for review in reviews:
				running_total += review.review_stars

			# set average rating via formula
			if running_total != 0 and len(reviews) != 0:
				item.average_star_rating = int(running_total/len(reviews))

			else:
				item.average_star_rating = None

			# append to dictionary to pass in
			results.append(dict(
				id = item.product_table.id,
				item_name = item.product_table.item_name,
				selling_price = item.product_table.selling_price,
				item_description = item.product_table.item_description,
				rating = None if item.review_table.id is None else item.review_table.review_stars,
				average_star_rating = item.average_star_rating,
				stock_quantity = item.product_table.stock_quantity
				))
	return response.json(dict(product_list=results))



# given code
@auth.requires_login()
@auth.requires_signature(hash_vars=False)
def set_stars():
	product_id = int(request.vars.product_id)
	review_stars = int(request.vars.rating)

	db.review_table.update_or_insert(
		(db.review_table.product_id == product_id) &
		(db.review_table.review_email == auth.user.email),
		product_id = product_id,
		review_email = auth.user.email,
		review_stars = review_stars
		)

	return "ok"



# we're gonna need to check for user validation in js/html
def get_user():
	user_email = None if auth.user is None else auth.user.email 
	return response.json(dict(user_email=user_email))



#code for saving review
@auth.requires_login()
@auth.requires_signature(hash_vars=False)
def save_user_review():

	# set variables to hold current product id and email of reviewer
	product_id = request.vars.product_id
	review_email = request.vars.review_email

	# search for item and the matching review email, validify and replace the content
	db.review_table.update_or_insert(
		((db.review_table.product_id == product_id) &
		(db.review_table.review_email == review_email)),
		review_content=request.vars.review_content,
		product_id=product_id
		)
	return "ok"


# code for grabbing user review
@auth.requires_login()
@auth.requires_signature(hash_vars=False)
def get_user_review():

	# set variables to hold current product id and email of reviewer
	product_id = request.vars.product_id
	review_email = request.vars.review_email

	# search for item and the matching review email
	user_review = db((db.review_table.product_id == product_id) & (db.review_table.review_email == review_email)).select().first()

	# return query
	return response.json(dict(user_review=user_review))


# code for getting other reviews
def get_other_reviews():

	# if youre not logged in just grab the product
	if auth.user is None:
		other_reviews = db(db.review_table.product_id == request.vars.product_id).select()
	else:

		# if you're logged in then grab the product and all of the data from which you are not the author
		other_reviews = db(
			(db.review_table.product_id == request.vars.product_id) &
			(db.review_table.review_email != auth.user.email)).select()

	# return that into the html/js
	return response.json(dict(other_reviews=other_reviews))


# add item to shopping cart
@auth.requires_login()
@auth.requires_signature(hash_vars=False)
def add_to_shopping_cart():

	# grab the product_id, user, and the shopping cart flag
	product_id = request.vars.product_id
	shopping_cart_email = request.vars.shopping_cart_email
	in_shopping_cart = request.vars.in_shopping_cart

	# update the database
	db.shopping_cart.update_or_insert(

		# QUERY:
			# validify product id
			# validify user
		((db.shopping_cart.product_id == product_id) & 
		 (db.shopping_cart.shopping_cart_email == shopping_cart_email)),

		# update appropriate items including the current time the item was added
		product_id = product_id,
		in_shopping_cart = in_shopping_cart,
		shopping_cart_publish_time = datetime.datetime.utcnow()
		)

	return "ok"


# code to grab shopping cart
@auth.requires_login()
@auth.requires_signature(hash_vars=False)
def get_shopping_cart():
	
	# query all products in the shopping cart and order them by the time they were added, most recent first.
	shopping_cart = db((db.product_table.id == db.shopping_cart.product_id) & 
					   (db.shopping_cart.in_shopping_cart == True)).select(orderby= db.shopping_cart.shopping_cart_publish_time)

	return response.json(dict(shopping_cart=shopping_cart))



#code to provide list of items in shopping cart
@auth.requires_login()
@auth.requires_signature(hash_vars=False)
def get_quantity():
	# initialize array which will hold results
	results = []

	# query all items in the product_table which has been put in the shopping cart
	query = db((db.product_table.id == db.shopping_cart.product_id) & 
		          (db.shopping_cart.in_shopping_cart == True)).select()

	total_quantity = 0
	total_price = 0

	for item in query:
		total_price += (item.product_table.selling_price * float(item.shopping_cart.product_quantity))
		total_quantity += int(item.shopping_cart.product_quantity)

	# for each item in our query, append it to our array
	for item in query:
		results.append(dict(
			quantity = item.shopping_cart.product_quantity,
			product_id = item.shopping_cart.product_id,
			shopping_cart_idx = int(item.shopping_cart.shopping_cart_idx)
			))

	# and return that array as a dictionary
	return response.json(dict(results=results, total_price=total_price, total_quantity=total_quantity))	


# code to increment quantity of item in shopping cart
@auth.requires_login()
@auth.requires_signature(hash_vars=False)
def increment_quantity():

	# grab the product_id, index, time, and user of the item passed in
	product_id = request.vars.product_id
	index = request.vars.index
	time = request.vars.time
	shopping_cart_email = request.vars.shopping_cart_email


	# fix up a query to validate item and grab its quantity in stock value to make one liner below
	query = db((db.shopping_cart.shopping_cart_publish_time == time) &
			   (db.product_table.id == db.shopping_cart.product_id) & 
		       (db.shopping_cart.in_shopping_cart == True)).select(db.product_table.stock_quantity).first()
	
	# update the shopping cart database entry
	db.shopping_cart.update_or_insert(
		# QUERY:
			# validate the time the person added the item in the shopping cart, 
			# the person who added it, 
			# and whether its in the shopping cart
		((db.shopping_cart.shopping_cart_publish_time == time) & 
		 (db.shopping_cart.shopping_cart_email == shopping_cart_email) & 
		 (db.shopping_cart.in_shopping_cart == True)),

		# ONE LINER:
		#  if the product quantity is not null and does not exceed stock limit, increment
		#  else decrement
		product_quantity = (int(request.vars.product_quantity) + 1) if request.vars.product_quantity is not None and (int(request.vars.product_quantity))  < query.stock_quantity else (int(request.vars.product_quantity)),

		# set the shopping cart index in database with js value
		shopping_cart_idx = int(index),

		)
	return "ok"

@auth.requires_login()
@auth.requires_signature(hash_vars=False)
def decrement_quantity():
	# grab index, time, and user of the item passed in
	shopping_cart_email = request.vars.shopping_cart_email
	index = request.vars.index
	time = request.vars.time
	logger.info("\n\n")

	# update the database
	db.shopping_cart.update_or_insert(

		# QUERY:
			# validate the time 
			# validate the person who added it
			# and whether its in the shopping cart
		((db.shopping_cart.shopping_cart_publish_time == time) & 
		 (db.shopping_cart.shopping_cart_email == shopping_cart_email) & 
		 (db.shopping_cart.in_shopping_cart == True)),

		# if product quantity is not 0, then decrement, else it's zero, you can't go negative
		product_quantity = (int(request.vars.product_quantity) - 1) if (int(request.vars.product_quantity)) > 0 else 0,

		# set the shopping cart index in database with js value
		shopping_cart_idx = int(index)
		)
	return "ok"

# code to clear cart
@auth.requires_login()
@auth.requires_signature(hash_vars=False)
def clear_cart():

	#query all of the items in the user's shopping cart 
	query = db(db.shopping_cart.shopping_cart_email == auth.user.email).select()
	
	# set each item to not be in the shopping cart
	for item in query:
		item.in_shopping_cart = False

	# delete theme all
	db(db.shopping_cart.shopping_cart_email == auth.user.email).delete()


