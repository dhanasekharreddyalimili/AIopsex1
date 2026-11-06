import os
from flask import Flask, request, render_template_string
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

app = Flask(__name__)

# Replace these placeholders with your Azure AI Language resource details.
# IMPORTANT: Do not commit real credentials to a public GitHub repository.
endpoint = "https://msftfoundry2029090809.cognitiveservices.azure.com/"
api_key = "DaR7D6i3cYa34Ix0FP3Jc6paB7waT2KUYGVTxxHQhu7DlzgtTno5JQQJ99CKACHYHv6XJ3w3AAAAACOGtDEK"


def authenticate_client():
    if "YOUR-LANGUAGE-RESOURCE" in endpoint or "PASTE_YOUR_NEW" in api_key:
        raise ValueError(
            "Update the endpoint and API key placeholders in app.py "
            "with your Azure AI Language resource credentials."
        )

    return TextAnalyticsClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(api_key)
    )


def detect_language(client, text):
    documents = [{"id": "1", "text": text}]
    response = client.detect_language(documents=documents)[0]

    if response.is_error:
        raise RuntimeError(response.error.message)

    language = response.primary_language
    return {
        "language": language.name,
        "iso_code": language.iso6391_name,
        "confidence": round(language.confidence_score, 4),
    }


HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Azure AI Language Detection</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #eef2f7;
            margin: 0;
            padding: 40px 16px;
        }
        .container {
            background: white;
            max-width: 680px;
            margin: 0 auto;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 3px 14px rgba(0,0,0,.12);
        }
        h1 { color: #174a7e; }
        textarea {
            box-sizing: border-box;
            width: 100%;
            min-height: 130px;
            padding: 12px;
            font-size: 16px;
            border: 1px solid #bbb;
            border-radius: 6px;
        }
        button {
            background: #0078d4;
            color: white;
            border: 0;
            padding: 12px 24px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 16px;
        }
        button:hover { background: #005a9e; }
        .result {
            background: #e8f4ff;
            padding: 16px;
            margin-top: 22px;
            border-radius: 8px;
            text-align: left;
        }
        .error {
            background: #fff0f0;
            color: #a40000;
            padding: 12px;
            border-radius: 6px;
            margin-top: 18px;
        }
    </style>
</head>
<body>
<div class="container">
    <h1>Azure AI Language Detection</h1>
    <p>Enter text below to identify its language.</p>

    <form method="POST">
        <textarea name="text" placeholder="Example: Hello, how are you?"
                  required>{{ input_text }}</textarea>
        <br><br>
        <button type="submit">Detect Language</button>
    </form>

    {% if result %}
    <div class="result">
        <h3>Detection Result</h3>
        <p><strong>Language:</strong> {{ result.language }}</p>
        <p><strong>ISO code:</strong> {{ result.iso_code }}</p>
        <p><strong>Confidence score:</strong> {{ result.confidence }}</p>
    </div>
    {% endif %}

    {% if error %}
    <div class="error">{{ error }}</div>
    {% endif %}
</div>
</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def home():
    result = None
    error = None
    input_text = ""

    if request.method == "POST":
        input_text = request.form.get("text", "").strip()

        if not input_text:
            error = "Please enter some text."
        else:
            try:
                client = authenticate_client()
                result = detect_language(client, input_text)
            except Exception:
                app.logger.exception("Language detection failed")
                error = (
                    "Language detection failed. Check the Azure endpoint, "
                    "key, resource configuration, and App Service logs."
                )

    return render_template_string(
        HTML,
        result=result,
        error=error,
        input_text=input_text,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
