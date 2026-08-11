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


search_knowledge_schema ={
    'type': 'function',
    'function':{
        'name': 'search_knowledge',
        'description':(
            '从护肤专业知识库检索与用户问题相关的参考资料'
            '适用于需要护肤原理、成分使用方法'
            '成分风险、肤质护肤或复杂护肤知识的问题'
        ),
        'parameters': {
            'type': 'object',
            'properties': {
                'query':{
                    'type': 'string',
                    'description':'需要从知识库检索的完整自然语言'
                }
            },
            'required': ['query']
        }
    }
}