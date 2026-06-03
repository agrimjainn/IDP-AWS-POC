import boto3
import json
import time
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

AWS_CONFIG = {
    "region_name": "ap-south-1",
    "aws_access_key_id": os.getenv("AWS_ACCESS_KEY_ID", ""),
    "aws_secret_access_key": os.getenv("AWS_SECRET_ACCESS_KEY", "")
}

INPUT_BUCKET = os.getenv("INPUT_BUCKET", "my-idp-input-documents")
OUTPUT_BUCKET = os.getenv("OUTPUT_BUCKET", "my-idp-extracted-data")

s3_client = boto3.client("s3", **AWS_CONFIG)
bedrock_client = boto3.client("bedrock-runtime", **AWS_CONFIG)
bda_client = boto3.client("bedrock-data-automation-runtime", **AWS_CONFIG)

BEDROCK_PROMPT = """
You are an expert Intelligent Document Processing (IDP) agent.
Analyze the attached invoice document and extract the information.
You must output ONLY a valid JSON object matching the following schema.
Do not include any markdown formatting, preamble, backticks, or explanations.

Desired JSON Format:
{
  "headerFields": {
    "documentNumber": "",
    "purchaseOrderNumber": "",
    "shippingAmount": "",
    "taxAmount": "",
    "netAmount": "",
    "grossAmount": "",
    "tariff": "",
    "freight": "",
    "currencyCode": "",
    "documentDate": "",
    "senderName": "",
    "dueDate": ""
  },
  "lineItemFields": [
    {
      "description": "",
      "netAmount": "",
      "quantity": "",
      "unitPrice": "",
      "materialNumber": "",
      "unitOfMeasure": ""
    }
  ]
}
"""


def process_with_bedrock(document_bytes: bytes, filename: str) -> Dict[str, Any]:
    logger.info(f"Bedrock processing: {filename}")
    try:
        response = bedrock_client.converse(
            modelId="apac.amazon.nova-lite-v1:0",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "document": {
                                "format": "pdf",
                                "name": "invoice",
                                "source": {"bytes": document_bytes}
                            }
                        },
                        {"text": BEDROCK_PROMPT}
                    ]
                }
            ],
            inferenceConfig={"maxTokens": 2000, "temperature": 0.0}
        )
        raw_text = response['output']['message']['content'][0]['text'].strip()
        if raw_text.startswith("```"):
            raw_text = raw_text.split("```")[1]
            if raw_text.startswith("json"):
                raw_text = raw_text[4:]
            raw_text = raw_text.strip()
        extracted_data = json.loads(raw_text)
        return {"success": True, "filename": filename, "extractedData": extracted_data}
    except Exception as e:
        logger.error(f"Bedrock error for {filename}: {e}")
        return {"success": False, "filename": filename, "error": str(e)}


def format_bda_json(bda_data: Dict[str, Any]) -> Dict[str, Any]:
    inference = bda_data.get("inference_result", {})
    formatted_data = {
        "headerFields": {
            "documentNumber": inference.get("documentNumber", ""),
            "purchaseOrderNumber": inference.get("purchaseOrderNumber", ""),
            "shippingAmount": inference.get("shippingAmount", ""),
            "taxAmount": inference.get("taxAmount", ""),
            "netAmount": inference.get("netAmount", ""),
            "grossAmount": inference.get("grossAmount", ""),
            "tariff": inference.get("tariff", ""),
            "freight": inference.get("freight", ""),
            "currencyCode": inference.get("currencyCode", ""),
            "documentDate": inference.get("documentDate", ""),
            "senderName": inference.get("senderName", ""),
            "dueDate": inference.get("dueDate", "")
        },
        "lineItemFields": []
    }
    for item in inference.get("lineItems", []):
        formatted_data["lineItemFields"].append({
            "description": item.get("itemDescription", ""),
            "netAmount": item.get("netAmount", ""),
            "quantity": item.get("quantity", ""),
            "unitPrice": item.get("unitPrice", ""),
            "materialNumber": item.get("materialNumber", ""),
            "unitOfMeasure": item.get("unitOfMeasure", "")
        })
    return formatted_data


