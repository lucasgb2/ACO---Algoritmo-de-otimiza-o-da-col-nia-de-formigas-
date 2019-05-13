'''Algoritmo Colony Ant (ACO), feito por Lucas Garcia Batista
Como requisido de projeto final, para matéria de 
Tópicos em inteligência computacional '''

from matplotlib.pyplot import plot, title, show, annotate
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt2
from random import random, randrange, choice, choices
import math
import pprint
import timeit, time, datetime
import statistics

pp = pprint.PrettyPrinter()

class Vertice():
    def __init__(self, idd, x, y):
        self.id = int(idd)
        self.x = x
        self.y = y
        
    def __repr__(self):
        return 'Vertice %s' % str(self.id)
    
    
class Aresta():
    def __init__(self, pontoA, pontoB, feromonio = 0, custo = 0):
        self.pontoA = pontoA
        self.pontoB = pontoB
        self.feromonio = feromonio
        self.distancia = custo
        self.euclidiana = True
        
        self.calculaDistancia()
        
    def calculaDistancia(self):
        if self.euclidiana == True:
            origem =  [self.pontoA.x, self.pontoA.y]
            destino = [self.pontoB.x, self.pontoB.y]        
            self.distancia = self.distanciaEuclidiana(origem, destino)    
            
        return self.distancia
    
    def distanciaEuclidiana(self, origem, destino):
        return math.sqrt( ((origem[0] - destino[0])**2) + ((origem[1] - destino[1])**2) )
    
    def __repr__(self):
        return '[%s]<--------->[%s] = %s | Feromônio %s' % (self.pontoA, self.pontoB, str(self.distancia), str(self.feromonio))
    
class Formiga():    
    def __init__(self, verticeAtual):
        self.verticeAtual = verticeAtual        
        self.melhorCaminhoEncontrado = []
        self.custo = 0.0
        self.vizinhos = []
        self.interacao = 0
    
    def setMelhorCaminho(self, caminho, custo):
        if self.custo == 0:
            self.custo = custo
            self.melhorCaminhoEncontrado = caminho
            self.interacao += 1
        elif self.custo > custo:
            self.custo = custo
            self.melhorCaminhoEncontrado = caminho
            self.interacao += 1
                    
                
class GrafoCompleto():        
    
    def __init__(self, file=''):
        self.listaAresta = []
        self.listaVertice = []
        self.dicionarioListaAresta = {}
        self.file = file        
        self.vizinhos = {}
        self.matrix = []
        self.nomeArquivo = ''
        
        self.carregaArquivoXY()        
        self.montarGrafo()           
        
    def carregaArquivoXY(self):
        '''Extrai as cidade do arquivo de entrada. Os arquivos deve ter a estrutura .tsp '''
        vetorValues = []        
        file = self.file
        self.nomeArquivo = file        
        for line in open(file, 'r'):
            if line[0].isdigit():                
                vetorValues = [float(value) for value in line.split()[0:]]
                self.listaVertice.append(Vertice(vetorValues[0], vetorValues[1], vetorValues[2]))
               
             
    def montarGrafo(self):
        qtdeVertice = len(self.listaVertice)        
        for i in range(qtdeVertice):
            for j in range(qtdeVertice):
                aresta = Aresta(self.listaVertice[i], self.listaVertice[j])
                if aresta.distancia > 0:                                  
                    self.listaAresta.append(aresta)                       
                    self.montarDicionarioVizinho(aresta)
                    self.dicionarioListaAresta[(self.listaVertice[i].id, self.listaVertice[j].id)] = (aresta.distancia, 0)
       
                
    def montarDicionarioVizinho(self, aresta):        
        if aresta.pontoA.id not in self.vizinhos:
            self.vizinhos[aresta.pontoA.id] = [aresta.pontoB]
        elif aresta.pontoA.id != aresta.pontoB.id:
            self.vizinhos[aresta.pontoA.id].append(aresta.pontoB)

            
    def getFeromonioAresta(self, origem, destino):        
        valor = self.dicionarioListaAresta.get((origem.id, destino.id))
        return valor[1]
            
    def setFeromonioAresta(self, origem, destino, novoFeromonio):
        value = self.dicionarioListaAresta[(origem.id, destino.id)]        
        self.dicionarioListaAresta[(origem.id, destino.id)] = (value[0], novoFeromonio)
    
    def getDistanciaAresta(self, origem, destino):
        valor = self.dicionarioListaAresta.get((origem.id, destino.id))
        return valor[0]
    
    def getDistanciaAndFeromonioAresta(self, origem, destino):
        return self.dicionarioListaAresta.get((origem.id, destino.id))
            
    def getDistanciaArestasTotal(self, arestas):
        total = 0.0        
        for i in range(len(arestas)-1):
            total += self.getDistanciaAresta(arestas[i], arestas[i+1])
        total += self.getDistanciaAresta(arestas[-1], arestas[0])
        return total
    
    def plotar(self, path):        
        points = self.listaVertice
        x = []
        y = []
        for point in points:
            x.append(point.x)
            y.append(point.y)
            
        plt.plot(x, y, 'co')        
    
        for p in range(len(path)-1):
            i = path[p]
            j = path[p-1]            
            plt.arrow(i.x, i.y, j.x - i.x, j.y - i.y, color='r', length_includes_head=True)    
        
        plt.title(self.nomeArquivo)
        plt.show()
            
        
