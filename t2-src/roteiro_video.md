# Roteiro do vídeo (≈ 1 min por slide)
1. **Capa** — apresentar o grupo e o tema: assistência técnica modelada como rede de 3 filas com retorno.
2. **Descrição** — recepção (Q1), bancada de reparo (Q2) e teste de qualidade (Q3); reprovados no teste voltam à bancada. Tempos em minutos.
3. **Modelo** — mostrar o desenho: Kendall de cada fila, intervalos de chegada/atendimento e probabilidades de roteamento; destacar o retorno Q3 → Q2.
4. **Resultados** — semente 1, 100.000 aleatórios. Q2 com 100% de utilização, população média 7,14, resposta 42,9 min e 4.059 perdas; Q1 e Q3 em ~75%. Citar a validação com o simulator.jar.
5. **Proposta** — só Q2 muda: servidores 2 → 3 e capacidade 8 → 10.
6. **Comparação** — perdas em Q2: 4.059 → 121; resposta em Q2: 42,9 → 19,9 min; Q3 sobe para 96% de utilização e 331 perdas.
7. **Conclusões** — o gargalo migrou para o teste; próximo passo: ampliar Q3 ou reduzir o retorno (20%).
