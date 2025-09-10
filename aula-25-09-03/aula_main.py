"""
    Author: Luis F. M. Brunhara
    Date: 2025-09-03

    Description: Aula 3

    Não é bem o que pediu, mas acho que serve. :3
    Alias, meu GitHub:  https://github.com/SopaDeCogumelos?tab=repositories
"""

class Eletrico:
    def __init__(self, potencia, voltage):
        # super().__init__() removed. Initialization is handled by the child class.
        allowed_voltages = ['127V', '220V', 'Bivolt']
        if voltage not in allowed_voltages:
            raise ValueError(f"Voltagem inválida. Use uma das opções: {allowed_voltages}")

        self.potencia = potencia   # in Watts
        self.voltage = voltage

    def __str__(self):
        return (
            f'Eletrico(potencia={self.potencia}W, '
            f'voltage={self.voltage})'
        )


class Produto:
    def __init__(self, nome, preco, subcategoria):
        super().__init__() # Call the next __init__ in the MRO.
        self.nome = nome
        self.preco = preco
        self.subcategoria = subcategoria
        self.categoria = 'Geral' # Default category

    def aplicar_desconto(self, percentual):
        if not 0 < percentual < 1:
            raise ValueError('Percentual de desconto deve estar entre 0 e 1.')
        self.preco *= (1 - percentual)

    def __str__(self):
        return (
            f'Produto(nome={self.nome}, '
            f'preco={self.preco:.2f}, '
            f'categoria={self.categoria}, '
            f'subcategoria={self.subcategoria}'
        )

class ProdutoEletrico(Eletrico, Produto):
    def __init__(self, nome, preco, subcategoria, potencia, voltage):
        # Explicitly call the __init__ of both parent classes with the correct arguments.
        Eletrico.__init__(self, potencia=potencia, voltage=voltage)
        Produto.__init__(self, nome=nome, preco=preco, subcategoria=subcategoria)
        # Set the correct category after parent initializations.
        self.categoria = 'Elétrico'

    def __str__(self):
        # Updated to include all relevant attributes.
        return (
            f'ProdutoEletrico(nome={self.nome}, '
            f'preco={self.preco:.2f}, '
            f'subcategoria={self.subcategoria}, '
            f'potencia={self.potencia}W, '
            f'voltage={self.voltage}, '
            f'categoria={self.categoria})'
        )



# --- Main Script ---
if __name__ == '__main__':
    # Create an instance of an electrical product
    try:
        liquidificador = ProdutoEletrico(
            nome='Liquidificador 500W Wallita',
            subcategoria= 'Liquidificador',
            preco=150.00,
            potencia=500,
            voltage='220V'
        )
        print(liquidificador)

        # Apply a 10% discount
        liquidificador.aplicar_desconto(0.10)
        print(f'Preço com desconto: {liquidificador.preco:.2f}')
    except ValueError as e:
        print(f'Erro: {e}')

    print('End of script.')