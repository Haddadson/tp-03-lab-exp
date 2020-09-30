import sys
import requests
from json import dump
from json import loads
from datetime import datetime
from dateutil import relativedelta
import time

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
 search (query:"stars:>1000 and language:{LANGUAGE}", type:REPOSITORY, first:5{AFTER}) {
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

#chave de autenticação do GitHub
#INSIRA SEU TOKEN DO GITHUB AQUI#
token_github = None #Substitua o None por uma string com seu token de acesso ao GitHub 

if token_github is None:
   raise Exception("O token do GitHub não está configurado.")

headers = {"Authorization": "Bearer " + token_github} 

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

  #paginação
  while (next_page and total_pages < 20):
      total_pages += 1
      print("Pagina -> ", total_pages)
      cursor = result["data"]["search"]["pageInfo"]["endCursor"]
      next_query = query.replace("{AFTER}", ", after: \"%s\"" % cursor).replace("{LANGUAGE}", language)
      json["query"] = next_query
      result = run_query(json, headers)
      nodes += result['data']['search']['nodes']
      next_page  = result["data"]["search"]["pageInfo"]["hasNextPage"]

  #inserindo cabeçalho de identificação de dados ao csv
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
            "forks->totalCount\n"
          )

  #salvando os dados no CSV
  print(language + " - Gravando linhas CSV...")
  for node in nodes:
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

      with open(sys.path[0] + "\\" + csv_file_name + ".csv", 'a+') as the_file:
          the_file.write(
            node['nameWithOwner'] + ";" + 
            node['url'] + ";" + 
            str(node['stargazers']['totalCount']) + ";" + 
            primary_language + ";" +
            datetime_created_at.strftime('%d/%m/%y %H:%M:%S') + ";" +
            str(repository_age_years) + ";" +
            str(repository_age_days) + ";" +
            str(node['releases']['totalCount']) + ";" +
            str(releases_per_days) + ";" +
            str(node['watchers']['totalCount']) + ";" +
            str(node['forks']['totalCount']) + "\n"
          )

  print("Finalizando...")
    
mine_data("Python", "ResultadosPython")
mine_data("Java", "ResultadosJava")
