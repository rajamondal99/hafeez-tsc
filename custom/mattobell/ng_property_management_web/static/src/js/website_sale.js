odoo.define('ng_property_management_web.website_sale', function (require) { 
"use strict";
var ajax = require('web.ajax');
var core = require('web.core');
var _t = core._t;
var base = require('web_editor.base');
var Model = require('web.Model');
function update_product_image(event_source, product_id) {
    var $img = $(event_source).closest('tr.js_product, .oe_website_sale').find('span[data-oe-model^="product."][data-oe-type="image"] img:first, img.product_detail_img');
    $img.attr("src", "/web/image/product.product/" + product_id + "/image");
    $img.parent().attr('data-oe-model', 'product.product').attr('data-oe-id', product_id)
        .data('oe-model', 'product.product').data('oe-id', product_id);
}
    
$('.oe_website_sale').each(function () {

    var oe_website_sale = this;
    function price_to_str(price) {
        price = Math.round(price * 100) / 100;
        var dec = Math.round((price % 1) * 100);
        return price + (dec ? '' : '.0') + (dec%10 ? '' : '0');
    }
    
    $(oe_website_sale).on('change', 'input.js_variant_change, select.js_variant_change, ul[data-attribute_value_ids]', function (ev) {
        var $ul = $(ev.target).closest('.js_add_cart_variants');
        var $parent = $ul.closest('.js_product');
        var $product_id = $parent.find('input.product_id').first();
        var $price = $parent.find(".oe_price:first .oe_currency_value");
        var $default_price = $parent.find(".oe_default_price:first .oe_currency_value");
        var $optional_price = $parent.find(".oe_optional:first .oe_currency_value");
        var variant_ids = $ul.data("attribute_value_ids");
        var values = [];
        $parent.find('input.js_variant_change:checked, select.js_variant_change').each(function () {
            values.push(+$(this).val());
        });
        $parent.find("label").removeClass("text-muted css_not_available");

        var product_id = false;
        for (var k in variant_ids) {
            if (_.isEmpty(_.difference(variant_ids[k][1], values))) {
                $price.html(price_to_str(variant_ids[k][2]));
                $default_price.html(price_to_str(variant_ids[k][3]));
                if (variant_ids[k][3]-variant_ids[k][2]>0.2) {
                    $default_price.closest('.oe_website_sale').addClass("discount");
                    $optional_price.closest('.oe_optional').show().css('text-decoration', 'line-through');
                } else {
                    $default_price.closest('.oe_website_sale').removeClass("discount");
                    $optional_price.closest('.oe_optional').hide();
                }
                product_id = variant_ids[k][0];
                break;
            }
        }

        if (product_id) {
            update_product_image(this, product_id);
        }
        $parent.find(".oe_installment_price_h4").addClass('hidden');
        ajax.jsonRpc("/shop/get_installments", 'call', {'product_id': product_id})
            .then(function (installment) {
                if (installment.length > 0){
                    $('#installment_div').removeClass("hidden")
                    $('#installments').empty()
                    $('#installments').append("<option selected='selected' value='0' >" + ' Select Installment'+ "</option>")
                   for (var i in installment) { 
                       $('#installments').append("<option value='" +installment[i].id+ "' data-amount='" +installment[i].amount+ "' data-installment_no='" +installment[i].installment_no+ "'>" +installment[i].name+ "</option>")
                    }
                } else {
                    $('#installment_div').hide()
                 }
            });
        
        $parent.find("#installments").on('change', function(){
            var selected = $(this).find('option:selected');
            var sale_amount = selected.data('amount');
            var installment_number = selected.data('installment_no');
            var installment_amount = sale_amount / installment_number
            $parent.find(".oe_price:first .oe_currency_value").html(price_to_str(+sale_amount) );
            $parent.find(".oe_installment_price_h4").removeClass('hidden');
            $parent.find(".oe_installment_price:first .oe_currency_value").html(price_to_str(+installment_amount) );
        })
        $parent.find("input.js_variant_change:radio, select.js_variant_change").each(function () {
            var $input = $(this);
            var id = +$input.val();
            var values = [id];

            $parent.find("ul:not(:has(input.js_variant_change[value='" + id + "'])) input.js_variant_change:checked, select").each(function () {
                values.push(+$(this).val());
            });

            for (var k in variant_ids) {
                if (!_.difference(values, variant_ids[k][1]).length) {
                    return;
                }
            }
            $input.closest("label").addClass("css_not_available");
            $input.find("option[value='" + id + "']").addClass("css_not_available");
        });
        
        if (product_id) {
            $parent.removeClass("css_not_available");
            $product_id.val(product_id);
            $parent.find("#add_to_cart").removeClass("disabled");
        } else {
            $parent.addClass("css_not_available");
            $product_id.val(0);
            $parent.find("#add_to_cart").addClass("disabled");
        }
    });
    
    $('div.js_product', oe_website_sale).each(function () {
        $('input.js_product_change', this).first().trigger('change');
    });

    $('.js_add_cart_variants', oe_website_sale).each(function () {
        $('input.js_variant_change, select.js_variant_change', this).first().trigger('change');
    });

})
})