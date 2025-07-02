# PROJETO BACK END PARA CÁLCULO DE REDE BAYESIANA ATRAVÉS DE ORDENS DE COMPRA

Este repositório comporta o projeto backend do sistema de recomendação de forma de pagamento para ordens de compra através de um cálculo de rede bayesiana. Este projeto se complementa com uma interface gráfica, acessível no link: <https://github.com/Erick-Pereira/oc-recomendacao-frontend>

### COMO INSTALAR E EXECUTAR O PROJETO

Requisitos: 

- Python 3.12 ou superior

> **Faça um clone ou baixe o conteúdo do repositório**:

`git clone https://github.com/vssCOSTA/TrabalhoClaudio `

> **Utilize o arquivo SQL no MySQL**

- Abra o MySQL WorkBench e execute uma instância local com o usuário `root` e a senha `root`. 

- Crie um schema com o nome `final_claudio` e selecione ele para que as alterações sejam aplicadas a ele.

- Encontre o arquivo `final_claudio_ordcompra.sql` na raíz do projeto e exporte-o para o schema creado anteriormente.

Caso o MySQL esteja instalado junto do servidor dele, nada mais é necessário.

> **Abra o projeto em uma IDE e execute os comando necessários**:


Instala as dependências necessárias:

`pip install -r requirements.txt`

Inicia o servidor FastAPI:

`python -m uvicorn main:app --reload`

Isso irá iniciar o servidor para que as requisições sejam feitas pelo frontend. As notas enviadas serão salvas no banco de dados para cálculos da rede bayesiana.
