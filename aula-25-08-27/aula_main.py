""""
    Author: Luis F. M. Brunhara
    Date: 2025-08-27

    Description: Aula 2 - Funções e Estruturas Condicionais
"""

def print_hello(name):
    print(f'Hello, {name}!')
    return True

def for_example():
    for i in range(10, 4, -2):
        print(f'Iteration {i}')

if __name__ == '__main__':
    if print_hello('Python'):
        print('Function executed successfully.')
    else:
        print('Function execution failed.')
    for_example()
    print('End of script.')
