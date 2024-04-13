# -*- coding: utf-8 -*-

{
    'name': 'IT IS Mail cc bcc',
    'version': '0.12',
    'category': 'Discuss',
    'sequence': 25,
    'summary': 'Mailing Lists',
    'description': """
Business oriented Social Networking
===================================

It enables the users to send cc and bcc emails on SO, Invoice, All chatter and Under Discuss > Send Mail. 

    """,
    'website': 'https://www.odoo.com/',
    'depends': ['base', 'base_setup', 'mail'],
    'data': [
        'security/ir.model.access.csv',
             
    ],
    'demo': [

    ],
    'installable': True,
    'application': False,
    'icon': "/itis_mail_cc_bcc/static/src/img/icon.png",
}
