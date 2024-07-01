import requests
from validadores import conectar_bd
from datetime import datetime
import random
import time

def verificar_validador(validador_url):
    try:
        response = requests.get(validador_url, timeout=5)
        if response.status_code == 200:
            return True
    except requests.exceptions.RequestException:
        return False
    return False

def enviar_dados_transacao(validador_url, dados_transacao):
    # Converte 'horario' para string se for um objeto datetime
    if isinstance(dados_transacao.get('horario'), datetime):
        dados_transacao['horario'] = dados_transacao['horario'].strftime("%Y-%m-%d %H:%M:%S")
    
    response = requests.post(validador_url, json=dados_transacao)
    if response.status_code == 200:
        resultado_validacao = response.json()
        conn, cursor = conectar_bd()
        cursor.execute("""SELECT chave_unica from validadores WHERE chave_unica = ?""", resultado_validacao["chave"][0], )
        chave_existente = cursor.fetchall()
        
        if chave_existente:
            if resultado_validacao["status"] == "Transação válida":
                print("A transferência foi autorizada")
                return 1, chave_existente[0][0] 
            elif resultado_validacao["status"] == "Transação inválida":
                print("Transação rejeitada pelo validador.")
                return 2, chave_existente[0][0] 
            else:
                print("Erro ao enviar transação para o validador.")
                return 3, chave_existente[0][0] 
        else:
            print("A Chave não corresponde a chave do validador")

    else:
        print(f"Erro ao enviar a transação: {response.status_code}")
        return 3, None


validador_url = "http://127.0.0.1:5001"
validador_url2 = "http://127.0.0.1:5002"
validador_url3 = "http://127.0.0.1:5003"
validador_url4 = "http://127.0.0.1:5004"

# Lista de URLs dos validadores
validadores = [validador_url, validador_url2, validador_url3, validador_url4]
    
    
def fazer_validacao(url1, url2, url3, dados_da_transacao):
    conn, cursor = conectar_bd()
    lista_resultados = list()

    if isinstance(dados_da_transacao.get('horario'), str):
        dados_da_transacao['horario'] = datetime.strptime(dados_da_transacao['horario'], "%Y-%m-%d %H:%M:%S")


    lista_resultados.append(enviar_dados_transacao(url1, dados_da_transacao))
    lista_resultados.append(enviar_dados_transacao(url2, dados_da_transacao))
    lista_resultados.append(enviar_dados_transacao(url3, dados_da_transacao))

    valor_taxa = float(dados_da_transacao['valor']) * 1.0150
    taxa = valor_taxa - float(dados_da_transacao['valor'])
    valor_seletor = taxa * 1/3
    valor_validadores = (taxa - valor_seletor) / 2

    aprovado = 0
    for resultado, chave_unica in lista_resultados:
        if resultado == 1:
            aprovado += 1
        elif resultado == 2:
            aprovado -= 1
        elif resultado == 3:
            print("A transferência não pode ser validada.")
            break

    print(f"ID do pagante: {dados_da_transacao['remetente']}")
    print(f"ID do recebedor: {dados_da_transacao['recebedor']}")
    print(f"Valor da transação: {dados_da_transacao['valor']}")
    print(f"Valor com taxa: {valor_taxa}")

    if aprovado >= 1:
        print("A transferência foi autorizada pelos validadores")
        try:
            cursor.execute("UPDATE usuarios SET saldo = saldo - ? WHERE id = ?", (valor_taxa, dados_da_transacao["remetente"]))
            cursor.execute("UPDATE usuarios SET saldo = saldo + ? WHERE id = ?", (int(dados_da_transacao["valor"]), dados_da_transacao["recebedor"]))
            conn.commit()
            print("Transação realizada com sucesso.")
        except Exception as e:
            conn.rollback()
            print(f"Erro ao realizar a transação: {e}")
    else:
        print("A transferência foi recusada pelos validadores")

    conn.close()
    lista_validadores = []

    if aprovado >= 1:
        for validacao, chave_unica in lista_resultados:
            conn, cursor = conectar_bd()
            cursor.execute("SELECT nome, saldo, flags FROM validadores WHERE chave_unica = ?", (chave_unica,))
            validador = cursor.fetchall()
            lista_validadores.append(validador)
            if validacao == 2:
                print(f"O validador {validador[0][0]} rejeitou a transação.")
                cursor.execute("UPDATE validadores SET flags = flags + 1 WHERE chave_unica = ?", (chave_unica,))
                conn.commit()
                cursor.execute("SELECT flags FROM validadores WHERE chave_unica = ?", (chave_unica,))
                print(f"O validador {validador[0][0]} recebeu uma flag.")
                flags = cursor.fetchone()[0]
                if flags >= 3:
                    print(f"O validador {validador[0][0]} recebeu 3 flags. Zerando saldo e definindo para o valor minimo. (100 moedas.)")
                    cursor.execute("UPDATE validadores SET saldo = 100 WHERE chave_unica = ?", (chave_unica,))
                    cursor.execute("UPDATE validadores SET flags = 0 WHERE chave_unica = ?", (chave_unica,))
                conn.commit()
            else:
                print(f"O validador {validador[0][0]} aprovou corretamente a transação.")
                cursor.execute("UPDATE validadores SET saldo = saldo + ? WHERE chave_unica = ?", (valor_validadores, chave_unica))
                conn.commit()
                print(f"O validador {validador[0][0]} recebeu o valor de {valor_validadores} moedas.")
        requests.post(f'http://localhost:5000/transacoes/{dados_da_transacao['id']}/1')
       

    elif aprovado < 1:
        for validacao, chave_unica in lista_resultados:
            conn, cursor = conectar_bd()
            cursor.execute("SELECT nome, saldo, flags FROM validadores WHERE chave_unica = ?", (chave_unica,))
            validador = cursor.fetchall()
            lista_validadores.append(validador)
            if validacao == 1:
                print(f"O validador {validador[0][0]} aprovou a transação.")
                cursor.execute("UPDATE validadores SET flags = flags + 1 WHERE chave_unica = ?", (chave_unica,))
                conn.commit()
                print(f"O validador {validador[0][0]} recebeu uma flag.")
                cursor.execute("SELECT flags FROM validadores WHERE chave_unica = ?", (chave_unica,))
                print(f"O validador {validador[0][0]} recebeu uma flag.")
                flags = cursor.fetchone()[0]
                if flags >= 3:
                    print(f"O validador {validador[0][0]} recebeu 3 flags. Zerando saldo e definindo para o valor minimo. (100 moedas.)")
                    cursor.execute("UPDATE validadores SET saldo = 100 WHERE chave_unica = ?", (chave_unica,))
                    cursor.execute("UPDATE validadores SET flags = 0 WHERE chave_unica = ?", (chave_unica,))
                conn.commit()
            else:
                print(f"O validador {validador[0][0]} rejeitou corretamente a transação.")
                cursor.execute("UPDATE validadores SET saldo = saldo + ? WHERE chave_unica = ?", (valor_validadores, chave_unica))
                conn.commit()
                print(f"O validador {validador[0][0]} recebeu o valor de {valor_validadores} moedas.")
        requests.post(f'http://localhost:5000/transacoes/{dados_da_transacao['id']}/2')
        
                
