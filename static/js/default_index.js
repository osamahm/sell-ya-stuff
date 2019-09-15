// This is the js for the default/index.html view.


var app = function() {

    var self = {};

    Vue.config.silent = false; // show all warnings

    // Extends an array
    self.extend = function(a, b) {
        for (var i = 0; i < b.length; i++) {
            a.push(b[i]);
        }
    };

    // Enumerates an array.
    var enumerate = function(v) { var k=0; return v.map(function(e) {e._idx = k++;});};


    //function to get products for Asg4
    self.get_products = function() {

        //pass in API to get all products
        $.getJSON(get_product_list_url,
            function(data) {

                //set product_list to hold passed in list and process
                self.vue.product_list = data.product_list;
                self.process_products();
            });
    };

    //function to get shopping cart
    self.get_shopping_cart = function(){
        $.getJSON(get_shopping_cart_url, 
            function(data){
                self.vue.shopping_cart = data.shopping_cart;
                self.process_shopping_cart();
            });
    };



    self.process_products = function() {
        // This function is used to product-process products, after the list has been modified
        // or after we have gotten new products. 
        enumerate(self.vue.product_list);
        self.vue.product_list.map(function (e) {
            Vue.set(e, '_num_stars_display', e.rating);
            Vue.set(e, 'is_hidden', false);
            Vue.set(e, 'show_reviews', false);
            Vue.set(e, 'user_review', {review_content: ""});
            Vue.set(e, 'other_reviews', []);
            Vue.set(e, 'in_shopping_cart', false);
        });
    };

    //process the shopping list 
    self.process_shopping_cart = function(){
        enumerate(self.vue.shopping_cart);
        self.vue.shopping_cart.map(function (e){
            Vue.set(e, 'index', e._idx);
            Vue.set(e, 'quantity', e.quantity);
            Vue.set(e, 'product_id', e.shopping_cart.product_id);
            Vue.set(e, 'time', e.shopping_cart.shopping_cart_publish_time);
            Vue.set(e, 'total_quantity', e.total_quantity);
            Vue.set(e, 'total_price', e.total_price);
        });
    };



    // Code for star ratings.
    self.stars_out = function (product_idx) {
        // Out of the star rating; set number of visible back to rating.
        var p = self.vue.product_list[product_idx];
        p._num_stars_display = p.rating;
    };

    self.stars_over = function(product_idx, star_idx) {
        // Hovering over a star; we show that as the number of active stars.
        var p = self.vue.product_list[product_idx];
        p._num_stars_display = star_idx;
    };

    self.set_stars = function(product_idx, star_idx) {
        // The user has set this as the number of stars for the product.
        var p = self.vue.product_list[product_idx];
        p.rating = star_idx;
        // Sends the rating to the server.
        $.post(set_stars_url, {
            product_id: p.id,
            rating: star_idx,
        });
    };



    //code to grab user_email
    self.get_user = function(){
        $.getJSON(get_user_url, function(data){
            self.vue.user_email = data.user_email;
        });
    };



    //code to search
    self.search_products = function(){
        //for every product in our product list
        for (var i=0; i<self.vue.product_list.length; i++){

            //grab the product and its title
            var product = self.vue.product_list[i];
            var title = self.vue.product_list[i].item_name;

            //if the normalized title is within a normalized search_string query
            if (title.toLowerCase().includes(self.vue.search_string.toLowerCase())){
                product.is_hidden = false;
            } else {
                product.is_hidden = true;
            }
        }
    };




    //code to enable or disable reviews
    self.toggle_reviews = function(product_idx){
        //grab product
        var p = self.vue.product_list[product_idx];

        //traverse list of products
        for (var i = 0; i<self.vue.product_list.length; i++){

            //for every product that isn't at the index, hide
            if(i != product_idx){
                self.vue.product_list[i].show_reviews = false;
            }
        }

        //finally, toggle reviews so that it is true 
        p.show_reviews = !p.show_reviews;
    };




    //code to get current user's review
    self.get_user_review = function(product_idx){

        //grab product
        var p = self.vue.product_list[product_idx];

        //grab details 
        $.getJSON(get_user_review_url, 
            {product_id: p.id,
             review_email: self.vue.user_email
            },

            //if user review is not null, grab it
            function(data){
                if(data.user_review != null){
                    p.user_review = data.user_review;
                }
                //and unsave it, so that the user can modify and save
                Vue.set(p.user_review, 'saved', false);
            });
    };



    //code to save user review
    self.save_user_review = function(product_idx){

        //grab product and the user review for it
        var p = self.vue.product_list[product_idx];
        var user_review = p.user_review;

        //initially, review is not saved
        user_review.saved = false;

        //using api, set the db entries to hold relevant info
        $.post(save_user_review_url, {
            product_id: p.id,
            review_email: self.vue.user_email,
            review_content: user_review.review_content
        },
        //save when you have submitted the post form
        function(data){
            user_review.saved = true;
        });
    };

 


    //code to grab other reviews for a product
    self.get_other_reviews = function(product_idx){
        //grab product
        var p = self.vue.product_list[product_idx];

        //grab details
        $.getJSON(get_other_reviews_url, {product_id: p.id},
            function(data){
                p.other_reviews = data.other_reviews;
            });
    };




    //code to change shopping/cart mode
    self.toggle_mode = function(){
            self.vue.mode = !self.vue.mode;
    };




   //code to save item to shopping cart
    self.add_to_shopping_cart = function(product_idx){

       //grab product
       var p = self.vue.product_list[product_idx];

       //go through the entire product list
       for (var i = 0; i<self.vue.product_list.length; i++){

            //if the index is not equal to the product index AND the item is not already in the cart
            if(i != product_idx && self.vue.product_list[i].in_shopping_cart != true){

                //set it to be false
                self.vue.product_list[i].in_shopping_cart = false;
            }
       }
       
       //set item to be in the shopping cart
       p.in_shopping_cart = !p.in_shopping_cart;

       //post to the database
       $.post(add_to_shopping_cart_url, {
            product_id: p.id,
            shopping_cart_email: self.vue.user_email,
            in_shopping_cart: p.in_shopping_cart
       }); 

       //and update the shopping cart
       setTimeout(function(){

            self.get_shopping_cart();
            
        }, 500);

    };


    //populate the shopping cart values! 
    //Thought it'd be cool to do a void button command to initialize the js as needed.
    self.populate = function(){

        //for each of the values in the shopping cart, run get_quantity
        for(i = 0; i < self.vue.shopping_cart.length; i++){
             self.get_quantity(i);  
        }
    };


    //get_quantity updates the current shopping cart item's quantity
    self.get_quantity = function(product_idx){

        //grab the product in the shopping cart array
        var p = self.vue.shopping_cart[product_idx];

        //fetch data from api, returns a dict of items in the cart with:
            // - product quantities in shopping cart
            // - associated product id
            // - associated shopping cart index
        $.getJSON(get_quantity_url, {
        }, function(data){

            //checks all rows in dict
            for(i = 0; i < data.results.length; i++){

                //if ever the product's id is equal to an indice in our result
                if(product_idx == i){

                    //set quantity to the most updated quantity
                    p.quantity = data.results[i].quantity;
                    console.log("HELLLLLLLLLLLLLLLLLO")
                    console.log(data.total_price)
                    console.log(data.total_quantity)
                    console.log("HELLLLLLLLLLLLLLLLLO")

                    p.total_quantity = data.total_quantity;
                    p.total_price = data.total_price;
                }
            }
            //appropriate time out to ensure safe data transfer
            setTimeout(function(){
                self.vue.total_quantity = p.total_quantity;
                self.vue.total_price = p.total_price;
            }, 100);
        });
    };




    //code to increment quantity of a shopping cart item
    self.increment_quantity = function(product_idx){

        //grab da product with both hands
        var p = self.vue.shopping_cart[product_idx];

        //pass through to api:
            // -current user
            // -current quantity
            // -current index
            // -current time
        $.post(increment_quantity_url, {
                product_quantity: p.quantity,
                shopping_cart_email: self.vue.user_email,
                index: p._idx,
                time: p.time,
                total_quantity: p.total_quantity,
                total_price: p.total_price
            });

        //appropriate timeout to ensure safe data travel
        setTimeout(function(){
            
            //update the quantity on screen 
            self.get_quantity(product_idx);
        }, 200);
    };

    
    //code to decrement quantity of a shopping cart item
    self.decrement_quantity = function(product_idx){

        //grab da product again
        var p = self.vue.shopping_cart[product_idx];

        //pass through to api:
            // -current user
            // -current quantity
            // -current time
        $.post(decrement_quantity_url, {
                product_quantity: p.quantity,
                shopping_cart_email: self.vue.user_email,
                index: p._idx,
                time: p.time,
                total_quantity: p.total_quantity,
                total_price: p.total_price

            });

        //appropriate timeout to ensure safe data travel
        setTimeout(function(){
            
            //update the quantity on screen
            self.get_quantity(product_idx);
        }, 200);
    };


    //run python script to clear the cart
    self.clear_cart = function(){

    for(i = 0; i < self.vue.product_list.length; i++){
        self.vue.product_list[i].in_shopping_cart = false;
    }


        $.post(clear_cart_url,{},
            function(data){
               self.vue.shopping_cart = [];
               self.vue.total_price = 0;
               self.vue.total_price = 0;
           });
    };





    // Complete as needed.
    self.vue = new Vue({
        el: "#vue-div",
        delimiters: ['${', '}'],
        unsafeDelimiters: ['!{', '}'],
        data: {
            product_list: [],
            shopping_cart: [],
            star_indices: [1, 2, 3, 4, 5],
            search_string: "",
            user_email: undefined,
            mode: undefined,
            total_quantity: 0,
            total_price: 0,
        },
        methods: {
            stars_out: self.stars_out,
            stars_over: self.stars_over,
            set_stars: self.set_stars,
            search_products: self.search_products,
            toggle_reviews: self.toggle_reviews,
            save_user_review: self.save_user_review,
            get_user_review: self.get_user_review,
            get_other_reviews: self.get_other_reviews,
            add_to_shopping_cart: self.add_to_shopping_cart,
            get_shopping_cart: self.get_shopping_cart,
            toggle_mode: self.toggle_mode,
            get_quantity: self.get_quantity,
            increment_quantity: self.increment_quantity,
            decrement_quantity: self.decrement_quantity,
            populate: self.populate,
            clear_cart: self.clear_cart
        }

    });

    self.get_user();
    self.get_products();



    return self;
};

var APP = null;


// No, this would evaluate it too soon.
// var APP = app();

// This will make everything accessible from the js console;
// for instance, self.x above would be accessible as APP.x
jQuery(function(){APP = app();});