def clean_and_parse_s3_uri(s3_uri: str) -> tuple:
    if s3_uri.endswith(".json"):
        s3_uri = s3_uri.rsplit('/', 1)[0] + '/'
    if s3_uri.startswith("s3://"):
        s3_uri = s3_uri[5:]
    parts = s3_uri.split("/", 1)
    return parts[0], parts[1] if len(parts) > 1 else ""


def fetch_bda_results(result_s3_uri: str) -> Optional[Dict[str, Any]]:
    try:
        bucket, prefix = clean_and_parse_s3_uri(result_s3_uri)
        response = s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)
        if 'Contents' not in response:
            return None
        sorted_objects = sorted(response['Contents'], key=lambda x: x['LastModified'], reverse=True)
        json_keys = [obj['Key'] for obj in sorted_objects if obj['Key'].endswith(".json")]
        if not json_keys:
            return None
        target_key = next((k for k in json_keys if "custom_output" in k), json_keys[0])
        obj_response = s3_client.get_object(Bucket=bucket, Key=target_key)
        return json.loads(obj_response['Body'].read().decode('utf-8'))
    except Exception as e:
        logger.error(f"Error fetching BDA results: {e}")
        return None


def submit_bda_job(document_bytes: bytes, filename: str) -> Dict[str, Any]:
    try:
        s3_key = f"uploads/{int(time.time())}_{filename}"
        s3_client.put_object(Bucket=INPUT_BUCKET, Key=s3_key, Body=document_bytes)
        response = bda_client.invoke_data_automation_async(
            clientToken=f"token{int(time.time())}",
            dataAutomationConfiguration={
                "dataAutomationProjectArn": os.getenv("BDA_PROJECT_ARN", ""),
                "stage": "LIVE"
            },
            dataAutomationProfileArn=os.getenv("BDA_PROFILE_ARN", ""),
            inputConfiguration={"s3Uri": f"s3://{INPUT_BUCKET}/{s3_key}"},
            outputConfiguration={"s3Uri": f"s3://{OUTPUT_BUCKET}/results/"}
        )
        return {"filename": filename, "invocationArn": response["invocationArn"], "success": True}
    except Exception as e:
        logger.error(f"BDA submit error for {filename}: {e}")
        return {"filename": filename, "success": False, "error": str(e)}


def poll_bda_job(job: Dict[str, Any]) -> Dict[str, Any]:
    filename = job["filename"]
    invocation_arn = job["invocationArn"]
    try:
        start_time = time.time()
        while time.time() - start_time < 300:
            status_response = bda_client.get_data_automation_status(invocationArn=invocation_arn)
            status = status_response.get("status")
            logger.info(f"BDA status for {filename}: {status}")
            if status not in ["Created", "InProgress"]:
                break
            time.sleep(5)
        if status == "Success":
            output_uri = status_response.get("outputConfiguration", {}).get("s3Uri", f"s3://{OUTPUT_BUCKET}/results/")
            bda_result = fetch_bda_results(output_uri)
            if bda_result:
                return {"success": True, "filename": filename, "extractedData": format_bda_json(bda_result)}
            return {"success": False, "filename": filename, "error": "Failed to fetch results from S3"}
        return {"success": False, "filename": filename, "error": f"Job ended with status: {status}"}
    except Exception as e:
        logger.error(f"BDA poll error for {filename}: {e}")
        return {"success": False, "filename": filename, "error": str(e)}


@app.route('/api/process-documents', methods=['POST'])
def process_documents():
    try:
        files = request.files.getlist('files')
        mode = request.form.get('mode')

        if not files:
            return jsonify({"error": "No files provided"}), 400
        if mode not in ['bedrock', 'bda']:
            return jsonify({"error": "Invalid mode"}), 400

        results = []

        if mode == 'bedrock':
            for file in files:
                document_bytes = file.read()
                filename = secure_filename(file.filename)
                result = process_with_bedrock(document_bytes, filename)
                results.append(result)

        elif mode == 'bda':
            jobs = []
            for file in files:
                document_bytes = file.read()
                filename = secure_filename(file.filename)
                job = submit_bda_job(document_bytes, filename)
                jobs.append(job)

            for job in jobs:
                if job["success"]:
                    result = poll_bda_job(job)
                else:
                    result = {"success": False, "filename": job["filename"], "error": job.get("error")}
                results.append(result)

        return jsonify({"results": results}), 200

    except Exception as e:
        logger.error(f"Endpoint error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"}), 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)