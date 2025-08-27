""""
    Author: Luis F. M. Brunhara
    Date: 2024-08-27

    Description: Aula 2 - Funções e Estruturas Condicionais
"""

def print_hello(name):
    print(f'Hello, {name}!')
    return True

if __name__ == '__main__':
    if print_hello('Python'):
        print('Function executed successfully.')
    else:
        print('Function execution failed.')
    print('End of script.')
