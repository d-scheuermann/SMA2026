# Atividade T2 — Simulação de rede de filas (Assistência técnica de eletrônicos)

Disciplina: Simulação e Métodos Analíticos (PUCRS)

## Arquivos
| Arquivo | Conteúdo |
|---|---|
| `modelo_inicial.yml` / `modelo_melhorado.yml` | Modelos simulados antes e depois da melhoria |
| `resultado_inicial.txt` / `resultado_melhorado.txt` | Saída do simulador (semente 1, 100.000 aleatórios) |
| `indices_simulacao.xlsx` | Planilha com fórmulas dos índices (N, X, U, R) e comparação |
| `simulador.py` | Simulador G/G/c/K (mesmo código usado nos módulos anteriores) |
| `indices.py` | Calcula N, X, U e R a partir da simulação |

## Como executar
Requisito: Python 3.8+ (PyYAML é opcional).
```bash
python3 simulador.py modelo_inicial.yml                      # relatório no terminal
python3 simulador.py modelo_melhorado.yml -o resultado_melhorado.txt
python3 indices.py modelo_inicial.yml modelo_melhorado.yml   # índices por fila (sementes 1 a 3)
java -jar simulator.jar run modelo_inicial.yml               # verificação com o simulador do módulo 3
```
Os resultados do `simulador.py` e do `simulator.jar` são idênticos nos dois modelos (estados, tempos, perdas e tempo global).

## Fórmulas dos índices
Para cada fila, com π(n) = tempo acumulado em n / tempo total, c servidores e μ = 1/(tempo médio de atendimento), tempo médio = (mín + máx)/2:
- População: N = Σ n·π(n)
- Vazão: X = μ · Σ min(n, c)·π(n)
- Utilização: U = Σ min(n, c)·π(n) / c
- Tempo de resposta: R = N / X