import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

# Load environment variables
load_dotenv()

# Initialize the ultra-fast, low-energy Groq model for UI translation
llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.3)


def generate_developer_feedback(auditor_results: dict) -> str:
    print("Generating cognitive-friendly developer feedback...")

    system_instruction = """
    You are the Developer Feedback Agent for the SMART-GTD framework.
    Your job is to take raw technical metrics from the Green Auditor and translate them into a highly readable, low-cognitive-load summary for a human developer.
    
    The developer is about to review an AI-suggested code refactoring.
    
    Rules for your feedback:
    1. Be concise. Use bullet points.
    2. Clearly state if the code PASSED or FAILED the green thresholds.
    3. Explain the Cyclomatic Complexity and Energy measurements in simple, actionable terms.
    4. Highlight exactly what changed or what needs to be fixed to lower the cognitive burden of reading the code.
    """

    # Format the raw data from the Auditor
    raw_data_string = f"""
    Status: {auditor_results['status']}
    Cyclomatic Complexity: {auditor_results['cyclomatic_complexity']}
    Energy Consumed: {auditor_results['energy_consumed']} kWh
    Auditor Feedback: {auditor_results['feedback']}
    Code Snippet Length: {len(auditor_results['generated_code'])} characters
    """

    messages = [
        SystemMessage(content=system_instruction),
        HumanMessage(
            content=f"Here are the raw metrics from the Green Auditor:\n{raw_data_string}")
    ]

    # Generate the simplified feedback
    response = llm.invoke(messages)
    return response.content


if __name__ == "__main__":
    # Simulated output from your Green Auditor (Iteration 3 pass)
    mock_auditor_data = {
        "status": "PASS",
        "cyclomatic_complexity": 2.66,
        "energy_consumed": 0.0000000235,
        "feedback": "Metrics within green thresholds. Swapped nested loops for an early-exit while loop.",
        "generated_code": "def bubble_sort(arr):\n    swapped = True..."
    }

    feedback = generate_developer_feedback(mock_auditor_data)

    print("\n================ DEVELOPER UI DASHBOARD ================")
    print(feedback)
