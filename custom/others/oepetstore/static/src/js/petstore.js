/*
the first parameter(instance) is the current instance of the Odoo web client, it gives access to various capabilities defined by the Odoo (translations, network services) as well as objects defined by the core or by other modules.
the second parameter(local) is your own local namespace automatically created by the web client. Objects and variables which should be accessible from outside your module (either because the Odoo web client needs to call them or because others may want to customize them) should be set inside that namespace.
*/

//modules are declared as functions set on the global openerp variable.
openerp.oepetstore = function(instance, local) {
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;


////////////////////////////////////////////////////////////////////////
//
//
//
//
// SEE THE BELOW EXERCISE FOR  REFERENCE PURPOSE
//
//
//
//
//////////////////////////////////////////////////////////////////////////


//Exercise. Not really suitable. Dont use this. Use the Odoo Exercise below
//This Class is an Instance of the AbstractField Class. Whateever program that must use this class, must create an object from the class.
 local.myWidget = instance.Widget.extend({
        start : function(){
             this.$el.append(instance.web.qweb.render("myWidgetTemplate",{'products': ['Beans','Rice','Garri','Akamu'],colour:'#00FF00',colour_name:'blue'})); //Passes the widget context variables ass dictionary
        },
    });
    instance.web.client_actions.add('petstore.myWidget', 'instance.oepetstore.myWidget');

//So a client action handler can be a Javascript function, or a Widget as we use it below
//Odoo Exercise  .This is the method you should always use. You can even call other templates
local.OdooExercise = instance.Widget.extend({  //This is the client action handler for the client action defined in the xml file. It is the entry main point for the client action program. All other widgets can be instantiated inside here
 //Note
//a client action handler can also be a regular function, in whch case it'll be called and its result (if any) will be interpreted as the next action to execute.
        start: function() {
            prods = ["cpu", "mouse", "keyboard", "graphic card", "screen"];
            var productsOdoo = new local.ProductsWidget(this, prods, "#00FF00");
            productsOdoo.appendTo(this.$el);// $el is the widget's root element

            //Calling other templates with context parameters
            this.$el.append(instance.web.qweb.render("myWidgetTemplate",{'products': ['Beans','Rice','Garri','Akamu'],colour:'#00FFCC',colour_name:'blue'})); //Passes the widget context variables ass dictionary
        },
    });
//A client action is (as its name implies) an action type defined almost entirely in the client, in javascript for Odoo web. The server simply sends an action tag (an arbitrary name), and optionally adds a few parameters, but beyond that everything is handled by custom client code
//Our widget is registered as the handler for the client action through the following line of code:
instance.web.client_actions.add('petstore.action_tag_exercise_odoo', 'instance.oepetstore.OdooExercise'); // mapping the widget to the client action


 local.ProductsWidget = instance.Widget.extend({
 //For those assigning template and using the init() to pass parameters(i.e. context parameters)
        template: "ProductsWidget",
        init: function(parent, products, color) {
            this._super(parent);
            this.products = products;
            this.color = color;
        },
        start : function(){
              //  Does not work. Brings error. Parameters need to be passed, for it to work. see the below correction
             //this.$el.append(instance.web.qweb.render("ProductsWidget"));  //OR
             //this.$el.append(instance.web.qweb.render("ProductsWidget1"));

            //This works fine. LESSON NOTE: if you are passing your parameters through the init(), then you must assign a template variable as shown above.
             //  For those rendering templates and passing context parameters, without assigning the above template
             this.$el.append(instance.web.qweb.render("ProductsWidget1",{'products': ["cpu1", "mouse1", "keyboard1", "graphic card1", "screen1"],color:'#00FFAA'})); //Passes the widget context variables ass dictionary
        },

    });

//////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////







//This Class is an Instance of the AbstractField Class. Whateever program that must use this class, must create an object from the class.
    local.HomePage = instance.Widget.extend({
        className: 'oe_petstore_homepage',

        start: function() {
            console.log("pet store home page loaded");
            alert('This is the pet store');

            //All widgets(this) e.g. the HomePage widget, have a el(ROOT ELEMENT of the WIDGET) which represents the section of page they're in charge of (as a jQuery object).
            this.$el.append("<div>Hello dear Odoo user!</div>");  // By default, $el is an empty <div> element. Widget content should be inserted there.
               //"this" is the widget, el is the root element, $el selects the root element
           var greeting = new local.GreetingsWidget();
           res = greeting.appendTo(this.$el);  //When the appendTo() method is called, it asks the widget to insert itself at the specified position and to display its content. The start() method will be called during the call to appendTo().

           //Due to multiple technical and conceptual reasons, it is necessary for a widget to know who is its parent and who are its children.
            var greeting1 = new local.GreetingsWid(this); //passes the parent widget(this) to the greeting widget. Note that the init function of a widget has the "parent" parameter.  The first argument is this, which in that case was a HomePage instance. This tells the widget being created which other widget is its parent.
            greeting1.appendTo(this.$el);
            alert(this.getChildren()[0].$el)

            //When overriding the init() method of a widget it is of the utmost importance to pass the parent to the this._super() call, otherwise the relation will not be set up correctly:
            var greeting2 = new local.GreetingsWidg(this,'kinco'); //passes the parent widget(this) to the greeting widget.  The first argument is this, which in that case was a HomePage instance. This tells the widget being created which other widget is its parent.
            greeting2.appendTo(this.$el);


            //Finally, if a widget does not have a parent (e.g. because it's the root widget of the application), null can be provided as parent:
            var greeting3 = new local.GreetingsWidg(null,'No Parent Here'); //passes the parent widget(this) to the greeting widget.  The first argument is this, which in that case was a HomePage instance. This tells the widget being created which other widget is its parent.
            greeting3.appendTo(this.$el);


            //greeting.destroy();

            this.$el.append(instance.web.qweb.render("HomePageTemplate", {name: "Klaus"}))


            return res
        },
    });


    // Creating a new widget
    local.GreetingsWidget = instance.Widget.extend({
        className: 'oe_petstore_greetings',
        start: function() {
            this.$el.append("<div>We are so happy to see you again in this menu!</div>");

        },

    });

//Due to multiple technical and conceptual reasons, it is necessary for a widget to know who is its parent and who are its children.
    local.GreetingsWid = instance.Widget.extend({
        className: 'oe_petstore_greetings_extra',
        start: function() {
            alert(this.getParent().$el)
        },

    });


//When overriding the init() method of a widget it is of the utmost importance to pass the parent to the this._super() call, otherwise the relation will not be set up correctly:
   local.GreetingsWidg = instance.Widget.extend({
        init: function(parent, name) {
            this._super(parent);
            this.name = name;
        },
        start : function(){alert('Hey there: ' + this.name)},
    });



    //note the <div class="oe_petstore_greetings"> element which represents the GreetingsWidget instance is inside the <div class="oe_petstore_homepage"> which represents the HomePage instance, since we appended
/* <div class="oe_client_action">
        <div class="oe_petstore_homepage">   // represents that element($el) that is usually empty, for the HomePage instance.
            <div>Hello dear Odoo user!</div>
            <div class="oe_petstore_greetings">     //represents the GreetingsWidget instance
                <div>We are so happy to see you again in this menu!</div>
            </div>
        </div>
    </div>
 */


    var MyClass = instance.web.Class.extend({

        say_hello : function(){
            alert('I am saying Hello to ' + this.name + ' ' + this.surname);
        },

        init : function(surname){
            this.surname = surname ;
        },


    });

    var myObject = new MyClass('Okonkwo');
    myObject.name = "Kingsley";
    myObject.say_hello();


//It is also possible to create subclasses from existing (used-defined) classes by calling extend() on the parent class, as is done to subclass Class():
    var MySpanishClass = MyClass.extend({
        say_hello: function() {
           alert('hola ' + this.surname)
         },
    });

    var my_object = new MySpanishClass("Bob");
    my_object.say_hello();

// When overriding a method using inheritance, you can use this._super() to call the original method:
    var MySpanishClass = MyClass.extend({
    say_hello: function() {
         this._super();
        alert("translation in Spanish: hola " + this.surname);
    },
    });
    var my_object = new MySpanishClass("John");
    my_object.say_hello();



    instance.web.client_actions.add('petstore.homepage', 'instance.oepetstore.HomePage');




/////////////////////////////////////////////////////////////////////

///// OTHER EXAMPLES

////////////////////////////////////////////////////////////////////



local.OtherExamples = instance.Widget.extend({ //Client action handler
    start : function(){
        var mywidgetb = new local.MyWidgetButton(this);
        mywidgetb.appendTo(this.$el);



 /////////////////////////////////////////////////////////////////
// USING EVENTS
/////////////////////////////////////////////////////////////////

//NOTE that odoo does not recommend creating custom events that need to be triggered. rather use functions to do the job. see note below
//Triggering events on an other widget is generally a bad idea. The main exception to that rule is openerp.web.bus which exists specifically to broadcasts evens in which any widget could be interested throughout the Odoo web application.

//Create custom event, if you want other global functions inside/outside your javascript module to respond to it, and do other things. If not just run direct function
        var confirmwidg = new local.ConfirmWidget(this);
        confirmwidg.appendTo(this.$el);
        // Bind the user_chose_event to the function: user_chose
        confirmwidg.on("user_chose_event", this, this.user_chose); //We can then set up a parent event instantiating our generic widget and listening to the user_chose event using on():


      var confirmwidggood= new local.ConfirmWidget(this);
      confirmwidggood.appendTo(this.$el);
      confirmwidggood.on("eventTrig", this, this.the_function);  //Binds the custom event(eventTrig) to the function
      confirmwidggood.trigger("eventTrig", 'This is the message i have for you, for triggering the custom event now');  // raises this function_good event


//Selecting dom elements using .find() . however, But because it's a common operation, Widget() provides an equivalent shortcut through the $() method:
//Warning
//The global jQuery function $() should never be used unless it is absolutely necessary: selection on a widget's root are scoped to the widget and local to it, but selections with $() are global to the page/application and may match parts of other widgets and views, leading to odd or dangerous side-effects. Since a widget should generally act only on the DOM section it owns, there is no cause for global selection.
        this.$el.find('.cancel_button').css("background-color", 'red');
        this.$('button.ok_button').css("background-color", 'yellow');


        //Colour Widget
        var ciw = new local.ColorInputWidget(this);
        ciw.appendTo(this.$el);

        var mycolorwidg = new  local.MyDisplayWidget(this);
        mycolorwidg.appendTo(this.$el)

/////////////////////////////////////////////////////////////////
// USING EVENTS ENDS HERE
/////////////////////////////////////////////////////////////////


//////////////////////////////////////////////////////////////////////////////
/// Communication with the Odoo Server Calling Methods
//////////////////////////////////////////////////////////////////////////////
       var mM = new local.ModelMessage(this).appendTo(this.$el);

 //////////////////////////////////////////////////////////////////////////////
/// Communication with the Odoo Server Calling Methods Ends HERE
//////////////////////////////////////////////////////////////////////////////

//////////////////////////////////////////////////////////////////////////////
// Using Queries / Calling Methods
//////////////////////////////////////////////////////////////////////////////
       var mwidgetMesaage = new local.MessageOfTheDay(this).appendTo(this.$el);

        var ptw = new local.PetToyWidget(this).appendTo(this.$el.find('.pet_toy_widget_here'));
//////////////////////////////////////////////////////////////////////////////
// Using Queries / Calling Methods Wnds here
//////////////////////////////////////////////////////////////////////////////



    },
    user_chose : function(is_confirm){
       if (is_confirm) {
            alert("The user agreed to continue");
        } else {
            alert("The user refused to continue");
        }
    },
    the_function: function(msg) {
        alert(msg);
    },
        color_changed: function() {
            this.$(".oe_color_div").css("background-color", this.colorInput.get("color"));
        },

});
instance.web.client_actions.add('action_tag_other_examples', 'instance.oepetstore.OtherExamples');

//a client action handler can also be a regular function, in which case it'll be called and its result (if any) will be interpreted as the next action to execute.
//instance.web.client_actions.add('action_tag_other_examples', 'instance.oepetstore.ok_now');
//local.ok_now = function(){
//alert('I am a direct function. And i am working fine');
//},


































///////////////////////////////////////////////////////////////////////////////
//////////////
////                      WIDGETS SECTION
////////////
////////////////////////////////////////////////////////////////////////////////////



//////////////////////////////////////////////////////////////////
///////////      USING EVENTS WIDGETS
/////////////////////////////////////////////////////////////////
local.MyWidgetButton = instance.Widget.extend({
    template : 'OtherExampleWidget',
    events: {
        "click button.ok_button": "button_clicked",
    },
    button_clicked: function() {
        alert('Ths event button has been clicked');
    },
});


local.ConfirmWidget = instance.Widget.extend({

    events: {   // This is event inside event.
        'click button.ok_button1': function () {
            this.trigger('user_chose_event', true);  // Raises the event(user_chose_event) when the ok_button1 is clicked, and passes the parameter to the function that will respond to the event
        },
        'click button.cancel_button1': function () { //We can then set up a parent event instantiating our generic widget and listening to the user_chose event using on():
            this.trigger('user_chose_event', false);
        }
    },
    start: function() {
        this.$el.append("<div>Are you sure you want to perform this action for this operation?</div>" +
            "<button class='ok_button1'>Ok Perform</button>" +
            "<button class='cancel_button1'>Cancel it</button>");
    },
});


local.ColorInputWidget = instance.Widget.extend({

    template : 'ColorInputWidget',
    events : {
        'change input' : function(){

          var color = ["#",this.$(".oe_color_red").val(),this.$el.find(".oe_color_green").val(),this.$(".oe_color_blue").val()].join('');
          //this.$el.find('.display .thespan').css("background-color", color);
          //OR
          this.$('.display .thespan').css("background-color", color).text('This is the new Text, that you must use all the time from now on. Thanks and Regards');

          $('#mydisplay span').css("background-color", color); //jquery global to find and select

          $('.oe_color_div').css("background-color", color);
        },
    },
});


local.MyDisplayWidget = instance.Widget.extend({
template : 'MyDisplayWidget' ,
});

/////////////////////////////////////////////////////////////////

// USING EVENTS WIDGETS ENDS HERE

/////////////////////////////////////////////////////////////////




//////////////////////////////////////////////////////////////////
// Modify existing widgets and classes
//////////////////////////////////////////////////////////////////

TestClass = instance.web.Class.extend({
    testMethod: function() {
        return "hello";
    },
});

//This system is similar to the inheritance mechanism, except it will alter the target class in-place instead of creating a new class.
TestClass.include({  // Just similar to _inherit parameter, and function overriding in odoo. Affects the parent class members
 testMethod: function() {
        return this._super() + " world include";
    },
});

w = TestClass.extend({   //a class extending another class. Just similar to python extend. The parent class members are not affected
    testMethod: function() {
        return this._super() + " world extending";
    },
});

alert(new TestClass().testMethod());
alert(new w().testMethod());

//////////////////////////////////////////////////////////////////////
////   Modify existing widgets and classes Ends here
////////////////////////////////////////////////////////////////////






//////////////////////////////////////////////////////////////////////////////
/// Communication with the Odoo Server WIDGETS
//////////////////////////////////////////////////////////////////////////////

local.ModelMessage = instance.Widget.extend({
    start: function() {
        var myself = this;
        var model = new instance.web.Model("oepetstore.message_of_the_day");
        model.call("my_method", [1,2,3],{context: new instance.web.CompoundContext({'myVarKey':'The Variable Context from the javascript module'})}).then(function(result) {
            myself.$el.append("<div>Hello " + result.hello_key + "</div>");  // check the xhr on your browser to see what was returned
            // will show "Hello world" to the user
        });
    },
});

//////////////////////////////////////////////////////////////////////////////
/// Communication with the Odoo Server WIDGETS Ends here
//////////////////////////////////////////////////////////////////////////////



//////////////////////////////////////////////////////////////////////////////
// Using Queries / Calling Methods WIDGETS
//////////////////////////////////////////////////////////////////////////////

local.MessageOfTheDay = instance.Widget.extend({ //creates the new widget class
    template : 'MessageOfTheDay',  // the view of the widget
    start :  function(){
           var self = this;   // when calling odoo model, we must assign the "this" object to any local variable and then use it
           var modelObj = new instance.web.Model('oepetstore.message_of_the_day');
           modelObj.query(['message']).order_by().order_by('-create_date', '-id').filter().limit(15).all().then(
               function(myresult){
                       self.$el.find('.oe_mywidget_message_of_the_day').text(myresult[0].message);

                       for (i in myresult) {
                            self.$('.oe_mywidget_message_of_the_day').append((myresult[i].message)+ '<br />');
                        }

               }
           );
           //OR  so query() combines search() and read() together
//           modelObj.call('search',[],{'limit:15})
//            .then(function (ids) {
//                return modelObj.call('read', [ids, ['message']]);
//            })
//            .then(function (result) {
//                // do work with users records
//                alert(result);
//            });
    },

});



 local.PetToyWidget = instance.Widget.extend({
        template: 'PetToyWidget',
        events : { 'click .oe_petstore_pettoy': 'selected_item',
        },
        start : function(){
            var self = this ;
            var modelProduct = new instance.web.Model('product.product');
            modelProduct.query(['name','image']).filter([['categ_id.name', '=', "Pet Toys"]]).limit(5).all().then(

               function(myres){


                    _(myres).each(function (itm) {
                        //Better than the below options

                        self.$el.append(instance.web.qweb.render('PetToy', {'mitem': itm}));

                    });

                    //OR JUST CREATE THE TEMPLATE AND APPEND.
                    _(myres).each(function (item) {
                        var htmltoappend = '<p><t t-esc="item.name"/></p>' +
                          '<p><img t-att-src="data:image/jpg;base64,' + item.image + '"/></p>'
                        self.$('.oe_petstore_pettoy_extra').append(htmltoappend);
                    });

                    //OR OlD Loop way. But use the above way
                    for (i in myres) {
                           var htmltoappend = '<p><t t-esc="item.name"/></p>' +
                          '<p><img t-att-src="data:image/jpg;base64,' + i.image + '"/></p>'
                        self.$('.oe_petstore_pettoy_extra1').append((htmltoappend));
                     }

               }
            );

        },
        selected_item : function(event){
               console.log(event);
            this.do_action({

                type: 'ir.actions.act_window',
                res_model: 'product.product',
                res_id: $(event.currentTarget).data('id'),
                views: [[false, 'form']],
                target : 'new',
            });

        },
 });
//////////////////////////////////////////////////////////////////////////////
// Using Queries / Calling Methods WIDGETS Ends Here
//////////////////////////////////////////////////////////////////////////////




///////////////////////////////////////////////////////////////////////////////
/// Creating a New Type of Field (Overridding a Field) Starts Here
////////////////////////////////////////////////////////////////////////////

//This Class is an Instance of the AbstractField Class. Whateever program that must use this class, must create an object from the class.
local.FieldChar2 = instance.web.form.AbstractField.extend({

    init: function() {

    this._super.apply(this, arguments);
    this.set("value", "");

    },
    start: function() {
            this.on("change:effective_readonly", this, function() {
                this.display_field();
                this.render_value(); // gets value from the widget or from the input field. The input field appears when in edit mode, and the widget field appears when on readonly mode
            });
            this.display_field();
            return this._super();
        },
     display_field: function() {
            var sef = this;
            console.log('This is the Widget Object: '+ this); // this will show you the Widget object
             console.log(this)
              console.log(sef)
            this.$el.html(QWeb.render("FieldChar2", {widgt: this}));
            if (! this.get("effective_readonly")) {
                this.$("input").change(function() {
                    //Note "this" represents the "input" field object and no longer represents the widget object. That is why we initialize a var object at the top, so that the input object can have access to the widget object
                     console.log('This (this) is the Input Object: ' ); // this will show you the input object
                    console.log(this)
                    console.log('This (sef) is the Widget Object: '); // this will show you the Widget object
                     console.log(sef)
                   sef.internal_set_value(sef.$("input").val()); //This will take the value in the temporary input field and put it inside the widget. So on readonly mode, the widget fields shows, but on write mode the new input field shows.
                });
            }
        },
    render_value: function() {
        if (this.get("effective_readonly")) {
            this.$el.text(this.get("value"));  // get the widget value in readonly mode
        } else {
            this.$("input").val(this.get("value")); // get the input field value when in write mode
        }

    },


});
instance.web.form.widgets.add('char2', 'instance.oepetstore.FieldChar2');



local.FieldMyColor = instance.web.form.AbstractField.extend({
        init : function(){
            this._super.apply(this, arguments);
            this.set("value", "");
        },

        start : function(){
            this.on("change:effective_readonly", this, function() {
                this.display_field();
                this.render_value(); // gets value from the widget or from the input field. The input field appears when in edit mode, and the widget field appears when on readonly mode
            });
            this.field_manager.on("field_changed:field1", this, this.field1changed);  // Watch and react to another field for changes
            this.display_field();
            return this._super();
        },
        field1changed : function(){
            var field1 = this.field_manager.get_field_value("field1");
            alert('Current Target Value for Field1 using field manager :'+ field1 );
            this.field_manager.set_values({field4: parseInt(this.field_manager.get_field_value('field1'))});
        },
        display_field : function(){
                var self = this
                this.$el.html(QWeb.render("FieldtheColor", {wid: this}));
                if (! this.get("effective_readonly")) { //write mode
                    this.$("input").change(function() {
                       self.internal_set_value(self.$("input").val()); //This will take the value in the temporary input field and put it inside the widget. So on readonly mode, the widget fields shows, but on write mode the new input field shows.
                    });
                }
        },

        render_value : function(){
                if (this.get("effective_readonly")) {  //readonly mode
                    this.$(".oe_field_color_content").css("background-color", this.get("value") || "#FFFFFF");  // get the widget value in readonly mode
                } else { // read and write mode
                    this.$el.find("input").val(this.get("value") || "#FFFFFF"); // get the input field value when in write mode
                }
        },
});
instance.web.form.widgets.add('thecolor', 'instance.oepetstore.FieldMyColor');

///// OR


local.FieldColor = instance.web.form.AbstractField.extend({

    events: {
        'change input': function (e) {
            if (!this.get('effective_readonly')) {
                this.internal_set_value($(e.currentTarget).val());
            }
        },
        // This cannot work for handling events in widget variable property (effective_readonly), rather use the .on() method for binding the change event for the widget variable property
//        'change:effective_readonly' : function(e){
//                this.display_field();
//                this.render_value();
//        },

    },
//template: "FieldColor",

    init: function() {
        this._super.apply(this, arguments);
        this.set("value", "");

    },
    start: function() {
        var sup = this._super();
    // right way for binding event to widget variable property (effective_readonly)
        this.on("change:effective_readonly", this, function() {
            this.display_field();
            this.render_value();
        });
        this.display_field();
        return sup;
    },

    display_field: function() {
        if (this.get("effective_readonly")) {  //readonly mode
                   this.$el.html(QWeb.render("FieldColor1", {widget: this}));
                } else { // read and write mode
                   this.$el.html(QWeb.render("FieldColor2", {widget: this}));
                }
    },
    render_value: function() {
        if (this.get("effective_readonly")) {
            this.$(".oe_field_color_content").css("background-color", this.get("value") || "#FFFFFF");
        } else {
            this.$("input").val(this.get("value") || "#FFFFFF");
        }
    },
});
instance.web.form.widgets.add('color', 'instance.oepetstore.FieldColor');



local.addition = instance.web.form.AbstractField.extend({
    start: function() {
        var sup = this._super();
        this.field_manager.on("field_changed:field2", this, this.display_result);
        this.field_manager.on("field_changed:field3", this, this.display_result);
        this.display_result();
        return sup;

    },
    display_result: function() {
        var result = this.field_manager.get_field_value("field2") +
                     this.field_manager.get_field_value("field3");
        this.$el.text("field2 and field3 = " + result);
    }
});
instance.web.form.widgets.add('addition', 'instance.oepetstore.addition');



local.GmapWidget = instance.web.form.AbstractField.extend({

    events: {
        'click #btn_coord': function (e) {
            if (!this.get('effective_readonly')) {
                this.get_geolocation();
            }
        },
    },
    start : function(){
       var sup = this._super();
       this.field_manager.on("field_changed:latitude", this, this.display_map);
       this.field_manager.on("field_changed:longitude", this, this.display_map);
       this.on("change:effective_readonly", this, function() {
            this.display_map();
        });
        this.get_geolocation();
        return sup ;
    },
    get_geolocation : function(){
        var self = this ;
        navigator.geolocation.getCurrentPosition(function(position){
            self.field_manager.set_values({'latitude': position.coords.latitude,'longitude':position.coords.longitude});
            self.display_map();
        });
    },
    // OR
//    get_geolocation : function(){
//        navigator.geolocation.getCurrentPosition(this.proxy('ok'));
//    },
//    ok : function(position){
//            this.field_manager.set_values({'latitude': position.coords.latitude,'longitude':position.coords.longitude});
//            this.display_map();
//
//    },

    display_map : function(){
       var lat = this.field_manager.get_field_value('latitude');
       var long = this.field_manager.get_field_value('longitude');
       this.$el.html(QWeb.render("GoogleMap",{'latitude': lat, 'longitude': long, 'wi':this}));
    },

});
instance.web.form.widgets.add('gmap', 'instance.oepetstore.GmapWidget');


///////////////////////////////////////////////////////////////////////////////
/// Creating a New Type of Field (Overridding a Field)  ends here
////////////////////////////////////////////////////////////////////////////



///////////////////////////////////////////////////////////////////////////////
//  The Form View Custom Widgets (Creating a new widget) Starts Here
//////////////////////////////////////////////////////////////////////////////

//This example did not work. So it was commented
//local.WidgetCoordinates = instance.web.form.FormWidget.extend({
//    events: {
//        'click button': function () {
//            navigator.geolocation.getCurrentPosition(
//                this.proxy('received_position'));
//        }
//    },
//    start: function() {
//        var sup = this._super();
//        this.field_manager.on("field_changed:provider_latitude", this, this.display_map);
//        this.field_manager.on("field_changed:provider_longitude", this, this.display_map);
//        this.on("change:effective_readonly", this, this.display_map);
//        this.display_map();
//        return sup;
//    },
//    display_map: function() {
//        this.$el.html(QWeb.render("WidgetCoordinates", {
//            "latitude": this.field_manager.get_field_value("provider_latitude") || 0,
//            "longitude": this.field_manager.get_field_value("provider_longitude") || 0,
//        }));
//        this.$("button").toggle(! this.get("effective_readonly"));
//    },
//    received_position: function(obj) {
//        this.field_manager.set_values({
//            "provider_latitude": obj.coords.latitude,
//            "provider_longitude": obj.coords.longitude,
//        });
//    },
//});
//
//instance.web.form.custom_widgets.add('coordinates', 'instance.oepetstore.WidgetCoordinates');


/////////////////////////////////////////////////////////////////////////////
//  The Form View Custom Widgets (Creating a new widget)  Ends Here
//////////////////////////////////////////////////////////////////////////////









}