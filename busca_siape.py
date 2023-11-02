#Autor: Rubens de Souza Matos Junior
#Script para obter SIAPE de docentes disponíveis na página pública do SIGAA/IFS

from bs4 import BeautifulSoup
from urllib3.exceptions import InsecureRequestWarning
from urllib3 import disable_warnings
from requests_html import HTMLSession
from urllib.parse import urljoin

import time
import re
import os
import requests
import sys

def get_siape_in_links(links, dnames):

    # Obtem os SIAPEs a partir de cada link, junto com os nomes informados na lista dnames
    for index,dlink in enumerate(links):
        linkAndSIAPE = dlink.split("=")
        siape=linkAndSIAPE[1]
        nome=dnames[index]
        print(f"SIAPE do(a) docente {nome}: {siape}")


url = "https://sigaa.ifs.edu.br/sigaa/public/docente/busca_docentes.jsf"

# Obtem nome do docente que foi passado como argumento para o script
docente=sys.argv[1]

# Faz requisição para a página de busca dos docentes no SIGAA, criando sessão que será usada na consulta posterior
disable_warnings(InsecureRequestWarning)
session = HTMLSession()
session.verify = False
res = session.get(url,verify=False)
soup = BeautifulSoup(res.html.html, "html.parser")

# Monta os dados para serem enviados no formulário com o método POST 
data = {}
data['form'] = 'form'
data['form:nome'] = docente
data['form:buscar'] = 'Buscar'
data['javax.faces.ViewState'] = 'j_id1'
data['form:departamento'] = '0'

# Envia a requisição de consulta com os dados e processa a resposta com o BeautifulSoup
res = session.request("POST",url, data=data, verify=False)
soup = BeautifulSoup(res.content, "html.parser")

# Extrai links para a página pública de cada docente. No link consta o SIAPE
docentes_links = [link['href'] for link in soup.find_all(href=re.compile("siape"))]

# Extrai os nomes dos docentes retornados
docentes_nomes = [dNome.string for dNome in soup.find_all('span',class_="nome")]

numDocentes = len(docentes_links)
print(f"Quantidade de docentes identificados: {numDocentes}")

# Obtem os SIAPEs de cada docente
get_siape_in_links(docentes_links, docentes_nomes)
