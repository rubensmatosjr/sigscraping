#!/usr/bin/env python
# Autores: Rubens de Souza Matos Junior
# Script para download e armazenamento em dataframe de notas e faltas dos boletins de alunos dos cursos técnicos integrados ou subsequentes no SIGAA/IFS

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from urllib3.exceptions import InsecureRequestWarning
from urllib3 import disable_warnings
from getpass import getpass
import pandas as pd
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC


import time
import re
import requests
import json

def configuraChrome():
 
   disable_warnings(InsecureRequestWarning)
   return webdriver.Chrome()


def raspaBoletins(nome, matricula, curso):

    # achando a tabela
    tables = driver.find_elements(By.CLASS_NAME, "tabelaRelatorio")
    tabela_2023 = tables[0].get_attribute('outerHTML')

    # HTML table to DataFrame
    soup = BeautifulSoup(tabela_2023, "html.parser")
    table_2023 = soup.find(name='table')
    df = pd.read_html(str(table_2023))[0]
    df.loc[:, 'Nome'] = nome
    df.loc[:, 'Matrícula'] = matricula
    df.loc[:, 'Curso'] = curso
    
    return df


# Função para avançar para a página de consulta de boletins automaticamente
# Não funciona perfeitamente ainda.
def avancaParaConsultaBoletins():

    # esperar o site carregar
    wait = WebDriverWait(driver, 2)
    
    # Clicks no site até chegar na tabela
        
    driver.get("https://sigaa.ifs.edu.br/sigaa/escolhaVinculo.do?dispatch=escolher&vinculo=1")
   
    pular_avisos = driver.find_elements(By.XPATH, '//input[@value="Pular Avisos"]')
    if len(pular_avisos)>0:
        pular_avisos[0].click()
        
    # esperar o site carregar
    wait = WebDriverWait(driver, 2)
    
    driver.get("https://sigaa.ifs.edu.br/sigaa/verMenuTecnico.do")
    
    wait = WebDriverWait(driver, 2)

    #Clica na aba Aluno
    tab_aluno = driver.find_element(By.ID, 'elgen-12').click()
    
    #Clica na opção "Emitir Boletim Individual"
    driver.find_element(By.XPATH, '//a[@id="menuTecnicoForm:emitirBoletimIndividual"]').click()    


def salvaBoletim(linhaAluno, cursoAtual):   
   
   dadosEstudante=linhaAluno.text.split()   
   matriculaAluno = dadosEstudante[0]
   #Remove a matrícula e o status, deixando apenas as partes do nome do(a) estudante na array
   dadosEstudante.pop(0)
   dadosEstudante.pop(len(dadosEstudante)-1)
   nomeAluno = " ".join(dadosEstudante)
   
   print(f"Matrícula: {matriculaAluno}, Nome: {nomeAluno}")
   linhaAluno.find_element(By.TAG_NAME,'input').click()
   wait = WebDriverWait(driver, 2)
   df_aluno=raspaBoletins(nomeAluno, matriculaAluno, cursoAtual) 
   return df_aluno
   
def insereDadosCurso(nomeCurso, nomeCampus):

   # O script insere nos campos o nome do curso e a matrícula e clica no botão "Buscar"

   
   campoCurso = driver.find_element(By.NAME, "formulario:curso")
   campoCurso.clear()
   campoCurso.send_keys(nomeCurso)
   
   campoCampus = driver.find_element(By.NAME, "formulario:j_id_jsp_1742295858_320")
   #campoCampus.clear()
   campoCampus.send_keys(nomeCampus)
   driver.find_element(By.XPATH, '//input[@value="Buscar"]').click()

def loginSIGAA(driver, username, password):

   # Abre navegador na pagina de Login do SIGAA

   driver.implicitly_wait(5)
   driver.get('https://sigaa.ifs.edu.br/sigaa/verTelaLogin.do')

   # O script insere nos campos o usuário e senha digitados no console anteriormente

   user = driver.find_element(By.NAME, "user.login")
   user.send_keys(username)
   passwd = driver.find_element(By.NAME, "user.senha")
   passwd.send_keys(password)

   driver.find_element(By.XPATH, '//input[@value="Entrar"]').click()

 
