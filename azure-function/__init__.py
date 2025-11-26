import logging
import azure.functions as func
import requests
import json
from azure.storage.blob import BlobServiceClient
import os
from datetime import datetime

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        alimento = req.params.get("alimento")
        quantidade = req.params.get("quantidade")

        if not alimento or not quantidade:
            return func.HttpResponse(
                "Parâmetros obrigatórios: alimento, quantidade (g)",
                status_code=400
            )

        quantidade = float(quantidade)

        # 1) Busca na API USDA
        api_key = os.getenv("USDA_API_KEY")
        url = f"https://api.nal.usda.gov/fdc/v1/foods/search?api_key={api_key}&query={alimento}"

        response = requests.get(url)
        data = response.json()

        if "foods" not in data or len(data["foods"]) == 0:
            return func.HttpResponse(
                f"Alimento '{alimento}' não encontrado na USDA.",
                status_code=404
            )

        alimento_info = data["foods"][0]

        # pega calorias (Energy in kcal)
        calorias_100g = None
        for nutrient in alimento_info["foodNutrients"]:
            if nutrient["nutrientName"].lower() in ["energy", "calories", "energy (kcal)"]:
                calorias_100g = nutrient["value"]
                break

        if calorias_100g is None:
            return func.HttpResponse(
                "Não foi possível encontrar calorias na USDA.",
                status_code=500
            )

        # 2) Cálculo da ingestão
        calorias_totais = (calorias_100g * quantidade) / 100

        resultado = {
            "alimento": alimento,
            "quantidade_g": quantidade,
            "calorias_por_100g": calorias_100g,
            "calorias_totais": calorias_totais,
            "timestamp": datetime.utcnow().isoformat()
        }

        # 3) Salva no Blob Storage
        conn_str = os.getenv("STORAGE_CONNECTION_STRING")
        container = os.getenv("BLOB_CONTAINER")

        blob_client = BlobServiceClient.from_connection_string(conn_str)
        container_client = blob_client.get_container_client(container)

        try:
            container_client.create_container()
        except:
            pass

        blob_name = f"ingestao_{datetime.utcnow().timestamp()}.json"
        container_client.upload_blob(blob_name, json.dumps(resultado), overwrite=True)

        # 4) Retorna para o usuário
        return func.HttpResponse(
            json.dumps(resultado, indent=2),
            mimetype="application/json",
            status_code=200
        )

    except Exception as e:
        logging.error(str(e))
        return func.HttpResponse(str(e), status_code=500)
