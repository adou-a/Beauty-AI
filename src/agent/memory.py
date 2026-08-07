class ConversationMemory:

    def __init__(self):
        
        self.messages = [
            {
                'role': 'system',
                'content':
                '''
                你是一个专业护肤分析助手
                你可以调用工具解决问题
                '''
            }
        ]




    def add_message(self,message):

        self.messages.append(message)


    def get_messages(self):
        return self.messages



