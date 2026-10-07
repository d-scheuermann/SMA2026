# Simulador de Redes de Filas — T1 | Redes Generalizadas (G/G/c/K)

Disciplina: **Simulação e Métodos Analíticos** — PUCRS  
Módulo — Desenvolvimento de Simulador Generalizado para Redes de Filas

Integrantes: Letícia Davi Nunes, Guilherme Santos Terre do Amaral,
Daniel Scheuermann, João Vitor Vogel.

---

## 1. Como executar

Requisito: **Python 3.8 ou superior** (nenhuma biblioteca externa obrigatória; caso `PyYAML` esteja instalado, ele será utilizado, caso contrário o leitor YAML embutido assume a leitura).

```bash
python3 simulador.py model.yml
```

O comando acima lê o modelo definido no arquivo `model.yml` e imprime o relatório completo no terminal.

Para salvar o relatório direto em um arquivo de texto:

```bash
python3 simulador.py model.yml -o resultado.txt
```

Também é possível sobrescrever temporariamente a semente e a quantidade de aleatórios via linha de comando:

```bash
python3 simulador.py model.yml --seed 1 --n 100000
```

---

## 2. Sintaxe e Formato do Arquivo de Modelo (`.yml`)

O simulador utiliza a especificação padronizada em YAML compatível com o `simulator.jar` do Módulo 3.

```yaml
!PARAMETERS
arrivals: 
   Q1: 2.0                            # Fila inicial com primeira chegada no tempo 2.0

queues: 
   Q1: 
      servers: 1                       # Quantidade de servidores (c)
      minArrival: 2.0                  # Intervalo de chegada externa minimo
      maxArrival: 4.0                  # Intervalo de chegada externa maximo
      minService: 1.0                  # Tempo de servico minimo
      maxService: 2.0                  # Tempo de servico maximo
   Q2: 
      servers: 2
      capacity: 5                      # Capacidade total (K). Se omitido = Infinita
      minService: 4.0
      maxService: 6.0
   Q3: 
      servers: 2
      capacity: 10
      minService: 5.0
      maxService: 15.0

network: 
-  source: Q1
   target: Q2
   probability: 0.2
-  source: Q1
   target: Q3
   probability: 0.8
-  source: Q2
   target: Q1
   probability: 0.3
-  source: Q2
   target: Q3
   probability: 0.5
-  source: Q3
   target: Q2
   probability: 0.7

rndnumbersPerSeed: 100000
seeds: 
- 1
```

### Regras do Modelo:
- **Filas (`queues`)**: 
  - Fila sem `capacity` possui capacidade infinita ($G/G/c$). Com `capacity` definida, opera no modelo $G/G/c/K$.
  - Chegadas em filas lotadas contabilizam perdas (`losses`).
- **Chegadas Externas (`arrivals`)**:
  - Declaradas apenas para as filas que recebem clientes vindos do exterior da rede.
- **Roteamento (`network`)**:
  - A soma das probabilidades de saída de uma fila pode ser $\le 1.0$. A diferença restante representa a probabilidade do cliente deixar o sistema.
- **Ordem dos Aleatórios**:
  - Percorre os destinos ordenados por probabilidade crescente para o sorteio de rotas.
  - Consome aleatórios para roteamento apenas quando a fila tem mais de uma rota possível (ou saída probabilística).

---

## 3. Modelo Exigido na Atividade (`model.yml`)

A topologia simulada conta com $3$ filas interconectadas com realimentação e saídas probabilísticas:

- **Fila 1 ($Q1$)**: $G/G/1$, $1..2$ min de serviço, chegadas externas no tempo $2.0$ com intervalo de $2..4$ min.
- **Fila 2 ($Q2$)**: $G/G/2/5$, $4..6$ min de serviço.
- **Fila 3 ($Q3$)**: $G/G/2/10$, $5..15$ min de serviço.

**Roteamentos**:
- $Q1 \to Q2$ ($20\%$) | $Q1 \to Q3$ ($80\%$)
- $Q2 \to Q1$ ($30\%$) | $Q2 \to Q3$ ($50\%$) | $Q2 \to \text{Saída}$ ($20\%$)
- $Q3 \to Q2$ ($70\%$) | $Q3 \to \text{Saída}$ ($30\%$)

---

## 4. Organização do Código

| Arquivo | Conteúdo |
|---|---|
| `simulador.py` | Motor da simulação a eventos discretos, LCG de 48-bits, leitor YAML/mini-YAML e gerador de relatório. |
| `model.yml` | Modelo da rede descrita na atividade em formato YAML. |
| `README.md` | Guia de uso e especificações do projeto. |

---

## 5. Decisões de Implementação e Compatibilidade

- **Gerador Pseudoaleatório (LCG 48-bit)**:
  Mesmo gerador congruencial linear do `simulator.jar`:
  $$x_{i+1} = (25214903917 \cdot x_i + 11) \pmod{2^{48}}$$
  com $u = \frac{x_{i+1}}{2^{48}}$. Amostragens uniformes em $[a, b]$ usam $a + (b - a) \cdot u$.
- **Critério de Encerramento**: A simulação encerra no instante exato do evento em que o 100.000º número aleatório é consumido.
- **Acúmulo dos Tempos de Estado**: A contabilização dos tempos em cada estado populacional de cada fila é atualizada a cada evento ocorrido na simulação.
- **Roteamento Ordenado**: As probabilidades de destino de cada nó da rede são pré-ordenadas em ordem crescente antes de compor a soma acumulada para o sorteio do próximo destino.