#fazer_validacao(validador_url, validador_url2, validador_url3, dados_transacao)
def chamar_validacoes():
    response = requests.get('http://localhost:5000/transacoes')
    transacoes = response.json()

    def validadores_on(validadores):
        validadores_online = []
        for validador in validadores:
            online = verificar_validador(validador)
            if online:
                validadores_online.append(validador)
        return validadores_online




    contagem_validador = {}
    for validador in validadores:
        contagem_validador[validador] = 0

    ultimos_validadores_selecionados = []

    def atualizar_contagem(validadores_selecionados):
        for validador in validadores_selecionados:
            if validador in ultimos_validadores_selecionados:
                contagem_validador[validador] += 1
            else:
                contagem_validador[validador] = 0
            

    for transferencia in transacoes:
        if transferencia['status'] == 0:
            validadores_online = validadores_on(validadores)
            start_time = time.time()
            while len(validadores_online) < 3:
                print("Não existem validadores o suficiente ativos na rede no momento, aguardando...")
                time.sleep(5)
                validadores_online = validadores_on(validadores)
                if time.time() - start_time > 60:
                    print("Tempo de espera excedido. Não existem validadores ativos no momento.")
                    break

            if len(validadores_online) < 3:
                continue

            validadores_selecionados = random.sample(validadores_online, 3)
            atualizar_contagem(validadores_selecionados)
            ultimos_validadores_selecionados = validadores_selecionados

            for i, validador in enumerate(validadores_selecionados):
                if contagem_validador[validador] == 5:
                    print(f"o validador {validador} será substituido")
                    novos_validadores = [v for v in validadores_online if v not in validadores_selecionados]
                    if novos_validadores:
                        validadores_selecionados[i] = random.choice(novos_validadores)
                        contagem_validador[validador] = 0
                    else:
                        print("não há nenhum validador para substituir no momento.")
                        break

            # Atualizar a lista de últimos validadores selecionados
            ultimos_validadores_selecionados = validadores_selecionados.copy()

            str_horario = transferencia['horario']
            format_horario = "%a, %d %b %Y %H:%M:%S %Z"
            transferencia['horario'] = datetime.strptime(str_horario, format_horario)
            fazer_validacao(f"{validadores_selecionados[0]}/validar_transacao", f"{validadores_selecionados[1]}/validar_transacao", f"{validadores_selecionados[2]}/validar_transacao", transferencia)

    response = requests.get('http://localhost:5000/transacoes')
    transacoes = response.json()
    print("Todas as validações foram respondidas.")
    for transferencia in transacoes:
        print(transferencia)


conn, cursor = conectar_bd()
cursor.execute(""" UPDATE  validadores set saldo = 15000 WHERE nome = 'José' """)
cursor.execute(""" UPDATE  validadores set saldo = 15000 WHERE nome = 'Jonathan' """)
cursor.execute(""" UPDATE  validadores set saldo = 15000 WHERE nome = 'Ruan' """)
conn.commit()


#1= concluido com sucesso
#2= não aprovado
#3= não executado