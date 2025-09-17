"""
    Disciplina: Tópicos Avançados de Programação
    Professor: Christiane Marie Schweitzer
    Aluno: Luis Felipe Marcon Brunhara

"""

# --- INICIO Bloco de import ---

from datetime import datetime

# --- FIM Bloco de import ---

# --- INICIO Bloco de classes ---

class Conta:
    def __init__(self, nome, valor, data_vencimento, juros):
        self.nome = nome
        self.valor = valor
        self.data_vencimento = data_vencimento
        self.taxa_juros = juros

    def __str__(self):
        return f"Conta - Empresa: {self.nome}, Valor: R${self.valor:.2f}, Vencimento: {self.data_vencimento}"
    
    def adicionar_juros(self):
        dias_atraso = (datetime.now().date() - self.data_vencimento).days
        if dias_atraso > 0:
            self.valor += self.valor * (self.taxa_juros / 100) ** dias_atraso

        
class ContaEnergia(Conta):
    def __init__(self, nome, valor, data_vencimento, juros, kwh, taxa_iluminacao, taxa_energia, imposto):
        super().__init__(nome, valor, data_vencimento, juros)
        self.consumo_kwh = kwh
        self.taxa_iluminacao = taxa_iluminacao
        self.taxa_energia = taxa_energia
        self.imposto = imposto
        self.valor = (self.consumo_kwh * self.taxa_energia) + self.taxa_iluminacao + self.imposto

    def __str__(self):
        info_base = super().__str__()
        return f"{info_base}, Consumo: {self.consumo_kwh}kWh, Taxa Iluminação: R${self.taxa_iluminacao:.2f}, Taxa Energia: R${self.taxa_energia:.2f}, Imposto: R${self.imposto:.2f}"

# --- FIM Bloco de classes ---

# --- INICIO Bloco de funções ---
def menu():
    print("\n=== Menu de Opções ===")
    print("1 - Criar Conta de Energia")
    print("2 - Adicionar Juros")
    print("3 - Listar Contas")
    print("0 - Sair")
    escolha = input("Escolha uma opção: ")
    return escolha

def ler_data():
    while True:
        try:
            data_str = input("Data de vencimento (dd/mm/aaaa): ")
            return datetime.strptime(data_str, '%d/%m/%Y').date()
        except ValueError:
            print("Data inválida! Use o formato dd/mm/aaaa")

def ler_float(mensagem):
    while True:
        try:
            return float(input(mensagem))
        except ValueError:
            print("Valor inválido! Digite um número válido")
# --- FIM Bloco de funções ---

# --- INICIO Main ---
def main():
    contas = []  # Lista para armazenar as contas
    
    try:
        while True:
            escolha = menu()
            if escolha == "1":
                nome = input("Nome da empresa: ")
                valor = 0  # O valor será calculado automaticamente
                data_vencimento = ler_data()
                juros = ler_float("Taxa de juros (% ao dia): ")
                kwh = ler_float("Consumo em kWh: ")
                taxa_iluminacao = ler_float("Taxa de iluminação fixa: ")
                taxa_energia = ler_float("Taxa por kWh: ")
                imposto = ler_float("Imposto fixo: ")
                
                conta = ContaEnergia(nome, valor, data_vencimento, juros, kwh, 
                                   taxa_iluminacao, taxa_energia, imposto)
                contas.append(conta)
                print("\nConta de energia criada com sucesso!")
                print("Detalhes da conta:")
                print(conta)
                
            elif escolha == "2":
                if not contas:
                    print("\nNenhuma conta cadastrada!")
                else:
                    for conta in contas:
                        conta.adicionar_juros()
                    print("\nJuros adicionados com sucesso!")
                    
            elif escolha == "3":
                if not contas:
                    print("\nNenhuma conta cadastrada!")
                else:
                    print("\n=== Lista de Contas ===")
                    for i, conta in enumerate(contas, 1):
                        print(f"\nConta #{i}")
                        print(conta)
                        
            elif escolha == "0":
                print("\nEncerrando o programa...")
                break
                
            else:
                print("\nOpção inválida. Tente novamente.")
                
    except Exception as e:
        print(f"\nErro inesperado: {e}")
        return
# --- FIM Main ---

# --- Call for main function ---
if __name__ == '__main__':
    main()