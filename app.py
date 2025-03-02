from flask import Flask, render_template, request, jsonify
import json
import ollama  # Make sure to install using: pip install ollama

app = Flask(__name__)

# NHS Domain Knowledge
with open("./text_content.json", "r", encoding="utf-8") as json_data:
    nhs_domains = json.load(json_data)
    json_data.close()


@app.route("/")
def index():
    return render_template("index.html", domains=nhs_domains)


@app.route("/domain/<domain_id>")
def domain_detail(domain_id):
    if domain_id in nhs_domains:
        return render_template(
            "domain_detail.html", domain=nhs_domains[domain_id], domain_id=domain_id
        )
    else:
        return render_template("404.html"), 404


@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.json
    user_message = data.get("message", "")
    domain_context = data.get("domain", "")

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    try:
        # Create system prompt with domain context if provided
        system_content = """You are an NHS data science assistant chatbot.
You provide helpful, accurate, and concise information about NHS data, systems, and healthcare analytics.
When suggesting approaches, prioritize NHS-approved methods and technologies.
Include references to NHS Digital standards and frameworks when relevant.
Always clarify you are an AI assistant providing general information, not specific implementation advice."""

        # Add domain-specific context if a domain was specified
        if domain_context and domain_context in nhs_domains:
            domain_info = nhs_domains[domain_context]
            system_content += f"\n\nYou are currently helping with questions about {domain_info['title']}: {domain_info['description']}."
            system_content += f"\nRelevant data sources include: {', '.join(domain_info['relevant_data_sources'])}."
            system_content += f"\nKey metrics for this domain include: {', '.join(domain_info['key_metrics'])}."

        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_message},
        ]

        # Try using ollama, but fall back to a mock response if not available
        try:
            response = ollama.chat(model="llama3", messages=messages)
            bot_response = response["message"]["content"]
        except Exception as e:
            print(f"Error using ollama: {str(e)}")
            # Fallback response
            bot_response = "I'm sorry, I couldn't connect to the language model. Please ensure Ollama is running with the llama3 model."

        return jsonify({"response": bot_response})

    except Exception as e:
        return jsonify({"error": f"Error: {str(e)}"}), 500


@app.route("/api/domains")
def get_domains():
    return jsonify(nhs_domains)


if __name__ == "__main__":
    app.run(debug=True)
