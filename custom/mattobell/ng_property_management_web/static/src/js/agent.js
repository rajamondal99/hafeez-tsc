odoo.define('ng_property_management_web', function (require) {
var ajax = require('web.ajax');

    $(document).ready(function () {
        $('.js_payment').find('form').click(function(){
            sale_agent = $("#sale_agent").val() 
	    branch = $("#branch").val()
            ajax.jsonRpc('/shop/payment/sale_agent/', 'call', {'sale_agent' : sale_agent, 'branch' : branch}).then(function (data) {
             });
        })
    });

})















