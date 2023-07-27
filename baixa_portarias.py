#Autor: Rubens de Souza Matos Junior
#Script para download de portarias disponíveis no SIPAC/IFS

from selenium import webdriver
from selenium.webdriver.common.by import By
#from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from bs4 import BeautifulSoup
from urllib3.exceptions import InsecureRequestWarning
from urllib3 import disable_warnings

import time
import re
import os
import requests

disable_warnings(InsecureRequestWarning)



def clean_filename(name):
    # Elimina caracteres invalidos para nomes de arquivos e mantem dentro de um limite de 40 caracteres para facilitar legibilidade
    # Baseado em https://github.com/MalloyDelacroix/DownloaderForReddit
    invalid_chars = '"*\\/\'.|?:<>'
    filename = ''.join([x if x not in invalid_chars else '#' for x in name])
    if len(filename) >= 41:
        filename = filename[:40] + '...'
    return filename 


def download_file(url, local_filename):

    with requests.get(url, stream=True, verify=False) as response:
        response.raise_for_status()
        with open(local_filename, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)


def get_pdf_in_links(url, links, fnames):
    # Cria um diretório para armazenar os PDFs
    os.makedirs('PDFs', exist_ok=True)    

    # Efetua o download dos PDFs de cada link, com numeracao sequencial e nomes informados na lista fnames (ex: PDF_001_Arquivo_etc.pdf)
    for index, pdf_link in enumerate(links, start=1):
        fname = clean_filename(fnames[index-1].strip())
        fnumber = str(index).zfill(3)
        pdf_url = f"{url}/{pdf_link}"
        pdf_name = f"PDFs/PDF_{fnumber}_{fname}.pdf"
        print(f"Baixando o PDF {index}...")
        print(fname)
        download_file(pdf_url, pdf_name)
        time.sleep(2)


# Abre navegador na pagina de Busca Avançada do SIPAC para o usuario digitar os dados:
# SIAPE, nome do servidor, ou qualquer outro criterio de busca e clicar em buscar
driver = webdriver.Firefox()
driver.get('https://sipac.ifs.edu.br/public/jsp/boletim_servico/busca_avancada.jsf')

# Aguarda no maximo 20 segundos para aparecer a pagina com a tabela dos informativos (portarias).
# Tempo deve ser suficiente para o usuario digitar os dados no formulario e pressionar o botao
el = WebDriverWait(driver, timeout=20).until(lambda d: driver.find_element(By.ID,"tableInformativos"))

# Faz o parse da pagina HTML atual para o objeto estruturado do BeautifulSoup
soup = BeautifulSoup(driver.page_source, 'html.parser')
driver.close()

# Extrai links para os PDFs de cada portaria
pdf_links = [link['href'] for link in soup.find_all(href=re.compile("verArquivo"))]

# Extrai assuntos de cada portaria. Estao em celulas da tabela, logo apos a palavra Assunto em negrito
table = soup.find('table', id="tableInformativos")
pdf_subjects = []
for row in table.find_all("b"):
    pdf_subjects.append(row.next_sibling)

numPDFs = len(pdf_links)
print(f"Quantidade de links de portarias identificados: {numPDFs}")

# Realiza o download dos arquivos PDF
get_pdf_in_links("https://sipac.ifs.edu.br", pdf_links, pdf_subjects)
   
