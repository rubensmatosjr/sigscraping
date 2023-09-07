# Autor: Rubens de Souza Matos Junior
# Script para download de boletins de alunos dos cursos técnicos integrados ou subsequentes no SIGAA/IFS

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from urllib3.exceptions import InsecureRequestWarning
from urllib3 import disable_warnings
from getpass import getpass

import time
import re
import requests
import json

# Função para avançar para a página de consulta de boletins automaticamente
# Não funciona perfeitamente ainda.
def avancaParaConsultaBoletins():

	driver.find_element(By.CLASS_NAME, "login100-form-btn").click()
	el = WebDriverWait(driver, timeout=20).until(lambda d: driver.find_element(By.CLASS_NAME,"descricaoOperacao"))

	driver.get("https://sigaa.ifs.edu.br/sigaa/escolhaVinculo.do?dispatch=escolher&vinculo=1")
	driver.find_element(By.ID, "link").click()
	driver.get('https://sigaa.ifs.edu.br/sigaa/graduacao/busca_discente.jsf')


def salvaBoletim(linhaAluno):

	print("Ativo: "+linhaAluno.text)
    	nomeAluno = linhaAluno.find_elements(By.TAG_NAME,'td')[3]
    	tituloBoletim = nomeAluno.text
    	discButton = linhaAluno.find_element(By.TAG_NAME,'input')
    	discButton.click()
    	scriptTitulo = "document.title = '" + tituloBoletim + "';"
    	driver.execute_script(scriptTitulo)
    	driver.execute_script('window.print();')
    	

# Função para configurar a impressão em PDF no navegador.
# É preciso passar como parâmetro o diretório para salvar os boletins    	
def configuraChrome(pastaBoletins):

   disable_warnings(InsecureRequestWarning)
   appState = {
        "recentDestinations": [
          {
            "id": "Save as PDF",
            "origin": "local",
            "account": ""
          }
         ],
        "selectedDestinationId": "Save as PDF",
        "version": 2
   }

   profile = {'printing.print_preview_sticky_settings.appState': json.dumps(appState),
           'savefile.default_directory': pastaBoletins}

   chrome_options = webdriver.ChromeOptions()
   chrome_options.add_experimental_option('prefs', profile)
   chrome_options.add_argument('--kiosk-printing')


# Para iniciar, armazenamos o nome de usuário e senha da pessoa no SIGAA

username=input("Digite seu SIAPE")
password=getpass("Digite sua senha")

# Também solicitamos o caminho da pasta onde os boletins serão salvos

folder=input("Digite o caminho para a pasta onde os boletins serão salvos")

# Definimos algumas propriedades para o navegador Chrome, incluindo a pasta para salvar os PDFs dos boletins

configuraChrome(folder)

# Abre navegador na pagina de Login do SIGAA

driver = webdriver.Chrome(options=chrome_options)
driver.implicitly_wait(5)
driver.get('https://sigaa.ifs.edu.br/sigaa/verTelaLogin.do')

# O script insere nos campos o usuário e senha digitados no console anteriormente

user = driver.find_element(By.NAME, "user.login")
user.send_keys(username)
passwd = driver.find_element(By.NAME, "user.senha")
passwd.send_keys(password)

# Por enquanto, precisamos apertar o botão de entrar no sistema manualmente
# Em seguida, navegar até a página de consulta dos boletins
# Digitar os dados para consulta (nome do curso, p. ex.) e clicar em consultar.
# Esse processo deve ser feito em até 60 segundos
# Quando a função avancaParaConsultaBoletins() estiver funcionando, não será mais necessário esse processo.

el = WebDriverWait(driver, timeout=60).until(lambda d: driver.find_element(By.CLASS_NAME,"listagem"))

# Obtém boletins dos alunos ativos

status = "ATIVO"
listaAlunos = driver.find_element(By.CLASS_NAME,"listagem")
elements = listaAlunos.find_elements(By.TAG_NAME, 'tr')

for idx, e in enumerate(elements):
    linhaAlunoAtual = elements[idx]

    # Se a linha atual da listagem possui o status Ativo, salva o boletim desse aluno 
    if (status in linhaAlunoAtual.text):

    	salvaBoletim(linhaAlunoAtual)
    	
    	# Volta para a janela da listagem de alunos    	

    	time.sleep(2)
    	driver.back()
    	driver.refresh()
    	time.sleep(2)
    	
    	# Recupera novamente os elementos da listagem de alunos
    	# para evitar o erro de "Stale Element Reference Exception"

    	listaAlunos = driver.find_element(By.CLASS_NAME,"listagem")
	elements = listaAlunos.find_elements(By.TAG_NAME, 'tr')
    else:
    	print("Não ativo: "+linhaAlunoAtual.text)
