from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from config import conectar_mysql, SECRET_KEY, DEBUG  

app = Flask(__name__)
app.secret_key = SECRET_KEY

# =============================
#       ROTA PRINCIPAL
# =============================
@app.route("/")
def home():
    if "usuario_id" in session:
        return redirect('/dashboard')
    return redirect('/login_page')

# =============================
#       PÁGINA DE LOGIN
# =============================
@app.route('/login_page')
def login_page():
    if "usuario_id" in session:
        return redirect('/dashboard')
    return render_template("Login_Dashboard.html")

# =============================
#       LOGIN
# =============================
@app.route("/login", methods=["POST"])
def login():
    dados = request.get_json()

    if not dados:
        return jsonify({"status": "erro", "mensagem": "JSON não enviado"})

    email = dados.get("email")
    senha = dados.get("senha")

    if not email or not senha:
        return jsonify({"status": "erro", "mensagem": "Campos vazios"})

    try:
        conn = conectar_mysql()
        if conn is None:
            return jsonify({"status": "erro", "mensagem": "Erro de conexão com o banco"})
            
        cursor = conn.cursor(dictionary=True)

        query = """
        SELECT id, email, senha, nome_completo 
        FROM tb_usuario 
        WHERE email = %s
        """
        cursor.execute(query, (email,))
        usuario = cursor.fetchone()

        cursor.close()
        conn.close()

        if not usuario:
            return jsonify({"status": "erro", "mensagem": "Usuário não encontrado"})

        if usuario["senha"] != senha:
            return jsonify({"status": "erro", "mensagem": "Senha incorreta"})

        session["usuario_id"] = usuario["id"]
        session["usuario_nome"] = usuario["nome_completo"]

        return jsonify({
            "status": "sucesso",
            "usuario": usuario["nome_completo"]
        })

    except Exception as e:
        print("Erro MySQL:", e)
        return jsonify({"status": "erro", "mensagem": "Erro no servidor"})

# =============================
#       PÁGINA DE CADASTRO
# =============================
@app.route('/register_page')
def register_page():
    if "usuario_id" in session:
        return redirect('/dashboard')
    return render_template("register.html")

# =============================
#       CADASTRO
# =============================
@app.route("/register", methods=["POST"])
def register():
    dados = request.get_json()

    if not dados:
        return jsonify({"status": "erro", "mensagem": "Dados não enviados"})
    
    nome_completo = dados.get("nome_completo")
    cpf = dados.get("cpf")
    matricula = dados.get("matricula")
    email = dados.get("email")
    senha = dados.get("senha")
    data_nascimento = dados.get("data_nascimento", "2000-01-01")

    if not all([nome_completo, cpf, matricula, email, senha]):
         return jsonify({"status": "erro", "mensagem": "Todos os campos são obrigatórios"})

    try:
        conn = conectar_mysql()
        if conn is None:
            return jsonify({"status": "erro", "mensagem": "Erro de conexão com o banco"})
            
        cursor = conn.cursor(dictionary=True)

        query_check = "SELECT id, email, cpf, matricula FROM tb_usuario WHERE email = %s OR cpf = %s OR matricula = %s"
        cursor.execute(query_check, (email, cpf, matricula))
        usuario_existente = cursor.fetchone()

        if usuario_existente:
            cursor.close()
            conn.close()
            
            if usuario_existente['email'] == email:
                return jsonify({"status": "erro", "mensagem": "E-mail já cadastrado na base."})
            elif usuario_existente['cpf'] == cpf:
                return jsonify({"status": "erro", "mensagem": "CPF já cadastrado na base."})
            else:
                return jsonify({"status": "erro", "mensagem": "Matrícula já cadastrada na base."})

        query_insert = """
            INSERT INTO tb_usuario 
            (nome_completo, cpf, matricula, email, senha, data_nascimento, data_cadastro, ativo) 
            VALUES (%s, %s, %s, %s, %s, %s, NOW(), 1)
        """
        
        cursor.execute(query_insert, (nome_completo, cpf, matricula, email, senha, data_nascimento))
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({"status": "sucesso", "mensagem": "Usuário cadastrado com sucesso!"})

    except Exception as e:
        print("Erro MySQL no Cadastro:", e)
        if 'conn' in locals() and conn.is_connected():
            conn.rollback()
        return jsonify({"status": "erro", "mensagem": f"Erro interno: {str(e)}"})

# =============================
#       DASHBOARD
# =============================
@app.route('/dashboard')
def dashboard():
    if "usuario_id" not in session:
        return redirect('/login_page')
    return render_template("dashboard.html", usuario=session)

# =============================
#       LOGOUT
# =============================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login_page")

if __name__ == "__main__":
    app.run(debug=DEBUG)