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
import datetime

def configuraChrome():
 
   disable_warnings(InsecureRequestWarning)
   return webdriver.Chrome()



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

 
def baixaListaAtivos(nomeCurso):

    el = WebDriverWait(driver, timeout=15).until(lambda d:  driver.find_element(By.CLASS_NAME,"listagem"))

    status = "ATIVO"
    listaAlunos = driver.find_element(By.CLASS_NAME,"listagem")
    elements = listaAlunos.find_elements(By.TAG_NAME, 'tr')

    # lista dos alunos    
    lista = []   

    for idx, e in enumerate(elements):
        linhaAlunoAtual = elements[idx]
        
        # Se a linha atual da listagem possui o status Ativo, inclui o aluno na lista 
        if ( status in linhaAlunoAtual.text ):
            dadosEstudante=linhaAlunoAtual.text.split()
            matAluno = dadosEstudante[0]
            #Remove a matrícula e o status, deixando apenas as partes do nome do(a) estudante na array
            dadosEstudante.pop(0)
            dadosEstudante.pop(len(dadosEstudante)-1)
            nomeAluno = " ".join(dadosEstudante)

            lista.append([matAluno, nomeAluno, nomeCurso])
      
    alunos_df = pd.DataFrame(lista, columns =['Matricula', 'Nome', 'Curso'])
    alunos_df.to_csv(nomeCurso+".csv")
    print(alunos_df)



# Para iniciar, armazenamos o nome de usuário e senha da pessoa no SIGAA

user=input("Digite seu SIAPE: ")
passw=getpass("Digite sua senha: ")

driver = configuraChrome()

loginSIGAA(driver, user, passw)

avancaParaConsultaBoletins()


el = WebDriverWait(driver, timeout=60).until(lambda d: driver.find_element(By.ID,"formulario:nomeDiscente"))


listaCursos = ["Redes de Computadores", "Automação Industrial", "Integrado em Eletromecânica" , "Integrado em Edificações"] 
#listaCursos = ["Integrado em Edificações"] 

dfCursos = []
for curso in listaCursos:
    print(curso)
    insereDadosCurso(curso, "CAMPUS LAGARTO")
    baixaListaAtivos(curso)
    dfAtual=pd.read_csv(curso+".csv")
    dfCursos.append(dfAtual)

# Gera dataframe concatenado de todos os cursos, com índice unificado
dfConcat = pd.concat([dfCursos[0],dfCursos[1],dfCursos[2],dfCursos[3]])

dfConcat = dfConcat.drop("Unnamed: 0",axis=1)
dfConcat = dfConcat.reset_index(drop=True)
print(dfConcat)

# Obtem a data atual
hoje = datetime.date.today()

# Converte a data para uma string formata Ano-Mes-Dia
hoje_str = hoje.strftime("%Y-%m-%d")

dfConcat.to_csv("Ativos-Integrados-"+hoje_str+".csv")
