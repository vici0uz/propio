odoo.define('foods.pos', function(require) {
'use strict';

    var screens = require('point_of_sale.screens');
    var gui = require('point_of_sale.gui');
    var core = require('web.core');
    var framework = require('web.framework');
    var rpc = require('web.rpc');
    var _t = core._t;
    var ScreenWidget = screens.ScreenWidget;
    var QWeb = core.qweb;
    var models = require('point_of_sale.models');

    // models.load_fields("product.pro")

    var ImprimirTicketWidget = screens.ReceiptScreenWidget.extend({
        template: 'ImprimirTicketCocinaWidget',
        click_next: function() {
        this.gui.show_screen('products');
        },
        click_back: function() {
            this.gui.show_screen('products');
        },
        print_web: function() {
            var self = this;

            console.log('sapee!');
            framework.blockUI();
            rpc.query({
                model: 'cocina.orden',
                method: 'crear_orden_desde_pos',
                args: [self.pos.get('selectedOrder').export_as_JSON()]}).then(function(result) {
                    self.hook_create_sale_order_success(result);
                });

                },
        hook_create_sale_order_success: function(result) {
            framework.unblockUI();
        }
        // window.print();
    });

    var _super_ = models.Orderline.prototype;
    var OrderLineExtendida = models.Orderline.extend({


        initialize: function(session, attributes) {
            return _super_.initialize.call(this, session, attributes);
        },

        es_cocinable_xd: function() {
            console.log(this.get_product().type);
            return this.get_product().type;
        }


    });

    models.load_fields('product.product', ['type']);
/*--------------------------------------*\
 |         THE RECEIPT SCREEN           |
\*======================================*/

// The receipt screen displays the order's
// receipt and allows it to be printed in a web browser.
// The receipt screen is not shown if the point of sale
// is set up to print with the proxy. Altough it could
// be useful to do so...

var TicketScreenWidget = ScreenWidget.extend({
    template: 'ImprimirTicketCocinaWidget',
    show: function() {
        this._super();
        var self = this;

        this.render_change();
        this.render_receipt();
        this.handle_auto_print();
    },
    handle_auto_print: function() {
        if (this.should_auto_print()) {
            this.print();
            if (this.should_close_immediately()) {
                this.click_next();
            }
        } else {
            this.lock_screen(false);
        }
    },
    should_auto_print: function() {
        return this.pos.config.iface_print_auto && !this.pos.get_order()._printed;
    },
    should_close_immediately: function() {
        var order = this.pos.get_order();
        var invoiced_finalized = order.is_to_invoice() ? order.finalized : true;
        return this.pos.config.iface_print_via_proxy && this.pos.config.iface_print_skip_screen && invoiced_finalized;
    },
    lock_screen: function(locked) {
        this._locked = locked;
        if (locked) {
            this.$('.next').removeClass('highlight');
        } else {
            this.$('.next').addClass('highlight');
        }
    },
    get_receipt_render_env: function() {
        var order = this.pos.get_order();
        return {
            widget: this,
            pos: this.pos,
            order: order,
            receipt: order.export_for_printing(),
            orderlines: order.get_orderlines(),
            paymentlines: order.get_paymentlines(),
        };
    },
    print_web: function() {
        var self = this;

        if ($.browser.safari) {
            document.execCommand('print', false, null);

            console.log('sapee!');
            framework.blockUI();
            rpc.query({
                model: 'cocina.orden',
                method: 'crear_orden_desde_pos',
                args: [self.pos.get('selectedOrder').export_as_JSON()]}).then(function(result) {
                    self.hook_create_sale_order_success(result);
                });
        } else {
            try {
                window.print();
                console.log('sapee!');
                framework.blockUI();
                rpc.query({
                model: 'cocina.orden',
                method: 'crear_orden_desde_pos',
                args: [self.pos.get('selectedOrder').export_as_JSON()]}).then(function(result) {
                    self.hook_create_sale_order_success(result);
                });
            } catch(err) {
                if (navigator.userAgent.toLowerCase().indexOf("android") > -1) {
                    this.gui.show_popup('error',{
                        'title':_t('Printing is not supported on some android browsers'),
                        'body': _t('Printing is not supported on some android browsers due to no default printing protocol is available. It is possible to print your tickets by making use of an IoT Box.'),
                    });
                } else {
                    throw err;
                }
            }
        }
        this.pos.get_order()._printed = true;
    },
    hook_create_sale_order_success: function(result) {
            framework.unblockUI();
        },
    print_xml: function() {
        var receipt = QWeb.render('XmlReceipt', this.get_receipt_render_env());

        this.pos.proxy.print_receipt(receipt);
        this.pos.get_order()._printed = true;
    },
    print: function() {
        var self = this;

        if (!this.pos.config.iface_print_via_proxy) { // browser (html) printing

            // The problem is that in chrome the print() is asynchronous and doesn't
            // execute until all rpc are finished. So it conflicts with the rpc used
            // to send the orders to the backend, and the user is able to go to the next
            // screen before the printing dialog is opened. The problem is that what's
            // printed is whatever is in the page when the dialog is opened and not when it's called,
            // and so you end up printing the product list instead of the receipt...
            //
            // Fixing this would need a re-architecturing
            // of the code to postpone sending of orders after printing.
            //
            // But since the print dialog also blocks the other asynchronous calls, the
            // button enabling in the setTimeout() is blocked until the printing dialog is
            // closed. But the timeout has to be big enough or else it doesn't work
            // 1 seconds is the same as the default timeout for sending orders and so the dialog
            // should have appeared before the timeout... so yeah that's not ultra reliable.

            this.lock_screen(true);

            setTimeout(function(){
                self.lock_screen(false);
            }, 1000);

            this.print_web();
        } else {    // proxy (xml) printing
            this.print_xml();
            this.lock_screen(false);
        }
    },
    click_next: function() {
        this.pos.get_order().finalize();
    },
    click_back: function() {
        // Placeholder method for ReceiptScreen extensions that
        // can go back ...
        this.gui.show_screen('products');

    },
    renderElement: function() {
        var self = this;
        this._super();
        this.$('.next').click(function(){
            if (!self._locked) {
                self.click_next();
            }
        });
        this.$('.back').click(function(){
            if (!self._locked) {
                self.click_back();
            }
        });
        this.$('.button.print').click(function(){
            if (!self._locked) {
                self.print();
            }
        });

    },
    render_change: function() {
        var self = this;
        this.$('.change-value').html(this.format_currency(this.pos.get_order().get_change()));
        var order = this.pos.get_order();
        var order_screen_params = order.get_screen_data('params');
        var button_print_invoice = this.$('h2.print_invoice');
        if (order_screen_params && order_screen_params.button_print_invoice) {
            button_print_invoice.show();
        } else {
            button_print_invoice.hide();
        }
    },
    render_receipt: function() {
        this.$('.pos-receipt-container').html(QWeb.render('CocinaTicket', this.get_receipt_render_env()));
    },
});
    gui.define_screen({name: 'ticket', widget: TicketScreenWidget});


    // gui.define_screen({name: 'bill', widget: ImprimirTicketWidget});



    var ImprimirTicketCocinaBtn = screens.ActionButtonWidget.extend({
        template: 'ImprimirTicketCocinaBtn',
        auto_back: true,

        button_click: function() {
            this.gui.show_screen('ticket');
     //     var order = self.pos.get_order();
     //         var lines = jQuery.extend(true, {}, order['orderlines']['models']);

     // //looping through each line
     //         $.each(lines, function(k, line){
     //         console.log(line);
     //         line.set_quantity('remove');
        // });
        console.log('hola papi');

        },

        is_visible: function() {
            return this.pos.get_order().orderlines.length > 0;
        }
    });

    screens.define_action_button({
        'name': 'OrderLine_Clear',
        'widget': ImprimirTicketCocinaBtn,
    });


    models.Orderline = OrderLineExtendida;
});
