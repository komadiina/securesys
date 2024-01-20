from system import System

def home_screen():
    print(f'============== kriptografijaaaaaaaa ==============')
    print(f'[R] - Register\n[L] - Login')
    print(f'> ', end = '')
    
if __name__ == '__main__':
    home_screen()
    sel = input().lower()
    
    while sel not in {'r', 'l'}:
        print(f'Invalid input, please try again.\n> ', end = '')
        sel = input().lower()
            
    if sel == 'r':
        System.register_user()
    elif sel == 'l':
        System.user_logon()