# tp-03-lab-exp

Trabalho Prático #03 para a disciplina de Laboratório de Experimentação de Software do curso de Engenharia de Software na PUC-Minas.

Aluno: Gabriel Henrique Souza Haddad Campos

Repositório: https://github.com/Haddadson/tp-03-lab-exp

A proposta do trabalho consiste na construção de uma aplicação que efetue consultas com paginação à API do GitHub utilizando GraphQL e Python.
Deve-se minerar dados dos 100 repositórios mais populares feitos em Python e os 100 repositórios mais populares feitos em Java a fim de responder as questões abaixo:

## Questões de pesquisa
1. Quais as características dos top-100 repositórios Java mais populares?
2. Quais as características dos top-100 repositórios Python mais populares?
3. Repositórios Java e Python populares possuem características de "boa qualidade" semelhantes?
4. A popularidade influencia nas características dos repositórios Java e Python?

## Métricas
Utilizaremos como fatores de qualidade métricas associadas à quatro dimensões:  
**Popularidade**: Número de estrelas, número de watchers, número de forks dos repositórios coletados  
**Tamanho**: Linhas de código (LOC e SLOC) e linhas de comentários  
**Atividade**: Número de releases, frequência de publicação de releases (número de releases / dias)  
**Maturidade**: Idade (em anos) de cada repositório coletado  

Para respondê-las, será necessário realizar uma análise quantitativa dos dados obtidos para identificar os valores correspondentes às métricas estipuladas.
Também será necessário clonar cada repositório localmente para realizar uma análise do código, contabilizando as LOCs e SLOCs e obtendo outras métricas de qualidade.

## Relatório Final
Para cada uma das questões de pesquisa, faça uma sumarização dos dados obtidos através de valores medianos. Mesmo que de forma informal, elabore hipóteses sobre o que você espera de resposta e tente analisar a partir dos valores obtidos.

Elabore um documento que apresente:

i. uma introdução simples com hipóteses informais;

ii. a metodologia que você utilizou para responder às questões de pesquisa;

iii. os resultados obtidos para cada uma delas;

iv. a discussão sobre o que você esperava como resultado (suas hipóteses) e os valores obtidos.


## Execução

Para execução do script, é necessário instalar as dependências utilizando os comandos abaixo:

> pip install requests

> pip install dump

> pip install python-dateutil

> pip install python_loc_counter

É necessário possuir o Git instalado para efetuar a clonagem dos repositórios.

Também é necessário inserir um token pessoal de desenvolvedor para acesso à API do GitHub no trecho indicado no código.

Após isso, basta executar o script e os arquivos CSV "ResultadoPython.csv" e "ResultadoJava.csv" serão criados na mesma pasta.
Durante a execução, serão exibidos logs informando o progresso, erros e retentativas das chamadas.
