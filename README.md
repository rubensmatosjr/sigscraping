# sigscraping
Extração automatizada de dados de páginas dos sistemas SIG utilizados pelo IFS

Por enquanto, o repositório possui apenas 3 scripts Python:

- Download de todas portarias emitidas pelo IFS para um determinado servidor interessado, disponibilizadas no SIPAC
- Download de todos os boletins de estudantes do IFS de um determinado curso, disponíveis no SIGAA desde que o usuário faça login com um perfil com as permissões para acessar os boletins
- Busca do número da matrícula SIAPE de docentes

O script de download de portarias tem como dependências principais o Selenium e o BeautifulSoup.

O scripts de download dos boletins tem como dependência principal apenas o Selenium.

O script de busca da matrícula SIAPE tem como dependências principais o BeaultifulSoap e a Requests_HTML
