import pandas as pd

dfPlanilha=pd.read_csv("planilha-pe-de-meia-2024-07.csv")

dfAtivos=pd.read_csv("Ativos-Integrados-2024-07-05.csv")

nomesPlanilha=dfPlanilha['Nome'].tolist()
nomesAtivos=dfAtivos['Nome'].tolist()

total=0
print("Alunos ativos que não estão na planilha do Pé de Meia")
for nome in nomesAtivos:
    if (nome not in nomesPlanilha):
        print(nome)
        total+=1
print(f"Total:{total}")
total=0
print("Alunos na planilha do Pé de Meia que não estão entre os ativos")
for nome in nomesPlanilha:
    if (nome not in nomesAtivos):
        print(nome)
        total+=1

print(f"Total:{total}")
