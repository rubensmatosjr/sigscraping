# sigscraping

Extração automatizada de dados de páginas dos sistemas SIG utilizados pelo Instituto Federal de Sergipe (IFS).

Por enquanto, o repositório possui apenas 3 scripts Python:

- **baixa\_portarias.py** Download de todas portarias emitidas pelo IFS para um determinado servidor interessado, disponibilizadas no SIPAC. Dependências principais: **Selenium** e **BeautifulSoup**.

- **baixa\_boletins\_tecnico.py** Download de todos os boletins de estudantes do IFS de um determinado curso, disponíveis no SIGAA desde que o usuário faça login com um perfil com as permissões para acessar os boletins. Dependência principal: **Selenium**.
- **busca\_siape.py** Busca do número da matrícula SIAPE de docentes. Dependências principais: **BeaultifulSoap** e a **Requests_HTML**.

**Autor:** Rubens Matos