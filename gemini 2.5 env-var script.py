# Initialize Gemini Client via Environment Variable
def get_client():
    # Python asks your operating system: "Hey, do you have a hidden variable named 'API_KEY'?"
    # If set up correctly, your OS hands back "YAHAHAHAHA" (YAHAHAHA being the api key)
    api_key = os.environ.get("API_KEY")

    # A quick safety check: if the OS didn't find it, stop the program and warn you.
    if not api_key:
        raise RuntimeError("Set API_KEY env var")

    # You hand the successfully retrieved string to Google
    return genai.Client(api_key=api_key)