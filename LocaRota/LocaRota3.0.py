import json
import random
import numpy as np 
from geopy.distance import geodesic


with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

#Definição de variaveis globais
cidades = config["cidades"]
param = config["param"]

#Classe para salvar variaveis das cidades selecionadas
class ProblemData:
    def __init__(self):
        self.qtd_cidades = 0
        self.distancias = None
        self.cidades_sel = []
        self.cidades_coord = [] 

Data = ProblemData()

def diferenca(cidade1, cidade2):
    idx1 = Data.cidades_sel.index(cidade1)
    idx2 = Data.cidades_sel.index(cidade2)
    return Data.distancias[idx1][idx2]

def avaliar_rota(rota):
    total = 0
    for i in range(len(rota) - 1):
        total += diferenca(rota[i], rota[i + 1])
    return total

def gerar_populacao(tamanho, cidade_disponiveis, cidade_inicial):
    populacao = []
    for _ in range(tamanho):
        rota = cidade_disponiveis.copy()
        random.shuffle(rota)
        rota = [cidade_inicial] + rota
        populacao.append(rota)
    return populacao

def selecao(populacao, tamanho):
    populacao.sort(key=avaliar_rota)
    return populacao[:tamanho]

def crossover(pai1, pai2):
    gene_size = param["crossover_gene_size"]
    gene_size = min(gene_size, len(pai1) - 1)
    
    inicio = random.randint(1, len(pai1) - gene_size)
    fim = inicio + gene_size

    new_filho = [None] * len(pai1)
    new_filho[inicio:fim] = pai1[inicio:fim]

    p2_idx = 0
    for i in range(len(pai1)):
        if i < inicio or i >= fim:
            while pai2[p2_idx] in new_filho:
                p2_idx += 1
            new_filho[i] = pai2[p2_idx]
            p2_idx += 1
    return new_filho

def mutacao(rota):
    taxa = param["mutation_individual_rate"]
    gene_mutacao = param["mutation_gene_size"]

    rota_mutada = rota.copy()
    if random.random() < taxa:
        if len(rota_mutada) > 2: 
            for _ in range(gene_mutacao):
                i, j = random.sample(range(1, len(rota_mutada)), 2)
                rota_mutada[i], rota_mutada[j] = rota_mutada[j], rota_mutada[i]
    return rota_mutada

def debug_geracao(geracao, populacao):
    melhor_rota_geracao = min(populacao, key=avaliar_rota)
    melhor_valor_geracao = avaliar_rota(melhor_rota_geracao)
    print(f"--- Geracao {geracao + 1} ---")
    print(f"Melhor rota atual: {melhor_rota_geracao}")
    print(f"Valor da rota (distancia): {melhor_valor_geracao:.2f} km\n")

def algoritmo_genetico(cidade_inicial_param, cidades_destino_param):
    populacao = gerar_populacao(param["population_size"], cidades_destino_param, cidade_inicial_param)

    for geracao in range(param["generations"]):
        debug_geracao(geracao, populacao)

        selecionados = selecao(populacao, param["selection_size"])
        filhos = []
        while len(filhos) < param["population_size"]:
            pai1, pai2 = random.sample(selecionados, 2)
            
            filho = crossover(pai1, pai2)
            filho = mutacao(filho)
            filhos.append(filho)
        populacao = filhos

    melhor_rota = min(populacao, key=avaliar_rota)
    return melhor_rota

print("-CAPITAIS DISPONIVEIS-")
for cidade in cidades.keys():
    print(cidade)

cidade_inicial = input("\nDigite a cidade inicial (exatamente como escrito acima): ").strip()

if cidade_inicial not in cidades:
    print("\nX Cidade inicial invalida! Encerrando.")
    exit()

cidades_destino_input = input("\nDigite as cidades destino separadas por virgula:\n").split(',')

cidades_destino = []
for c in cidades_destino_input:
    c_strip = c.strip()
    if c_strip:
        if c_strip not in cidades:
            print(f"\nX Cidade invalida na lista de destino: {c_strip}. Encerrando.")
            exit()
        cidades_destino.append(c_strip)

if cidade_inicial in cidades_destino:
    cidades_destino.remove(cidade_inicial)

if not cidades_destino:
    print("\nNenhuma cidade de destino valida informada. Encerrando.")
    exit()

#preparação dos dados que o algoritmo genético vai utilizar
Data.cidades_sel = [cidade_inicial] + cidades_destino
Data.qtd_cidades = len(Data.cidades_sel)
Data.cidades_coord = [cidades[c] for c in Data.cidades_sel] #lista com as coordenadas

Data.distancias = np.zeros((Data.qtd_cidades, Data.qtd_cidades)) #Cria uma matriz das cidades (Cidade * Cidade)

#Calculo de distancias
for i in range(Data.qtd_cidades):
    for j in range(i + 1, Data.qtd_cidades):
        loc1 = tuple(Data.cidades_coord[i]) 
        loc2 = tuple(Data.cidades_coord[j])
        
        distancia = geodesic(loc1, loc2).km
        
        Data.distancias[i][j] = Data.distancias[j][i] = distancia #Garantia que não vai calcular a ida e a volta das mesmas cidades
        print(f"   Distancia entre {Data.cidades_sel[i]} e {Data.cidades_sel[j]}: {distancia:.2f} km")

print("\n\nCalculando melhor rota com Algoritmo Genetico...\n")
melhor_rota = algoritmo_genetico(cidade_inicial, cidades_destino) #lista com a melhor sequência de cidades

print("\n--- Processo Concluido ---")
print("Melhor rota final encontrada:")
for cidade in melhor_rota:
    print(f"-> {cidade}")

print(f"\nValor da melhor rota final (distancia): {avaliar_rota(melhor_rota):.2f} km")