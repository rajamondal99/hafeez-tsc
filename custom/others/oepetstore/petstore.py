from openerp import api, fields, models

class message_of_the_day(models.Model):
    _name = "oepetstore.message_of_the_day"

    @api.model
    def my_method(self,a,b,c):
        ctxvar = self.env.context.get('myVarKey')

        return {"hello_key": "world this is kingsley from the model and %s ,%s , %s and also context: %s " % (a,b,c,ctxvar)}

    message = fields.Text()
    color = fields.Char(size=20)


class product(models.Model):
    _inherit = "product.product"

    max_quantity = fields.Float(string="Maximum Quantity")


class fields(models.Model):
    _name = 'field.field'

    field1 = fields.Text('This is Text field1')
    field2 = fields.Char('This is Char field2')
    field3 = fields.Char('This is Char field3')
    field4 = fields.Float('This is float field4')
    latitude = fields.Float('Latitude')
    longitude = fields.Float('Longitude')
    field5 = fields.Float('This is float field5')
    field6 = fields.Float('This is float field6')
