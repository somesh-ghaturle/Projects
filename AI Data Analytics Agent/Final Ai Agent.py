import os
import pandas as pd
import requests
import json

# Set Ollama host
os.environ["OLLAMA_HOST"] = "http://localhost:11434"

def ask_ollama_stream(prompt, model="llama3"):
    """Sends a question to Ollama and returns streaming response."""
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model,
        "prompt": prompt
    }
    headers = {"Content-Type": "application/json"}

    try:
        with requests.post(url, json=payload, headers=headers, stream=True) as response:
            response.raise_for_status()
            full_response = ""
            for line in response.iter_lines():
                if line:
                    json_response = json.loads(line)
                    if "response" in json_response:
                        print(json_response["response"], end="", flush=True)
                        full_response += json_response["response"]
            return full_response

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

# Load your dataset
# Choosing the dataset as "annual-enterprise-survey-2023-financial-year-provisional-size-bands"
# you can choose any dataset you want make sure to change it over here before Executing the File
data = pd.read_csv("/Users/somesh/Downloads/annual-enterprise-survey-2023-financial-year-provisional-size-bands.csv")

def descriptive_analytics(data):
    """Asks Ollama to summarize the dataset and provide key insights."""
    question = f"Here is a dataset: {data.head()}. What are the key insights?"
    print("\nDescriptive Analytics:")
    return ask_ollama_stream(question)

def predictive_analytics(data):
    """Asks Ollama to predict future trends based on historical data."""
    question = f"Here is a dataset: {data.head()}. Based on this data, what are the predicted trends for the future?"
    print("\nPredictive Analytics:")
    return ask_ollama_stream(question)

def data_cleaning(data):
    """Asks Ollama to suggest ways to clean or preprocess the data."""
    question = f"Here is a dataset: {data.head()}. What are some ways to clean or preprocess this data?"
    print("\nData Cleaning Suggestions:")
    return ask_ollama_stream(question)

def visualization_suggestions(data):
    """Asks Ollama to recommend the best way to visualize the data."""
    question = f"Here is a dataset: {data.head()}. What is the best way to visualize this data?"
    print("\nVisualization Suggestions:")
    return ask_ollama_stream(question)

def custom_query(data):
    """Allows the user to ask custom questions about the dataset."""
    while True:
        user_input = input("\nAsk a question about the data (or type 'exit' to quit): ")
        if user_input.lower() == "exit":
            break
        question = f"Here is a dataset: {data.head()}. {user_input}"
        print("\nOllama's Response:")
        ask_ollama_stream(question)
        print("\n")

def main():
    print("Welcome to the AI Data Analytics Agent!")
    print("Dataset Preview:")
    print(data.head())

    while True:
        print("\nSelect an option:")
        print("1. Descriptive Analytics")
        print("2. Predictive Analytics")
        print("3. Data Cleaning Suggestions")
        print("4. Visualization Suggestions")
        print("5. Custom Query")
        print("6. Exit")

        choice = input("Enter your choice (1-6): ")

        if choice == "1":
            descriptive_analytics(data)
        elif choice == "2":
            predictive_analytics(data)
        elif choice == "3":
            data_cleaning(data)
        elif choice == "4":
            visualization_suggestions(data)
        elif choice == "5":
            custom_query(data)
        elif choice == "6":
            print("Exiting the AI Data Analytics Agent. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()