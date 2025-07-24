{
    'name': 'Real Estate',

    'description': 'This is the tutorial module',

    'summary': 'Tutorial module',

    'license': 'LGPL-3',

    'category':'Real Estate/Brokerage',

    'application': True,

    'data': [
        'security/ir.model.access.csv',
        'security/estate_security.xml',
        'data/estate.property.type.csv',
        'views/estate_property_views.xml',
        'views/estate_property_offer_views.xml',
        'views/estate_property_type_views.xml',
        'views/estate_property_tag_views.xml',
        'views/res_partner_views.xml',
        'views/res_users_views.xml',
        'views/estate_menu_views.xml',
    ],
    
    'demo': [
        'data/demo_data.xml',
    ],

}