# -*- coding: utf-8 -*-

{
    'name': 'HR Performance Management',
    'version': '0.1',
    'category': 'custom',
    'description': """ HR Performance Management """,
    'author': 'Shon Puri (shonpuri@gmail.com, +91-9173765447)',
    'website': '',
    'depends': ['base', 'hr'],
    'data': [
            'security/ir.model.access.csv',
            'data/employee_seq.xml',
            'data/group_data.xml',
            'views/view_hr_performance_management.xml',
    ],
    'test': [],
    'installable': True,
    'images': [],
}
