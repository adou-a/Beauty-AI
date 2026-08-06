ingredient_tool_schema = {
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

search_ingredient_schema = {'type': 'function','function': {
    'name': 'check_skin_risk',
    'description': '提醒皮肤需要注意刺激性',
    'parameters':{
        'type': 'object',
        'properties':{
            'skin_type':{
                'type': 'string',
                'description': '肤质类型'
            }
        },
        'required': ['skin_type']
    }
}
}