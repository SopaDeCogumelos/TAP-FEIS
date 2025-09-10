"""
    Disciplina: Tópicos Avançados de Programação
    Professor: Christiane Marie Schweitzer
    Aluno: Luis Felipe Marcon Brunhara

"""

# --- INICIO Bloco de import ---

from datetime import datetime

# --- FIM Bloco de import ---

# --- INICIO Bloco de classes ---

""" 
    Classe Produto
    Atributos:
        nome: Nome do produto
        marca: Marca do produto
        preco: Preço do produto
"""
class Produto:
    def __init__(self, nome, marca, preco):
        self.nome = nome
        self.marca = marca
        self.preco = preco

""" 
    Classe Refrigerado (herda de Produto)
    Atributos:
        nome: Nome do produto
        marca: Marca do produto
        preco: Preço do produto
        temperatura: Temperatura de armazenamento
        validade: Data de validade
        fabricacao: Data de fabricação
"""
class Refrigerado(Produto):
    def __init__(self, nome, marca, preco, temperatura, validade, fabricacao):
        super().__init__(nome, marca, preco)
        self.temperatura = temperatura
        self.validade = datetime.strptime(validade, '%d/%m/%Y').date()
        self.fabricacao = datetime.strptime(fabricacao, '%d/%m/%Y').date()

"""
    Classe NaoPerecivel (herda de Produto)
    Atributos:
        nome: Nome do produto
        marca: Marca do produto
        preco: Preço do produto
        fabricacao: Data de fabricação
"""
class NaoPerecivel(Produto):
    def __init__(self, nome, marca, preco, fabricacao):
        super().__init__(nome, marca, preco)
        self.fabricacao = datetime.strptime(fabricacao, '%d/%m/%Y').date()

# --- FIM Bloco de classes ---

# --- INICIO Main ---
def main():

    return
# --- FIM Main ---

# --- Call for main function ---
if __name__ == '__main__':
    main()