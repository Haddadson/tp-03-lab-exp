import sys
import requests
from json import dump
from json import loads
from datetime import datetime
from dateutil import relativedelta
import time
from python_loc_counter import LOCCounter
import shutil
import os
import stat

#Execução da query para listagem de dados do GitHub
def run_query(json, headers):  
    print("Executando query...")
    request = requests.post('https://api.github.com/graphql', json=json, headers=headers)
    
    while (request.status_code != 200):
      print("Erro ao chamar API, tentando novamente...")
      print("Query failed to run by returning code of {}. {}. {}".format(request.status_code, json['query'],json['variables']))
      time.sleep(2)
      request = requests.post('https://api.github.com/graphql', json=json, headers=headers)
    
    return request.json()

query = """
query laboratorio {
 search (query:"stars:>10000 language:{LANGUAGE} sort:stars", type:REPOSITORY, first:5{AFTER}) {
    pageInfo{
        hasNextPage
        endCursor
    }
    nodes {
      ... on Repository {
        nameWithOwner
        createdAt
        url
        stargazers{
          totalCount
        }
        primaryLanguage{
          name
        }
        watchers {
          totalCount
        }
        forks {
          totalCount
        }
        releases{
          totalCount
        }
      }
    }
  }
}
"""

# Chave de autenticação do GitHub
# Substitua o None por uma string com seu token de acesso ao GitHub 
token_github = None # INSIRA SEU TOKEN DO GITHUB AQUI #

if token_github is None:
   raise Exception("O token do GitHub não está configurado.")

headers = {"Authorization": "Bearer " + token_github} 

# Limpa o repositório após seu uso, removendo os arquivos
def cleanRepository(folder):
  shutil.rmtree(folder, ignore_errors=True)

# Clona o repositório informado no diretório informado
def cloneRepository(gitPath, directoryPath):
  print("\n" + "Começa o git clone: " + gitPath)
  try:
    success = os.system("git clone --depth 1 %s %s" % (gitPath, directoryPath))

    if(success != 0):
      raise Exception ("Erro ao clonar") 

    print("Termina o git clone \n")

  except Exception:
    print("Tentando novamente")
    # Tenta clonar novamente
    clone_success = retryCloneRepository(gitPath, directoryPath)
    number_retries = 1
    while (not clone_success and number_retries <= 5):
      clone_success = retryCloneRepository(gitPath, directoryPath)
      number_retries += 1

# Retentativa de clonar or epositório
def retryCloneRepository(gitPath, directoryPath):
  try:
    success = os.system("git clone --depth 1 %s %s" % (gitPath, directoryPath))
    return success == 0
  except Exception:
    return False

