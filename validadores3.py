#para quinta feira: montar as portas e começar o seletor

import sqlite3
from flask import Flask, render_template, jsonify
from datetime import datetime
import uuid

app = Flask("VALIDADOR")

def conectar_bd():
    conn = sqlite3.connect('usuarios.db')
    return conn, conn.cursor()


from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "key123"

usuarios = {
    'José': 'jose',
    'Yan': 'yan',
    'Jonathan': 'jonathan'
}

@app.route('/')
def index():
    if 'usuario' in session:
        return f'Olá, {session["usuario"]}! <a href="/logout">Sair</a>'
    return 'Você não está logado. <a href="/login">Login</a>'

validador_logado = "Jonathan"
@app.route('/login', methods=['GET', 'POST'])
def login():
    global validador_logado 
    if request.method == 'POST':
        usuario = request.form['usuario']
        senha = request.form['senha']
        if usuario in usuarios and usuarios[usuario] == senha:
            session['usuario'] = usuario
            validador_logado = usuario
            return redirect(url_for('online'))
        return 'Credenciais inválidas. <a href="/login">Tentar novamente</a>'
    return render_template('login.html')

def validar_transacao(valor, pagadorID, recebedorID, horario):
    conn, cursor = conectar_bd()
    global validador_logado
    cursor.execute("SELECT saldo FROM validadores WHERE nome = ?", (validador_logado,))
    saldo_validador_logado = cursor.fetchone()

    pagante = dict()
    recebente = dict()
    cursor.execute("SELECT * FROM usuarios WHERE id = ?", (pagadorID,))
    
    for x in cursor.fetchall():
        pagante['id'] = x[0]
        pagante['nome'] = x[1]
        pagante['saldo'] = x[2]

    cursor.execute("SELECT * FROM usuarios WHERE id = ?", (recebedorID,))
    
    for x in cursor.fetchall():
        recebente['id'] = x[0]
        recebente['nome'] = x[1]
        recebente['saldo'] = x[2]

    print(valor)
    valor_taxa = int(valor) + (int(valor) * 0.02)


    print(validador_logado)
    cursor.execute("SELECT chave_unica FROM validadores WHERE nome = ?", (validador_logado,))
    chave = cursor.fetchall()
    print(chave)

    if valor_taxa < pagante['saldo'] and horario < datetime.now():
        return {"status": "Transação válida", "chave" : chave}
    else:
        return {"status": "Transação inválida", "chave" : chave}

@app.route('/validar_transacao', methods=['GET', 'POST'])
def validar_transacao_route():
    connection, cursor = conectar_bd()
    dados_transacao = request.json

    valor = dados_transacao['valor']
    pagadorID = dados_transacao['remetente']
    recebedorID = dados_transacao['recebedor']
    data_horario = dados_transacao['horario'] = datetime.strptime(dados_transacao['horario'], "%Y-%m-%d %H:%M:%S")
    

    resultado_transacao = validar_transacao(valor, pagadorID, recebedorID, data_horario)
    
    return jsonify(resultado_transacao)

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('index'))

@app.route('/online', methods=['GET', 'POST'])
def online():
    return "O validador está online"



if __name__ == '__main__':
    app.run(debug=True, port=5003)




#cria o elemento de conexão com o banco de dados e inicializa o cursor, o cursor é resposável por executar todas as funções no database, seja criar tabela, deletar, inserir dados, tudo.
def criar_tabela():
    connection = sqlite3.connect('usuarios.db')
    cursor = connection.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS validadores (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        saldo REAL NOT NULL,
        flags INT NOT NULL,
        chave_unica TEXT NOT NULL
    );
    """)
    connection.commit()
    connection.close()

# Função para inserir dados na tabela usuarios
def inserir_usuarios():
    connection = sqlite3.connect('usuarios.db')
    cursor = connection.cursor()
    dados = [
        ('João Silva', 1000.00),
        ('Maria Santos', 500.50),
        ('Pedro Oliveira', 750.25),
        ('Ana Pereira', 1200.75),
        ('Carlos Ferreira', 900.80)
    ]

    for dado in dados:
        cursor.execute("INSERT INTO usuarios (nome, saldo) VALUES (?, ?)", dado)

    connection.commit()
    connection.close()

# Função para inserir dados na tabela validadores
def inserir_validadores():
    connection = sqlite3.connect('usuarios.db')
    cursor = connection.cursor()

    chave_unica_str1 = str(uuid.uuid4())
    chave_unica_str2 = str(uuid.uuid4())
    chave_unica_str3 = str(uuid.uuid4())
    chave_unica_str4 = str(uuid.uuid4())

    dados = [
        ('José', 10000.00, 0, chave_unica_str1),
        ('Yan', 220349.00, 0, chave_unica_str2),
        ('Jonathan', 24242424.24, 0, chave_unica_str3),
        ('Ruan', 201015.00, 0, chave_unica_str4)
    ]

    for dado in dados:
        cursor.execute("INSERT INTO validadores (nome, saldo, flags, chave_unica) VALUES (?, ?, ?, ?)", dado)

    connection.commit()
    connection.close()


