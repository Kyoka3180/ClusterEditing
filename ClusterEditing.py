import math
import itertools
import datetime
from graphviz import Graph
import os
import time
#test用
import random

def pattern_TupletoInt(t):
    res=0
    for i in t:
        res+=2**i
    return res

def pattern_InttoTuple(i):
    res=[]
    j=0
    while i>0:
        if i%2==1:
            res.append(j)
        i=i>>1
        j+=1
    return tuple(res)

def renderGraph(V,E,title):
    dot = Graph(format='png')
    for i in range(len(V)):
        dot.node(str(i))
    for i in range(len(V)):
        for j in range(i+1,len(V)):
            if E[i][j]==1:
                dot.edge(str(i),str(j))
    dot.render(title)

class CE:
    def __init__(self,N,M,V,E,OutputPath=""):
        self.N=N
        self.M=M
        self.V=[V[i] for i in range(N)]
        self.E=[[E[__][_] for _ in range(N)] for __ in range(N)]
        self.SubsetMinimumCost=[math.inf]*(2**N)
        self.SubsetMinimumCostPattern=[set() for _ in range(2**N)]
        self.SubsetMinimumCost[0]=0
        self.nowTime = datetime.datetime.now()
        self.OutputPath=OutputPath
        if OutputPath=="":#指定がない場合、作成した時刻のファイルを作成
            self.OutputPath="output-"+self.nowTime.strftime('%Y%m%d%H%M%S')
        os.makedirs(self.OutputPath, exist_ok=True)
    
    def calCE(self):
        #初期条件のグラフの描画
        renderGraph(self.V,self.E,self.OutputPath+"/GraphBeforeCE")
        #書き込み用ファイルの作成
        self.file=open(self.OutputPath+"/Output.txt",mode="w")
        self.file.write("N : "+str(self.N)+"\nM : "+str(self.M)+"\n")
        startTime=time.time() #処理時間の計測
        #部分集合のサイズが小さい順に最小コストを計算
        for length in range(1,self.N+1):
            print("length time: "+str(time.time()-startTime))
            for s in range(2**self.N):
                if s.bit_count()!=length:
                    continue
                self.calMinimumCost(s)
        self.file.write("minimum cost : "+str(self.SubsetMinimumCost[2**self.N-1])+"\nminimum set\n")
        for i,Si in enumerate(self.SubsetMinimumCostPattern[2**self.N-1]):
            self.file.write(str(Si)+"\n")
            #今のクラスタに編集したときのグラフを作成
            tmpE=[[0]*self.N for _ in range(self.N)]
            for sj in Si:
                for vi,vj in itertools.combinations(sj,2):
                    tmpE[vi][vj]=1
                    tmpE[vj][vi]=1
            renderGraph(self.V,tmpE,self.OutputPath+"/"+str(i+1)+"th_graph_after_CE")
            CEcost=0
            for v1 in range(self.N):
                for v2 in range(v1+1,self.N):
                    if tmpE[v1][v2]!=self.E[v1][v2]:
                        CEcost+=1
            self.file.write("CEcose : "+str(CEcost)+"\n")
        self.file.write("time : "+str(time.time()-startTime)+"\n")
        self.file.close()

    def calMinimumCost(self,s):#sはVの部分集合
        sTuple=pattern_InttoTuple(s)
        #始めはsが一つの集合として現在のミニマムコストを設定
        self.SubsetMinimumCost[s]=self.calCECost(s)
        self.SubsetMinimumCostPattern[s].add((sTuple,))
        for r1 in range(1,len(sTuple)//2):
            for s1Tuple in itertools.combinations(pattern_InttoTuple(s),r1):
                s1=pattern_TupletoInt(s1Tuple)
                s2=s-s1
                tmpResult=self.calMergeCost(s1,s2)
                if tmpResult>self.SubsetMinimumCost[s]:
                    continue
                if tmpResult<self.SubsetMinimumCost[s]:
                    self.SubsetMinimumCost[s]=tmpResult
                    self.SubsetMinimumCostPattern[s].clear()
                for si in self.mergePatterns(s1,s2):
                    self.SubsetMinimumCostPattern[s].add(si)
        self.file.write("s : "+str(sTuple)+" cost : "+str(self.SubsetMinimumCost[s])+"\n")

    def calCECost(self,s):#部分集合sが一つのクラスタの時の編集コストを計算する
        sSet=set(pattern_InttoTuple(s))
        costAdd=0
        costDelete=0
        for v1 in range(self.N):
            for v2 in range(v1+1,self.N):
                if v1 in sSet and v2 in sSet:
                    if self.E[v1][v2]==0:
                        costAdd+=1
                    continue
                if v1 not in sSet and v2 not in sSet:
                    continue
                if self.E[v1][v2]==1:
                    costDelete+=1
        costTotal=costAdd+costDelete
        return costTotal

    def calMergeCost(self,s1,s2):#部分集合s1,s2を組み合わせてクラスタの集合としたときのsの編集コスト
        s1Tuple,s2Tuple=pattern_InttoTuple(s1),pattern_InttoTuple(s2)
        #重複した削除のコストを計算する
        duplicateDeleteCost=0
        for v1 in s1Tuple:
            for v2 in s2Tuple:
                if self.E[v1][v2]==1:
                    duplicateDeleteCost+=1
        return self.SubsetMinimumCost[s1]+self.SubsetMinimumCost[s2]-duplicateDeleteCost
                
    def mergePatterns(self,s1,s2):#部分集合s1,s2を組み合わせてできるクラスタ
        res = []
        for s1Pattern in self.SubsetMinimumCostPattern[s1]:
            for s2Pattern in self.SubsetMinimumCostPattern[s2]:
                tmpS=tuple(sorted(s1Pattern+s2Pattern))
                res.append(tmpS)
        return res
    

if __name__ == "__main__":
    N=15
    V=[1]*N
    M=40
    E=[[0]*N for _ in range(N)]
    e=0
    while e<M:
        v1=random.randint(0,N-1)
        v2=random.randint(0,N-1)
        if v1==v2 or E[v1][v2]==1:
            continue
        E[v1][v2]=1
        E[v2][v1]=1
        e+=1
    ce=CE(N,M,V,E)
    ce.calCE()
    