# Efetua a mineração de dados para a linguagem especificada
def mine_data(language, csv_file_name):

  print("Minerando para " + language)

  final_query = query.replace("{AFTER}", "").replace("{LANGUAGE}", language)

  json = {
      "query":final_query, "variables":{}
  }

  total_pages = 1

  print("Pagina -> 1")
  result = run_query(json, headers)

  nodes = result['data']['search']['nodes']
  next_page  = result["data"]["search"]["pageInfo"]["hasNextPage"]

  # Paginação na consulta para listar os 100 repositórios
  while (next_page and total_pages < 20):
      total_pages += 1
      print("Pagina -> ", total_pages)
      cursor = result["data"]["search"]["pageInfo"]["endCursor"]
      next_query = query.replace("{AFTER}", ", after: \"%s\"" % cursor).replace("{LANGUAGE}", language)
      json["query"] = next_query
      result = run_query(json, headers)
      nodes += result['data']['search']['nodes']
      next_page  = result["data"]["search"]["pageInfo"]["hasNextPage"]

  # Inserindo cabeçalho de identificação de dados ao CSV
  print("Gravando cabeçalho CSV...")
  with open(sys.path[0] + "\\" + csv_file_name + ".csv", 'a+') as the_file:
          the_file.write(
            "nameWithOwner" + ";" + 
            "url" + ";" +
            "primaryLanguage->name" + ";"  +
            "stargazers->totalCount" + ";" +
            "createdAt (UTC)" + ";" + 
            "repositoryAge (years)" + ";" +
            "repositoryAge (days)" + ";" +
            "releases->totalCount" + ";" +
            "releases/repositoryAge(days)" + ";" +
            "watchers->totalCount" + ";" +
            "forks->totalCount" + ";" +
            "Total SLOC" + ";" +
            "Total linhas em branco" + ";" +
            "Total linhas comentários" + ";" +
            "Total LOC" + "\n"
          )

  numRepo = 0

  # Iterando dados retornados
  print(language + " - Iterando dados retornados...")
  for node in nodes:

    # Tratamento de dados para análise das métricas
    if node['primaryLanguage'] is None:
      primary_language = "None"
    else:
      primary_language = str(node['primaryLanguage']['name'])

    date_pattern = "%Y-%m-%dT%H:%M:%SZ"
    datetime_now = datetime.now()
    datetime_created_at = datetime.strptime(node['createdAt'], date_pattern)
    repository_age_years = relativedelta.relativedelta(datetime_now, datetime_created_at).years
    repository_age_days = (datetime_now - datetime_created_at).days

    if repository_age_days == 0:
      releases_per_days = 0
    else:
      releases_per_days = node['releases']['totalCount'] / repository_age_days

    # Preparação para clonar o repositório
    repo_path = "Repository/" + language + "/" + str(numRepo)
    if(os.path.exists(repo_path)):
      cleanRepository(repo_path)
      print("\n" + "Limpeza da pasta do Repositório: ")
    print("repo_path = " + repo_path)
    numRepo += 1

    gitURL = node['url'] + ".git"
    cloneRepository(gitURL, repo_path)

    total_sloc = 0
    total_loc = 0
    total_blank_loc = 0
    total_comment_loc = 0

    # Percorre os arquivos .java e .py do repositório para ler a quantidade de LOC, caso o repositório exista
    if(os.path.exists(repo_path)):
      for root, dirs, files in os.walk(repo_path):
        for file in files:
          if (language == "Python" and file.endswith('.py')) or (language == "Java" and file.endswith('.java')):
            fullpath = os.path.join(root, file)
            print("\nLendo arquivo " + fullpath)

            try:
              counter = LOCCounter(fullpath)
              loc_data = counter.getLOC()
            except Exception:
              print("\Erro ao ler arquivo " + fullpath + ". Continuando...")
              continue

            total_sloc += loc_data['source_loc']
            total_blank_loc += loc_data['blank_loc']
            total_loc += loc_data['total_line_count']
            total_comment_loc += loc_data['total_comments_loc']

    print("\nTotal LOC final para o repo " + node['nameWithOwner'] + " é " + str(total_loc))
    print("\nTotal SLOC final para o repo " + node['nameWithOwner'] + " é " + str(total_sloc))
    print("\nTotal LOC em branco final para o repo " + node['nameWithOwner'] + " é " + str(total_blank_loc))
    print("\nTotal LOC em branco final para o repo " + node['nameWithOwner'] + " é " + str(total_comment_loc))

    print("\n ------ Fim da análise de um repositorio ------ \n" )
    
    cleanRepository(repo_path)

    # Gravando métricas obtidas no CSV
    with open(sys.path[0] + "\\" + csv_file_name + ".csv", 'a+') as the_file:
        the_file.write(
          node['nameWithOwner'] + ";" + 
          node['url'] + ";" + 
          primary_language + ";" +
          str(node['stargazers']['totalCount']) + ";" + 
          datetime_created_at.strftime('%d/%m/%y %H:%M:%S') + ";" +
          str(repository_age_years) + ";" +
          str(repository_age_days) + ";" +
          str(node['releases']['totalCount']) + ";" +
          str(releases_per_days) + ";" +
          str(node['watchers']['totalCount']) + ";" +
          str(node['forks']['totalCount']) + ";" + 
          str(total_sloc) + ";" +
          str(total_blank_loc) + ";" +
          str(total_comment_loc) + ";" + 
          str(total_loc) + "\n"
        )
    print("\n ------ Repositorio gravado em CSV ------ \n" )
    time.sleep(2)

  print("Finalizando...")

# Inicia mineração dos dados para Python e Java   
mine_data("Python", "ResultadosPython")
mine_data("Java", "ResultadosJava")
