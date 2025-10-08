"""
    Disciplina: Tópicos Avançados de Programação
    Professor: Christiane Marie Schweitzer
    Aluno: Luis Felipe Marcon Brunhara
    Git: https://github.com/SopaDeCogumelos/TAP-FEIS

"""

# --- BEGIN Importações ---
import random
# --- END Importações ---

# --- BEGIN Declaração de Classes e Funções ---

def select_word():
    # Seleciona uma palavra aleatória de uma lista predefinida.
    words = ["banana", "abacaxi", "uva", "mamao", "laranja", "morango", "limao"]
    return random.choice(words).lower()

def display_hangman(attempts):
    # Exibe o estado da forca com base no número de erros.
    stages = [  # 6 erros: Final
                """
                   --------
                   |      |
                   |      O
                   |     \\|/
                   |      |
                   |     / \\
                   -
                """,
                # 5 erros
                """
                   --------
                   |      |
                   |      O
                   |     \\|/
                   |      |
                   |     /
                   -
                """,
                # 4 erros
                """
                   --------
                   |      |
                   |      O
                   |     \\|/
                   |      |
                   |
                   -
                """,
                # 3 erros
                """
                   --------
                   |      |
                   |      O
                   |     \\|
                   |      |
                   |
                   -
                """,
                # 2 erros
                """
                   --------
                   |      |
                   |      O
                   |      |
                   |      |
                   |
                   -
                """,
                # 1 erro
                """
                   --------
                   |      |
                   |      O
                   |
                   |
                   |
                   -
                """,
                # 0 erros: Inicial
                """
                   --------
                   |      |
                   |
                   |
                   |
                   |
                   -
                """
    ]
    return stages[attempts]

def play_hangman():
    # Função principal para executar o jogo da forca.

    print("--- Bem-vindo ao Jogo da Forca! ---")

    # -- BEGIN Loop Principal do Jogo ---
    while True:
        # Inicia um novo jogo
        word = select_word()
        guessed_letters = set()  # Usar um conjunto é eficiente para verificar letras já tentadas
        attempts_left = 6

        while attempts_left > 0:
            # Monta a palavra a ser exibida com as letras adivinhadas
            display_word = ""
            win = True
            for letter in word:
                if letter in guessed_letters:
                    display_word += letter + " "
                else:
                    display_word += "_ "
                    win = False # Se ainda houver um underline, o jogador não venceu

            # Exibe o estado atual do jogo
            print(display_hangman(attempts_left))
            print(f"Palavra: {display_word}")
            print(f"Letras já tentadas: {', '.join(sorted(guessed_letters))}")
            print(f"Tentativas restantes: {attempts_left}")

            # Verifica se o jogador venceu
            if win:
                print("\nParabéns! Você adivinhou a palavra!")
                print(f"A palavra era: {word.upper()}")
                break

            # Pede uma nova letra ao jogador
            guess = input("Digite uma letra: ").lower()

            # Validação da entrada do usuário
            if not guess.isalpha() or len(guess) != 1:
                print("Entrada inválida. Por favor, digite apenas UMA letra.")
                continue

            if guess in guessed_letters:
                print("Você já tentou essa letra. Tente outra.")
                continue

            # Adiciona a letra ao conjunto de letras tentadas
            guessed_letters.add(guess)

            # Verifica se a letra está na palavra
            if guess in word:
                print(f"Bom palpite! A letra '{guess}' está na palavra.")
            else:
                print(f"Errou! A letra '{guess}' não está na palavra.")
                attempts_left -= 1
   

        # Fim de jogo (derrota)
        if not win:
            print(display_hangman(attempts_left))
            print("\n--- Fim de Jogo! ---")
            print("Você foi enforcado!")
            print(f"A palavra era: {word.upper()}")

        # Pergunta se o jogador quer jogar novamente
        replay = input("Deseja jogar novamente? (s/n): ").lower()
        if replay != 's':
            print("Obrigado por jogar! Até a próxima!")
            break
        else:
            print("\nIniciando um novo jogo...\n")
            continue
            
    # -- END Loop Principal do Jogo --

# --- END Declaração de Classes e Funções ---

# --- BEGIN Programa Principal ---
if __name__ == "__main__":
    play_hangman()
# --- END Programa Principal ---