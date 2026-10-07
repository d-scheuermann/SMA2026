import matplotlib.pyplot as plt

# 1. Definição das variáveis do Método Congruente Linear
X0 = 12345
a = 1664525
c = 1013904223
M = 2**32

quantidade = 1000
X = X0
numeros_aleatorios = []

# 2. Geração dos 1.000 números
for _ in range(quantidade):
    X = (a * X + c) % M
    U = X / M  # Normalização para o intervalo [0, 1)
    numeros_aleatorios.append(U)

# 3. Exportar os 1.000 números para um arquivo .txt (Para envio na atividade)
with open("1000_numeros_pseudoaleatorios.txt", "w") as arquivo:
    for i, num in enumerate(numeros_aleatorios):
        arquivo.write(f"{i+1}: {num:.8f}\n")
print("Arquivo '1000_numeros_pseudoaleatorios.txt' gerado com sucesso!")

# 4. Geração do Gráfico de Dispersão (U_n vs U_{n+1})
# Isso cria os pares (X, Y) deslocando a lista em 1 posição
eixo_x = numeros_aleatorios[:-1]
eixo_y = numeros_aleatorios[1:]

plt.figure(figsize=(8, 8))
plt.scatter(eixo_x, eixo_y, alpha=0.6, edgecolors='none', c='blue', s=15)
plt.title('Gráfico de Dispersão - Método Congruente Linear\n$U_n \\times U_{n+1}$')
plt.xlabel('Número Pseudoaleatório $U_n$')
plt.ylabel('Próximo Número $U_{n+1}$')
plt.xlim(0, 1)
plt.ylim(0, 1)
plt.grid(True, linestyle='--', alpha=0.5)

# Salva a imagem do gráfico (Para envio na atividade)
plt.savefig("grafico_dispersao.png", dpi=300, bbox_inches='tight')
plt.show()