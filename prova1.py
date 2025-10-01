"""
Prova 1 - Tópicos Avançados em Programação
Nome: Luis Felipe Marcon Brunhara
"""

from enum import Enum, auto

# Enum para os cargos
class Cargo(Enum):
    ESTAGIARIO = 1
    JUNIOR = 2
    PLENO = 3
    SENIOR = 4
    GERENTE = 5

# Classe Endereco
class Endereco:
    def __init__(self, rua, numero, cidade, estado):
        self.rua = rua
        self.numero = numero
        self.cidade = cidade
        self.estado = estado

    def __str__(self):
        return f"{self.rua}, {self.numero}, {self.cidade} - {self.estado}"

# Classe Pessoa, que possui um endereço
class Pessoa:
    def __init__(self, nome, idade):
        self.nome = nome
        self.idade = idade
        self.endereco = None

    def add_endereco(self, endereco):
        self.endereco = endereco

    def __str__(self):
        return f"Nome: {self.nome}, Idade: {self.idade}"

# Subclasse Funcionario, que herda de Pessoa
class Funcionario(Pessoa):
    def __init__(self, nome, idade, cargo: Cargo, salario):
        super().__init__(nome, idade)
        if not isinstance(cargo, Cargo):
            raise TypeError("O cargo deve ser uma instância do Enum Cargo.")
        self.cargo = cargo
        self.salario = salario
        self.salario_base = salario

    def promover(self, quantidade=1):
        cargos = list(Cargo)
        try:
            indice_atual = cargos.index(self.cargo)
        except ValueError:
            # Isso não deve acontecer se o cargo for sempre um membro do Enum
            return

        # Calcula o novo índice, garantindo que não ultrapasse o cargo máximo
        novo_indice = min(indice_atual + quantidade, len(cargos) - 1)

        if indice_atual != novo_indice:
            self.cargo = cargos[novo_indice]
            self.ajustar_salario()
            print(f"{self.nome} foi promovido para {self.cargo.name}.")
        else:
            print(f"{self.nome} já está no cargo máximo ({self.cargo.name}).")


    def ajustar_salario(self):
        # Salário aumenta 10% a cada nível de cargo (usando o valor do enum)
        self.salario = self.salario_base * (1.1 ** self.cargo.value)

    def __str__(self):
        # Sobrescreve o __str__ para incluir informações do funcionário
        info_pessoa = super().__str__()
        return f"{info_pessoa}, Cargo: {self.cargo.name}, Salário: R${self.salario:.2f}"

# Funçao para adicionar um funcionário
def adicionar_funcionario(lista_funcionarios):
    """Coleta dados e adiciona um novo funcionário à lista."""
    try:
        nome = input("Nome: ")
        idade = int(input("Idade: "))

        print("Cargos disponíveis:")
        for cargo in Cargo:
            print(f"{cargo.value} - {cargo.name}")
        cargo_input = int(input("Selecione o cargo (número): "))
        cargo = Cargo(cargo_input) # Isso já pode lançar ValueError

        salario_str = input("Salário inicial: ")
        salario = float(salario_str)

        novo_funcionario = Funcionario(nome, idade, cargo, salario)
        lista_funcionarios.append(novo_funcionario)
        print(f"Funcionário {nome} adicionado com sucesso.")

    except ValueError:
        # Captura erros de conversão de int/float ou de valor de Enum inválido
        print("\nErro: Entrada inválida. Verifique os valores de idade, cargo e salário. A operação foi cancelada.")


