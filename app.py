import os
import requests
from flask import Flask, request, jsonify, redirect
from dotenv import load_dotenv
import mercadopago # Importando a ferramenta!

# Carrega as "senhas" do nosso arquivo .env
load_dotenv()

# Inicializa o servidor Flask
app = Flask(__name__)

# --- CONFIGURAÇÃO DO MERCADO PAGO ---
# Pega a sua Chave Secreta (Access Token) do Render
MP_ACCESS_TOKEN = os.getenv('MP_ACCESS_TOKEN')
sdk = mercadopago.SDK(MP_ACCESS_TOKEN)

# --- NOSSO CATÁLOGO DE PRODUTOS "MANUAL" ---
# Esta parte continua igual. Aqui você gerencia seus produtos.
CATALOGO_DE_PRODUTOS = {
    "cn_3_4": {
        "id": "cn_3_4",
        "nome": "Carneiro Hidráulico 3/4 Polegada",
        "descricao": "Bomba carneiro hidráulico de 3/4 de polegada, alta eficiência.",
        "preco": 499.90, # Use ponto para centavos
        "imagem_url": "https://i.imgur.com/link-para-sua-imagem.jpg",
        "link_ml": "https://link-do-seu-produto-no-mercado-livre.com.br"
    },
    "cn_1_0": {
        "id": "cn_1_0",
        "nome": "Carneiro Hidráulico 1 Polegada",
        "descricao": "Bomba carneiro hidráulico de 1 polegada, modelo profissional.",
        "preco": 650.00,
        "imagem_url": "https://i.imgur.com/link-para-outra-imagem.jpg",
        "link_ml": "https://link-do-seu-outro-produto-no-mercado-livre.com.br"
    }
}
# -----------------------------------------------

# --- ROTA DE API: /api/produtos ---
# Esta rota envia seu catálogo para o site (Netlify)
@app.route('/api/produtos', methods=['GET'])
def get_produtos():
    print("📞 Pedido recebido: Enviando catálogo de produtos.")
    lista_de_produtos = list(CATALOGO_DE_PRODUTOS.values())
    return jsonify(lista_de_produtos)

# --- ROTA DE API: /api/processar-pagamento ---
# Esta é a rota que o Checkout Transparente vai usar.
@app.route('/api/processar-pagamento', methods=['POST'])
def processar_pagamento():
    print("📞 Pedido recebido: Processando pagamento...")
    try:
        dados = request.json
        produto_id = dados.get('produto_id')
        produto = CATALOGO_DE_PRODUTOS.get(produto_id)

        if not produto:
            return jsonify({"erro": "Produto não encontrado"}), 404

        payment_data = {
            "transaction_amount": produto['preco'],
            "token": dados.get('token'),
            "description": produto['nome'],
            "installments": dados.get('installments'),
            "payment_method_id": dados.get('payment_method_id'),
            "payer": dados.get('payer')
        }

        payment_response = sdk.payment().create(payment_data)
        payment = payment_response["response"]

        print(f"✅ Pagamento processado! Status: {payment['status']}")

        return jsonify({
            "status": payment["status"],
            "status_detail": payment["status_detail"],
            "id": payment["id"]
        })

    except Exception as e:
        print(f"🚨 Erro ao processar pagamento: {e}")
        erro_mp = e.cause if hasattr(e, 'cause') else str(e)
        return jsonify({"erro": "Falha no pagamento", "detalhes": erro_mp}), 500

# --- ROTA INICIAL (SÓ PARA TESTAR) ---
@app.route('/')
def homepage():
    return "<h1>O motor da LOJA (V5.1 - Transparente) está funcionando! 🚀</h1><p>Use /api/produtos para ver o catálogo.</p>"

# --- INICIANDO O SERVIDOR ---
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

