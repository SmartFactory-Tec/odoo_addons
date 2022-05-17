{
        'name': "SmartFactory",
        'version': '1.0',
        'author': 'Hiram Muñoz',
        'category': 'Manufacturing/Tec',
        'application': True,
        'depends': [
            'base',
            'web',
        ],
        'data': [
            "./data.xml"
        ],
        'assets': {
            'web.assets_backend': [
                         'SmartFactory/static/src/js/bundle.js',
            ],
        'web.assets_qweb': [
            'SmartFactory/static/src/templates/main.xml'
        ],
        },
}
