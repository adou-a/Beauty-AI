ingredient_tool = {
'type': 'function',
'function':{
'name': 'search_ingredient',
'description': '查询护肤成分信息',
'parameters': {
    'type': 'object',
    'properties': {
        'name': {
            'type': 'string',
            'description': '成分名称'
        }
    },
    'required': ['name']
}
}
}