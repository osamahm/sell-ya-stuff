# Define your tables below (or better in another model file) for example
#
# >>> db.define_table('mytable', Field('myfield', 'string'))
#
# Fields can be 'string','text','password','integer','double','boolean'
#       'date','time','datetime','blob','upload', 'reference TABLENAME'
# There is an implicit 'id integer autoincrement' field
# Consult manual for more options, validators, etc.




# after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)


"""

First define database tables for products, for stars, and for reviews; 
since you are going to write stars and reviews separately, 
	it’s easier to use separate tables for stars and reviews, 
	so you don’t have to worry about timing of writes.  
	Please ensure that the tables have appropriate names; 
		if you call “posts” the table for products, points will be taken off. 
"""

import datetime

def get_user_email():
	return auth.user.email if auth.user is not None else None

def get_current_time():
	return datetime.datetime.utcnow()

db.define_table('product_table',
				 Field('creator', default=get_user_email()),
				 Field('item_name', 'string'),
				 Field('item_description', 'string'),
				 Field('stock_quantity', 'integer'),
				 Field('sold_quantity', 'integer'),
				 Field('selling_price', 'double'),
				 Field('bought_price', 'double'),
				 Field('starred', 'boolean', default=False),
				 Field('profit', 'double'),
				 Field('publish_time', default= get_current_time())
				)

db.define_table('review_table',
	             Field('product_id', 'reference product_table'),
				 Field('review_email', default=get_user_email()),
				 Field('review_stars', 'integer', default=None),
				 Field('review_content'),
				)

db.define_table('shopping_cart',
				 Field('product_id', 'reference product_table'),
				 Field('shopping_cart_email', default=get_user_email()),
				 Field('in_shopping_cart', 'boolean', default=False),
				 Field('product_quantity', default=0),
				 Field('shopping_cart_idx', default=0),
				 Field('shopping_cart_publish_time', default=get_current_time()),
				 Field('total_quantity'),
				 Field('total_price')
	           )



db.product_table.creator.writable = False
db.product_table.creator.readable = False
db.product_table.starred.writable = False
db.product_table.starred.readable = False
db.product_table.sold_quantity.writable = False
db.product_table.sold_quantity.readable = False
db.product_table.profit.readable = False
db.product_table.profit.writable = False
db.product_table.publish_time.readable = False
db.product_table.publish_time.writable = False