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

    def __str__(self):
        """Retorna uma representação em string do produto."""
        return f"Produto: {self.nome}, Marca: {self.marca}, Preço: R${self.preco:.2f}"

""" 
    Classe Refrigerado (herda de Produto)
    Atributos:
        nome: Nome do produto
        marca: Marca do produto
        preco: Preço do produto
        temperatura: Temperatura de armazenamento
        validade: Data de validade (string no formato dd/mm/aaaa)
        fabricacao: Data de fabricação (string no formato dd/mm/aaaa)
"""
class Refrigerado(Produto):
    def __init__(self, nome, marca, preco, temperatura, validade, fabricacao):
        super().__init__(nome, marca, preco)
        self.temperatura = temperatura
        self.validade = datetime.strptime(validade, '%d/%m/%Y').date()
        self.fabricacao = datetime.strptime(fabricacao, '%d/%m/%Y').date()

    def __str__(self):
        """Estende o __str__ da classe pai com informações de refrigerado."""
        # Chama o __str__ da classe Produto
        info_base = super().__str__()
        validade_fmt = self.validade.strftime('%d/%m/%Y')
        fabricacao_fmt = self.fabricacao.strftime('%d/%m/%Y')
        return (f"{info_base}, Temp: {self.temperatura}°C, "
                f"Fabricação: {fabricacao_fmt}, Validade: {validade_fmt}")

"""
    Classe NaoPerecivel (herda de Produto)
    Atributos:
        nome: Nome do produto
        marca: Marca do produto
        preco: Preço do produto
        fabricacao: Data de fabricação (string no formato dd/mm/aaaa)
"""
class NaoPerecivel(Produto):
    def __init__(self, nome, marca, preco, fabricacao):
        super().__init__(nome, marca, preco)
        self.fabricacao = datetime.strptime(fabricacao, '%d/%m/%Y').date()

    def __str__(self):
        """Estende o __str__ da classe pai com informações de não perecível."""
        info_base = super().__str__()
        fabricacao_fmt = self.fabricacao.strftime('%d/%m/%Y')
        return f"{info_base}, Fabricação: {fabricacao_fmt}"

# --- FIM Bloco de classes ---

# --- INICIO Main ---
def main():
    try:
        leite = Refrigerado(
            nome="Leite Integral",
            marca="Marca Boa",
            preco=4.50,
            temperatura=5.0,
            validade="15/10/2025",
            fabricacao="15/10/2024"
        )

        arroz = NaoPerecivel(
            nome="Arroz Branco",
            marca="Marca Ótima",
            preco=25.00,
            fabricacao="01/01/2024"
        )

        print(leite)
        print(arroz)

    except (ValueError, IndexError) as e:
        print(f"Erro ao processar data. Verifique o formato (dd/mm/aaaa). Erro: {e}")
# --- FIM Main ---

# --- Call for main function ---
if __name__ == '__main__':
    main()