class ACO():
    
    def __init__(self, alfa, beta, feromonioInicial, taxaEvaporacao, numFormigas, interacao, file):
        self.alfa = alfa #parametro de influencia do feromonio
        self.beta = beta #parametro de influcencia da distância
        self.taxaEvaporacao = taxaEvaporacao
        self.numFormigas = numFormigas
        self.interacao = interacao      
        self.feromonioInicial = feromonioInicial        
        self.formigas = []        
        self.historico = []
        self.historicoMedia = []
        self.somaMedia = 0.0
        
        '''Gerar o gravo com base no arquivo .tsp'''
        self.grafo = GrafoCompleto(file)        
        
    
        
    def criarDistribuirFormigas(self):
        self.formigas = []
        vertices = [vertice for vertice in self.grafo.listaVertice]
        for i in range(self.numFormigas):
            selecionaVertice = choice(vertices)
            vertices.remove(selecionaVertice)
            f = Formiga(selecionaVertice)            
            self.formigas.append(f)
            
    def redistribuirFormigas(self):
        vertices = [vertice for vertice in self.grafo.listaVertice]
        for i in range(self.numFormigas):
            selecionaVertice = choice(vertices)
            vertices.remove(selecionaVertice)
            self.formigas[i].verticeAtual = selecionaVertice           
           
    def setHistoricoMedia(self, solucao):
        if self.somaMedia == 0:
            self.somaMedia = solucao
            self.historicoMedia.append(solucao)
        else:
            self.somaMedia = self.somaMedia + solucao        
            self.historicoMedia.append(self.somaMedia / (len(self.historicoMedia)+1))           
            
            
            
    def inicializaFeromonio(self):
        for aresta in self.grafo.listaAresta:            
            self.grafo.setFeromonioAresta(aresta.pontoA, aresta.pontoB, self.feromonioInicial)
            
    def run(self): 
        self.criarDistribuirFormigas()
        self.inicializaFeromonio()        
        
        for l in range(self.interacao):                        
            self.redistribuirFormigas()
            cidadesNaoVisitadas = []
            '''Pegando as cidades que a formiga deverá caminhar '''
            cidadesFormigaPassou = []
            for x in self.formigas:
                cidade = [x.verticeAtual]
                cidadesFormigaPassou.append(cidade)            
            
            '''Construindo uma solução para cada formiga '''
            for k in range(len(self.formigas)):
                for i in range(1, len(self.grafo.listaVertice)):
                    cidadesNaoVisitadas = list(set(self.grafo.vizinhos[self.formigas[k].verticeAtual.id]) - set(cidadesFormigaPassou[k]))
                                        
                    ''' Pegando valores das aresta para calculo '''
                    valFerDis = []
                    for c in cidadesNaoVisitadas:
                        valFerDis.append(list(self.grafo.getDistanciaAndFeromonioAresta(self.formigas[k].verticeAtual, c)) + [c])
                    
                    ''' Denominador da fórmula de seleção '''
                    feromonio = 0.0
                    distancia = 0.0
                    somatorioProbabilidade = 0.0
                    valores = []                    
                    for valores in valFerDis:
                        feromonio = valores[1] 
                        distancia = valores[0]                        
                        somatorioProbabilidade += (feromonio**self.alfa) * (( 1 /  distancia)**self.beta)                        
                    
                    if somatorioProbabilidade <= 0:  
                        somatorioProbabilidade = 1
                        
                    ''' Numerador da fórmula de seleção e geração das probabilidade '''
                    feromonio = 0.0
                    distancia = 0.0
                    probabilidade = 0.0
                    listaProbabilidade = {}
                    valores = []                    
                    for valores in valFerDis:                        
                        feromonio = valores[1] 
                        distancia = valores[0]  
                         
                        probabilidade = ((feromonio**self.alfa) * ((1 / distancia)**self.beta)) / somatorioProbabilidade						
                        listaProbabilidade[valores[2]] = probabilidade                    
                    
                    ''' Proxima cidade que a formiga irá caminhar (Método da roleta)'''                    
                    rand = random()
                    for p, v in listaProbabilidade.items():
                        rand -= v
                        if rand <= 0:
                            proximaCidadeEscolhida = p
                            break                                          
                    
                    ''' Adicionando a cidade escolhida a lista de cidades que a formiga já passou '''
                    cidadesFormigaPassou[k].append(proximaCidadeEscolhida)
                    
                    ''' Posiciona a formiga na proxima cidade '''
                    self.formigas[k].verticeAtual = proximaCidadeEscolhida
                 
                distanciaTotal = self.grafo.getDistanciaArestasTotal(cidadesFormigaPassou[k])
                self.formigas[k].setMelhorCaminho(cidadesFormigaPassou[k], distanciaTotal)
                self.historico.append(distanciaTotal)
                self.setHistoricoMedia(distanciaTotal)
                
            
            '''Atualizando taxa de feromonio das arestas '''
            for aresta in self.grafo.listaAresta:
                somaFeromonio = 0.0                     
                
                for f in range(len(self.formigas)):
                    '''Pegando os vertices que a formiga foi e gerando as arestas'''
                    arestaFormigas = []
                    for v in range(len(cidadesFormigaPassou[f]) - 1):
                        arestaFormigas.append((cidadesFormigaPassou[f][v], cidadesFormigaPassou[f][v+1]))                    
                    arestaFormigas.append((cidadesFormigaPassou[f][-1], cidadesFormigaPassou[f][0])) 
                    
                    '''Verificando se a formiga (f) passou pela a aresta que está sendo verificada'''                    
                    for a in arestaFormigas:
                        if (a[0].id == aresta.pontoA.id and a[1].id == aresta.pontoB.id):                            
                            somaFeromonio += (1 / self.formigas[f].custo)
                                                    
                novoFeromonio = (1 - self.taxaEvaporacao) * self.grafo.getFeromonioAresta(aresta.pontoA, aresta.pontoB) + somaFeromonio                
                self.grafo.setFeromonioAresta(aresta.pontoA, aresta.pontoB, novoFeromonio)
            

        solucao = None
        custo = None
        qualInteracao = 0
        for k in range(len(self.formigas)):            
            if not solucao:
                solucao = self.formigas[k].melhorCaminhoEncontrado
                custo = self.formigas[k].custo
                qualInteracao = self.formigas[k].interacao
            elif custo > self.formigas[k].custo:                
                solucao = self.formigas[k].melhorCaminhoEncontrado
                custo = self.formigas[k].custo                    
                qualInteracao = self.formigas[k].interacao    
                
        print('Interação %s com custo: %d\n' % (qualInteracao, custo))                         
                
        self.grafo.plotar(solucao)        
        self.historico.sort()
        self.historicoMedia.sort()        
        plt2.plot(self.historico, label='Melhor')
        plt2.plot(self.historicoMedia, 'g', label='Média')
        plt2.legend()
        plt2.title('Convergência para '+self.grafo.nomeArquivo)
        plt2.show()
        
        return [qualInteracao, custo]
                
                    
    
