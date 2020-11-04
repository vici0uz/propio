{
    'name': 'Lo que sea',
    'version': '0.1',
    'depends': [
        'product',
        'sale',
        'sale_management',
        'purchase',
        'stock',
        'sale',
        'hooks',
        'muk_web_client_refresh'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'views/sale.xml',
        'views/product.xml',
        'views/foods.xml',
        'views/vistas.xml'],
    'qweb': [
        'views/qweb.xml'
        ]
}
