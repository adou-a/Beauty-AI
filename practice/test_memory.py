from src.agent.session_memory  import MemoryStore



def test_memory():
    store = MemoryStore()


    user1 = store.get_memory('User001')


    user1.append(
        {
            'role': 'user',
            'content': '烟酰胺是什么'
        }
    )

    user2 = store.get_memory('user002')

    print(store.sessions)


if __name__ == '__main__':
    test_memory()