if __name__ == "__main__":        
    
    '''Definindo os paramentros iniciais'''
    alfa = 1.0
    beta = 5.0
    taxaEvaporacao = 0.5
    feromonioInicial = 0.8                
    interacao = 1    
    
    '''Definindo os arquivos TSPLIB para teste, os arquivos estão em uma pasta data '''
    files = ['eil51.tsp','pr76.tsp','kroA100.tsp']
    otimos = [426,108159,21282]
    numFormigas = [51,76,100]          
    
    '''Quantas vezes que um arquivo será executado '''
    execucoesPorFile = 1     
    
    '''For para executar os arquivos '''
    resultados = {}            
    for i, f in enumerate(files):
        melhor = None
        pior = None
        avg = 0.0
        avgTempo = 0
        desvioP = []
        
        ''' Quantidade de execução por arquivo '''
        for n in range(execucoesPorFile):        
            print('RUN %s do arquivo %s' % (n+1, f))            
            aco = ACO(alfa, beta, feromonioInicial, taxaEvaporacao, numFormigas[i], interacao, 'data/'+f)    
            
            '''Executando o ACO. Aqui o algoritmo retorna um vetor de tamanho 2, na primeira
             é o valor de qual interação foi melhor, e na segunda posição o custo '''
            r = aco.run() 
            custo = r[1]            
            
            '''Estatistíca'''
            if melhor == None or melhor > custo:
                melhor = custo            
                
            if pior == None or pior < custo:
                pior = custo               
                
            desvioP.append(r[1])                
            avg += custo            

        '''Estatistíca do arquivo executado'''            
        avg = (avg/execucoesPorFile)
        avgTempo = (avgTempo/execucoesPorFile)
        taxaConvergencia = (1 - ((melhor - otimos[i]) / otimos[i])) * 100
        if len(desvioP) > 1:
            statistics.stdev(desvioP)
        else:
            desvioP = 0
        
        if f not in resultados:            
            resultados[f] = {"otimo":otimos[i], 
                      "melhor":melhor, 
                      "pior":pior, 
                      "media":avg,
                      "desvioPadrão":desvioP,
                      "taxaConvergencia":taxaConvergencia, 
                      "tempoMedio": (str(round(avgTempo,2))+' sec' if avgTempo <= 60 else str(round(avgTempo / 60,2))+' min') }
    
    pp.pprint(resultados)