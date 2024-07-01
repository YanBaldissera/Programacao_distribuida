import requests
from datetime import datetime

#Criando clientes
#response = requests.post('http://localhost:5000/cliente/jose/1234/500')
#response = requests.post('http://localhost:5000/cliente/claytin/1234/500')
#Editando clientes
#response = requests.post('http://localhost:5000/cliente/1/250')
#response = requests.get('http://localhost:5000/cliente')
#response = requests.post('http://localhost:5000/cliente/2/300')
#response = requests.delete('http://localhost:5000/cliente/2')
#Criando seletores
#response = requests.post('http://localhost:5000/seletor/seletor1/123.123')
#response = requests.post('http://localhost:5000/seletor/seletor2/122.122')
#Editando seletores
#response = requests.post('http://localhost:5000/seletor/1/seletorB/111111')
#response = requests.post('http://localhost:5000/seletor/2/seletorA/222222')
#response = requests.delete('http://localhost:5000/seletor/2')


requests.delete('http://localhost:5000/transacoes/delete_all')

response = requests.post('http://localhost:5000/transacoes/1/4/100')
response = requests.post('http://localhost:5000/transacoes/2/4/111')
response = requests.post('http://localhost:5000/transacoes/4/3/110')
response = requests.post('http://localhost:5000/transacoes/1/2/100')
response = requests.post('http://localhost:5000/transacoes/2/5/111')
response = requests.post('http://localhost:5000/transacoes/1/4/100')
response = requests.post('http://localhost:5000/transacoes/2/4/111')
response = requests.post('http://localhost:5000/transacoes/4/3/110')
response = requests.post('http://localhost:5000/transacoes/1/2/100')
response = requests.post('http://localhost:5000/transacoes/2/5/111')
response = requests.get('http://localhost:5000/transacoes')

#transacoes/<int:rem>/<int:reb>/<int:valor>', methods = ['POST']

response = requests.get('http://localhost:5000/transacoes')

transacoes = response.json()

for transferencia in transacoes:
    print(transferencia)