if __name__ == "__main__":
    # Cria a lista de funcionários
    funcionarios = []
    # Cria um menu no terminal para interagir com o usuário
    while True:
        print("\nSelecione uma das opções:"
        "\n=================================="
        "\n1 - Ver lista de funcionários"
        "\n2 - Adicionar funcionário"
        "\n3 - Promover funcionário"
        "\n4 - Ver detalhes do funcionário"
        "\n5 - Editar informações do funcionário"
        "\n6 - Deletar funcionário"
        "\n7 - Gerenciar endereço do funcionário"
        "\n0 - Sair"
        "\n==================================")
        opcao = input("Opção: ")

        if opcao == "0":
            print("Saindo...")
            break
        elif opcao == "1":
            # Ver lista de funcionários
            if not funcionarios:
                print("Nenhum funcionário cadastrado.")
            else:
                for i, func in enumerate(funcionarios):
                    print(f"{i + 1}. {func.nome} - {func.cargo.name} - R${func.salario:.2f}")
        elif opcao == "2":
            adicionar_funcionario(funcionarios)
        elif opcao == "3":
            # Promover funcionário
            if not funcionarios:
                print("Nenhum funcionário cadastrado.")
                continue
            for i, func in enumerate(funcionarios):
                print(f"{i + 1}. {func.nome} - {func.cargo.name}")
            func_index = int(input("Selecione o funcionário para promover (número): ")) - 1
            if 0 <= func_index < len(funcionarios):
                quantidade = int(input("Quantos níveis de promoção? "))
                funcionarios[func_index].promover(quantidade)
            else:
                print("Funcionário inválido.")
        elif opcao == "4":
            # Ver detalhes do funcionário
            if not funcionarios:
                print("Nenhum funcionário cadastrado.")
                continue
            for i, func in enumerate(funcionarios):
                print(f"{i + 1}. {func.nome}")
            func_index = int(input("Selecione o funcionário para ver detalhes (número): ")) - 1
            if 0 <= func_index < len(funcionarios):
                print(funcionarios[func_index])
                if funcionarios[func_index].endereco:
                    print(f"Endereço: {funcionarios[func_index].endereco}")
                else:
                    print("Endereço: Não cadastrado.")
            else:
                print("Funcionário inválido.")

        elif opcao == "5":
            # Editar informações do funcionário
            if not funcionarios:
                print("Nenhum funcionário cadastrado.")
                continue
            for i, func in enumerate(funcionarios):
                print(f"{i + 1}. {func.nome}")
            func_index = int(input("Selecione o funcionário para editar (número): ")) - 1
            if 0 <= func_index < len(funcionarios):
                func = funcionarios[func_index]
                print("Deixe em branco para manter o valor atual.")

                # Atualiza nome e idade
                novo_nome = input(f"Nome ({func.nome}): ")
                if novo_nome:
                    func.nome = novo_nome

                nova_idade_str = input(f"Idade ({func.idade}): ")
                if nova_idade_str:
                    func.idade = int(nova_idade_str)

                # Lógica para atualizar o cargo
                print("Cargos disponíveis:")
                for c in Cargo:
                    print(f"{c.value} - {c.name}")
                cargo_input = input(f"Cargo ({func.cargo.name}): ")
                cargo_alterado = False
                if cargo_input:
                    try:
                        novo_cargo = Cargo(int(cargo_input))
                        if novo_cargo != func.cargo:
                            func.cargo = novo_cargo
                            cargo_alterado = True
                    except ValueError:
                        print("Cargo inválido. Mantendo o cargo atual.")

                # Atualiza o salário apenas se o cargo não foi alterado
                if cargo_alterado:
                    func.ajustar_salario()
                    print(f"Cargo alterado. Novo salário calculado: R${func.salario:.2f}")
                else:
                    novo_salario_str = input(f"Salário ({func.salario:.2f}): ")
                    if novo_salario_str:
                        func.salario = float(novo_salario_str)

                print("Informações atualizadas com sucesso.")
            else:
                print("Funcionário inválido.")

        elif opcao == "6":
            # Deletar funcionário
            if not funcionarios:
                print("Nenhum funcionário cadastrado.")
                continue
            for i, func in enumerate(funcionarios):
                print(f"{i + 1}. {func.nome}")
            func_index = int(input("Selecione o funcionário para deletar (número): ")) - 1
            if 0 <= func_index < len(funcionarios):
                confirmado = input(f"Tem certeza que deseja deletar {funcionarios[func_index].nome}? (s/n): ")
                if confirmado.lower() == 's':
                    del funcionarios[func_index]
                    print("Funcionário deletado com sucesso.")
                else:
                    print("Operação cancelada.")
            else:
                print("Funcionário inválido.")
        elif opcao == "7":
            # Gerenciar endereço
            if not funcionarios:
                print("Nenhum funcionário cadastrado.")
                continue
            for i, func in enumerate(funcionarios):
                print(f"{i + 1}. {func.nome}")
            func_index = int(input("Selecione o funcionário (número): ")) - 1
            if 0 <= func_index < len(funcionarios):
                func = funcionarios[func_index]
                print("Digite as informações do endereço.")
                rua = input("Rua: ")
                numero = input("Número: ")
                cidade = input("Cidade: ")
                estado = input("Estado: ")
                novo_endereco = Endereco(rua, numero, cidade, estado)
                func.add_endereco(novo_endereco)
                print("Endereço atualizado com sucesso.")
            else:
                print("Funcionário inválido.")
        else:
            print("Opção inválida. Tente novamente.")