def baixaBoletinsCurso(nomeCurso):
    # Obtém boletins dos alunos ativos

    el = WebDriverWait(driver, timeout=15).until(lambda d:  driver.find_element(By.CLASS_NAME,"listagem"))

    status = "ATIVO"
    listaAlunos = driver.find_element(By.CLASS_NAME,"listagem")
    elements = listaAlunos.find_elements(By.TAG_NAME, 'tr')

    # lista com os boletins    
    lista = []   

    for idx, e in enumerate(elements):
        linhaAlunoAtual = elements[idx]
        

        # Se a linha atual da listagem possui o status Ativo, salva o boletim desse aluno 
        if ( status in linhaAlunoAtual.text ):

           df_aluno=salvaBoletim(linhaAlunoAtual,nomeCurso)
           print(df_aluno)
           lista.append(df_aluno)
      
           # Volta para a janela da listagem de alunos
           driver.back()
           driver.refresh()
           time.sleep(2)
      
           # Recupera novamente os elementos da listagem de alunos
           # para evitar o erro de "Stale Element Reference Exception"

           listaAlunos = driver.find_element(By.CLASS_NAME,"listagem")
           elements = listaAlunos.find_elements(By.TAG_NAME, 'tr')   

           notas_df = pd.concat(lista, ignore_index=True)
           notas_df.to_csv(nomeCurso+".csv")
           print(notas_df)
           
           

def baixaBoletinsMatriculados(nomeCurso, listaMatriculas):
    # Obtém boletins dos alunos ativos

    el = WebDriverWait(driver, timeout=15).until(lambda d:  driver.find_element(By.CLASS_NAME,"listagem"))

    listaAlunos = driver.find_element(By.CLASS_NAME,"listagem")
    elements = listaAlunos.find_elements(By.TAG_NAME, 'tr')

    # lista com os boletins    
    lista = []   

    for idx, e in enumerate(elements):
        if idx<2: continue
        
        linhaAlunoAtual = elements[idx]
        
        if 'ATIVO' not in linhaAlunoAtual.text and 'CONCLUÍDO' not in linhaAlunoAtual.text and 'CANCELADO' not in linhaAlunoAtual.text:
           continue
           
        dadosEstudante = linhaAlunoAtual.text.split()
        matriculaAluno = dadosEstudante[0]        

        # Se a linha atual da listagem possui o status Ativo, salva o boletim desse aluno 
        if ( int(matriculaAluno) in listaMatriculas ):
           print(matriculaAluno)
           df_aluno=salvaBoletim(linhaAlunoAtual,nomeCurso)
           print(df_aluno)
           lista.append(df_aluno)
      
           # Volta para a janela da listagem de alunos
           driver.back()
           driver.refresh()
           time.sleep(2)
      
           # Recupera novamente os elementos da listagem de alunos
           # para evitar o erro de "Stale Element Reference Exception"

           listaAlunos = driver.find_element(By.CLASS_NAME,"listagem")
           elements = listaAlunos.find_elements(By.TAG_NAME, 'tr')   

           notas_df = pd.concat(lista, ignore_index=True)
           notas_df.to_csv(nomeCurso+".csv")
           print(notas_df)


# Para iniciar, armazenamos o nome de usuário e senha da pessoa no SIGAA

user=input("Digite seu SIAPE: ")
passw=getpass("Digite sua senha: ")

driver = configuraChrome()

loginSIGAA(driver, user, passw)

avancaParaConsultaBoletins()


el = WebDriverWait(driver, timeout=60).until(lambda d: driver.find_element(By.ID,"formulario:nomeDiscente"))


listaCursos = ["Redes de Computadores", "Automação Industrial", "Integrado em Eletromecânica" , "Integrado em Edificações"] 
#listaCursos = ["Integrado em Edificações"] 

dfMatriculas=pd.read_csv("Integrados-2024-03-27.csv")

matriculas=dfMatriculas['Matrícula'].unique().tolist()

print(matriculas)

dfCursos = []
for curso in listaCursos:
    print(curso)
    insereDadosCurso(curso, "CAMPUS LAGARTO")
    baixaBoletinsMatriculados(curso,matriculas)
    dfAtual=pd.read_csv(curso+".csv")
    dfCursos.append(dfAtual)

# Gera dataframe concatenado de todos os cursos, com índice unificado
dfConcat = pd.concat([dfCursos[0],dfCursos[1].iloc[1:],dfCursos[2].iloc[1:],dfCursos[3].iloc[1:]])

dfConcat = dfConcat.drop("Unnamed: 0",axis=1)
dfConcat = dfConcat.reset_index(drop=True)
print(dfConcat)
dfConcat.to_csv("Integrados-2024.csv")
