import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

# Load the API keys
load_dotenv()

# Initialize Gemini 2.5 Flash for massive context ingestion
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.1)


def scan_repository(directory_path: str) -> str:
    """Scans the local directory and compiles all Python files into a context string."""
    print(f"Scanning repository at: {directory_path}...")
    repository_context = []

    for root, dirs, files in os.walk(directory_path):
        # Ignore virtual environments and hidden folders
        if '.venv' in root or '.git' in root or '__pycache__' in root:
            continue

        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        code = f.read()
                        repository_context.append(
                            f"--- FILE: {file_path} ---\n{code}\n")
                except Exception as e:
                    print(f"Could not read {file_path}: {e}")

    return "\n".join(repository_context)


def orchestrate_architecture(repo_path: str):
    """Uses Gemini to map the architecture and find Green Technical Debt."""
    full_codebase = scan_repository(repo_path)

    if not full_codebase:
        print("No Python files found to analyze.")
        return

    print(
        f"Codebase ingested. Sending to {llm.model} for architectural mapping...")

    system_instruction = """
    You are the Contextual Orchestrator for the SMART-GTD framework. 
    Your job is to analyze the provided codebase and map its architecture.
    
    Specifically, you must:
    1. Identify any repeated code blocks or logic that violates the DRY (Don't Repeat Yourself) principle.
    2. Map the relationships between different files and modules.
    3. Identify architectural "energy hotspots" (e.g., inefficient data pipelines).
    
    Provide your output as a structured text response outlining the Architecture Summary, DRY Violations, and Refactoring Directives.
    """

    messages = [
        SystemMessage(content=system_instruction),
        HumanMessage(content=f"Here is the codebase:\n\n{full_codebase}")
    ]

    response = llm.invoke(messages)

    print("\n================ ORCHESTRATOR ANALYSIS ================")
    print(response.content)
    return response.content


if __name__ == "__main__":
    current_directory = os.getcwd()
    orchestrate_architecture(current_directory)
