#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simulador de redes de filas por eventos discretos.

Disciplina: Simulacao e Metodos Analiticos - PUCRS
Modulo 6 - Desenvolvimento de Simulador para Filas em Tandem

Uso:
    python simulador.py <arquivo_do_modelo>

Exemplo:
    python simulador.py modelo_m6.txt

O simulador nao e especifico para duas filas em tandem: ele le a topologia da
rede (filas, capacidades, servidores, intervalos e probabilidades de roteamento)
de um arquivo texto, de modo que qualquer topologia possa ser simulada.
"""

import sys
import heapq
from math import inf


# ---------------------------------------------------------------------------
# Gerador de numeros pseudoaleatorios (congruencial linear - modulo 2)
# ---------------------------------------------------------------------------

class GeradorEsgotado(Exception):
    """Sinaliza que o ultimo numero pseudoaleatorio permitido foi consumido."""


class Gerador:
    """
    Gerador congruencial linear:  x[i+1] = (a * x[i] + c) mod M
    O numero pseudoaleatorio uniforme em [0,1) e dado por x[i+1] / M.

    A simulacao se encerra assim que o numero de aleatorios permitido
    (parametro 'aleatorios' do modelo) e atingido.
    """

    def __init__(self, semente, limite, a=1664525, c=1013904223, M=2 ** 32):
        self.a, self.c, self.M = a, c, M
        self.x = semente
        self.limite = limite
        self.usados = 0

    def proximo(self):
        if self.usados >= self.limite:
            raise GeradorEsgotado()
        self.x = (self.a * self.x + self.c) % self.M
        self.usados += 1
        return self.x / self.M

    def uniforme(self, a, b):
        """Numero uniformemente distribuido no intervalo [a, b]."""
        return a + (b - a) * self.proximo()


# ---------------------------------------------------------------------------
# Entidades
# ---------------------------------------------------------------------------

class Fila:
    """Uma fila G/G/c/K da rede."""

    def __init__(self, nome, servidores, capacidade, atendimento,
                 chegada=None, primeira_chegada=None):
        self.nome = nome
        self.servidores = servidores
        self.capacidade = capacidade            # inf => fila sem limite
        self.atendimento = atendimento          # (min, max)
        self.chegada = chegada                  # (min, max) ou None
        self.primeira_chegada = primeira_chegada
        self.status = 0                         # clientes na fila (incl. em atendimento)
        self.perdas = 0
        self.rotas = []                         # [(destino ou None, probabilidade)]
        self.tempos = {}                        # estado -> tempo acumulado

    def acumula(self, delta):
        self.tempos[self.status] = self.tempos.get(self.status, 0.0) + delta

    def tem_espaco(self):
        return self.status < self.capacidade

    def __repr__(self):
        cap = "inf" if self.capacidade == inf else int(self.capacidade)
        return "%s (G/G/%d/%s)" % (self.nome, self.servidores, cap)


class Evento:
    """
    Evento do escalonador.

    tipo == "CHEGADA": chegada de um cliente vindo do exterior da rede.
    tipo == "SAIDA"  : termino de atendimento na fila de origem. O destino
                       (outra fila ou a saida do sistema) e sorteado no momento
                       em que o evento e tratado; quando o destino e outra fila
                       o evento corresponde a uma PASSAGEM entre filas.
    """

    __slots__ = ("tempo", "tipo", "fila", "ordem")

    def __init__(self, tempo, tipo, fila, ordem):
        self.tempo, self.tipo, self.fila, self.ordem = tempo, tipo, fila, ordem

    def __lt__(self, outro):
        # Ordena pelo tempo do evento; empates sao resolvidos pela ordem de criacao.
        if self.tempo != outro.tempo:
            return self.tempo < outro.tempo
        return self.ordem < outro.ordem


class Escalonador:
    """Lista de eventos futuros, ordenada pelo tempo de ocorrencia."""

    def __init__(self):
        self.heap = []
        self.contador = 0

    def agenda(self, tempo, tipo, fila):
        self.contador += 1
        heapq.heappush(self.heap, Evento(tempo, tipo, fila, self.contador))

    def proximo(self):
        return heapq.heappop(self.heap) if self.heap else None


# ---------------------------------------------------------------------------
# Leitura do modelo
# ---------------------------------------------------------------------------

def _intervalo(texto):
    a, b = texto.split("..")
    return (float(a), float(b))


def ler_modelo(caminho):
    """
    Sintaxe do arquivo de modelo (uma instrucao por linha, '#' inicia comentario):

        semente     <inteiro>
        aleatorios  <inteiro>

        fila <nome> servidores=<n> capacidade=<n|inf> atendimento=<min>..<max>
                    [chegada=<min>..<max>] [primeira_chegada=<tempo>]

        rota <origem> -> <destino|SAIDA> : <probabilidade>

    Filas sem 'chegada' nao recebem clientes do exterior da rede.
    Se uma fila nao possuir nenhuma rota declarada, assume-se que 100% dos
    clientes atendidos deixam o sistema.
    """
    filas, rotas = {}, []
    semente, aleatorios = 1, 100000

    # utf-8-sig descarta a marca BOM que alguns editores do Windows inserem.
    with open(caminho, "r", encoding="utf-8-sig") as f:
        for numero, linha in enumerate(f, 1):
            linha = linha.split("#")[0].strip()
            if not linha:
                continue
            partes = linha.split()
            chave = partes[0].lower()

            if chave == "semente":
                semente = int(partes[1])

            elif chave == "aleatorios":
                aleatorios = int(partes[1])

            elif chave == "fila":
                nome = partes[1]
                attr = dict(p.split("=", 1) for p in partes[2:])
                filas[nome] = Fila(
                    nome=nome,
                    servidores=int(attr["servidores"]),
                    capacidade=inf if attr["capacidade"].lower() == "inf"
                               else int(attr["capacidade"]),
                    atendimento=_intervalo(attr["atendimento"]),
                    chegada=_intervalo(attr["chegada"]) if "chegada" in attr else None,
                    primeira_chegada=float(attr["primeira_chegada"])
                                     if "primeira_chegada" in attr else None,
                )

            elif chave == "rota":
                # rota F1 -> F2 : 1.0
                resto = linha[len("rota"):].replace("->", " ").replace(":", " ")
                origem, destino, prob = resto.split()
                rotas.append((origem, destino, float(prob)))

            else:
                raise ValueError("Linha %d: instrucao desconhecida '%s'" % (numero, chave))

    for origem, destino, prob in rotas:
        if origem not in filas:
            raise ValueError("Rota com origem desconhecida: %s" % origem)
        alvo = None if destino.upper() == "SAIDA" else filas[destino]
        if alvo is None and destino.upper() != "SAIDA" and destino not in filas:
            raise ValueError("Rota com destino desconhecido: %s" % destino)
        filas[origem].rotas.append((alvo, prob))

    for fila in filas.values():
        if not fila.rotas:
            fila.rotas = [(None, 1.0)]

    return list(filas.values()), semente, aleatorios


# ---------------------------------------------------------------------------
# Simulacao
# ---------------------------------------------------------------------------

class Simulador:

    def __init__(self, filas, semente, aleatorios):
        self.filas = filas
        self.gerador = Gerador(semente, aleatorios)
        self.escalonador = Escalonador()
        self.tempo = 0.0

    # -- contabilizacao de tempo ------------------------------------------
    def acumula_tempo(self, instante):
        delta = instante - self.tempo
        for fila in self.filas:
            fila.acumula(delta)
        self.tempo = instante

    # -- agendamentos ------------------------------------------------------
    def agenda_chegada(self, fila, instante):
        self.escalonador.agenda(instante, "CHEGADA", fila)

    def agenda_saida(self, fila, instante):
        self.escalonador.agenda(instante, "SAIDA", fila)

    def sorteia_destino(self, fila):
        """
        Sorteia o destino de um cliente que terminou o atendimento em 'fila'.
        Quando ha um unico destino possivel nao se consome numero aleatorio,
        pois o roteamento e deterministico.
        """
        if len(fila.rotas) == 1:
            return fila.rotas[0][0]
        u = self.gerador.proximo()
        acumulado = 0.0
        for destino, prob in fila.rotas:
            acumulado += prob
            if u < acumulado:
                return destino
        return fila.rotas[-1][0]

    # -- entrada de um cliente em uma fila --------------------------------
    def entra(self, fila):
        if fila.tem_espaco():
            fila.status += 1
            if fila.status <= fila.servidores:
                self.agenda_saida(fila, self.tempo + self.gerador.uniforme(*fila.atendimento))
        else:
            fila.perdas += 1

    # -- tratamento dos eventos -------------------------------------------
    def trata_chegada(self, evento):
        fila = evento.fila
        self.acumula_tempo(evento.tempo)
        self.entra(fila)
        self.agenda_chegada(fila, self.tempo + self.gerador.uniforme(*fila.chegada))

    def trata_saida(self, evento):
        fila = evento.fila
        self.acumula_tempo(evento.tempo)
        fila.status -= 1
        if fila.status >= fila.servidores:
            self.agenda_saida(fila, self.tempo + self.gerador.uniforme(*fila.atendimento))
        destino = self.sorteia_destino(fila)
        if destino is not None:          # PASSAGEM de uma fila para outra
            self.entra(destino)

    # -- laco principal ----------------------------------------------------
    def executa(self):
        for fila in self.filas:
            if fila.primeira_chegada is not None:
                self.agenda_chegada(fila, fila.primeira_chegada)

        while True:
            evento = self.escalonador.proximo()
            if evento is None:
                break
            try:
                if evento.tipo == "CHEGADA":
                    self.trata_chegada(evento)
                else:
                    self.trata_saida(evento)
            except GeradorEsgotado:
                # O ultimo numero pseudoaleatorio permitido foi consumido:
                # a simulacao se encerra no instante do evento corrente.
                break


# ---------------------------------------------------------------------------
# Relatorio
# ---------------------------------------------------------------------------

def relatorio(sim):
    linhas = []
    add = linhas.append

    add("=" * 72)
    add("SIMULACAO DE REDE DE FILAS - RESULTADOS")
    add("=" * 72)

    for fila in sim.filas:
        cap = "inf" if fila.capacidade == inf else int(fila.capacidade)
        add("")
        add("Fila %s (G/G/%d/%s)" % (fila.nome, fila.servidores, cap))
        if fila.chegada:
            add("   chegadas do exterior: %g .. %g" % fila.chegada)
        add("   atendimento: %g .. %g" % fila.atendimento)
        destinos = ", ".join(
            "%s: %g%%" % ("SAIDA" if d is None else d.nome, p * 100) for d, p in fila.rotas
        )
        add("   roteamento: %s" % destinos)
        add("")
        add("   %-8s %18s %14s" % ("Estado", "Tempo acumulado", "Probabilidade"))
        add("   " + "-" * 42)
        total = sum(fila.tempos.values()) or 1.0
        for estado in sorted(fila.tempos):
            add("   %-8d %18.4f %13.2f%%"
                % (estado, fila.tempos[estado], 100.0 * fila.tempos[estado] / total))
        add("   " + "-" * 42)
        add("   Perda de clientes: %d" % fila.perdas)

    add("")
    add("=" * 72)
    add("Tempo global da simulacao: %.4f" % sim.tempo)
    add("Numeros pseudoaleatorios utilizados: %d" % sim.gerador.usados)
    add("=" * 72)
    return "\n".join(linhas)


def main():
    if len(sys.argv) != 2:
        print("Uso: python simulador.py <arquivo_do_modelo>")
        return 1
    filas, semente, aleatorios = ler_modelo(sys.argv[1])
    sim = Simulador(filas, semente, aleatorios)
    sim.executa()
    print(relatorio(sim))
    return 0


if __name__ == "__main__":
    sys.exit(main())