
def main():
    show_menu()
    while True:
        try:
            choice = int(input('give a number: '))
            if choice == 1:
                check_skin_type()
            elif choice == 2:
                check_ingredient()
            elif choice == 3:
                show_about()
            elif choice == 4:
                print('感谢使用 Beauty AI Assistant')
                break
            else:
                print('请输入正确的数字')
        except ValueError:
            print('请输入一个在1-4之间的数字')


def show_menu():
    print('Beauty AI Assistant')
    print('1.肤质检测\n' \
    '2.成分查询\n' \
    '3.关于项目\n' \
    '4.退出')


def check_skin_type():
    skin_type = input('请输入肤质：').strip()
    if skin_type == '干性':
        print('建议使用保湿型护肤品')
    elif skin_type == '油性':
        print('建议使用控油型护肤品')  
    elif skin_type == '混合性':
        print('建议使用平衡型护肤品')
    else:
        print('未知肤质')   


def check_ingredient():
    ingredient = input("请输入成分：").strip().lower()
    if ingredient == '烟酰胺':
        print('美白成分 ')
    elif ingredient == '透明质酸':
        print('保湿成分')
    else:
        print('未知成分')


def show_about():
    print("Beauty AI Assistant")
    print("一个用于肤质检测和护肤成分查询的命令行项目。")


main()