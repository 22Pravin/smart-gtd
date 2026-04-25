from codecarbon import EmissionsTracker
import io
import sys
import os
from typing import TypedDict
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
import radon.complexity as radon_cc

import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="codecarbon")
warnings.filterwarnings("ignore", category=FutureWarning, module="codecarbon")

# Load environment variables (Make sure your .env file has OPENAI_API_KEY)
load_dotenv()

# Initialize the reasoning model
llm = ChatGroq(model="llama-3.3-70b-versatile")

# 1. Define the State


class AuditorState(TypedDict):
    task_prompt: str
    generated_code: str
    energy_consumed: float
    cyclomatic_complexity: float
    iteration_count: int
    feedback: str
    status: str  # "PASS" or "FAIL"
    max_allowed_complexity: float

# 2. Node: The Generator/Refiner


def generate_code_node(state: AuditorState) -> AuditorState:
    current_iteration = state.get("iteration_count", 0)
    print(f"\n--- GENERATION NODE (Iteration {current_iteration}) ---")

    # If there is feedback from a failed audit, tell the LLM to fix it
    if state.get("feedback"):
        system_prompt = f"You are a Green Software Expert. Refactor the following code based on this feedback: {state['feedback']}. Provide ONLY valid Python code. Do not use markdown blocks like ```python."
        user_prompt = state["generated_code"]
    else:
        system_prompt = "You are a Green Software Expert. Write highly efficient, low-energy Python code. Provide ONLY valid Python code. Do not use markdown blocks like ```python."
        user_prompt = state["task_prompt"]

    messages = [("system", system_prompt), ("human", user_prompt)]
    response = llm.invoke(messages)

    return {
        "generated_code": response.content.strip(),
        "iteration_count": current_iteration + 1
    }

# 3. Node: The Structural & Energy Auditor


def audit_code_node(state: AuditorState) -> AuditorState:
    print("--- AUDITOR NODE ---")
    code = state["generated_code"]

    # 1. Measure Cyclomatic Complexity
    try:
        blocks = radon_cc.cc_visit(code)
        complexity = sum([b.complexity for b in blocks]) / \
            len(blocks) if blocks else 0.0
    except SyntaxError:
        print("Syntax Error detected.")
        return {"status": "FAIL", "feedback": "Syntax Error detected. Fix it.", "cyclomatic_complexity": -1.0}

    # 2. Measure REAL Hardware Energy (Execution)
    print("Measuring Execution Energy...")
    # Add measure_power_secs=1 to poll the CPU every second
    tracker = EmissionsTracker(
        project_name="auditor_execution",
        log_level="error",
        measure_power_secs=1
    )
    tracker.start()

    # Redirect standard output so the LLM's print statements don't flood your terminal
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()

    execution_success = True
    try:
        # Execute the generated code
        exec(code, {"__name__": "__main__"})
    except Exception as e:
        execution_success = False
        execution_error = str(e)

    sys.stdout = old_stdout
    tracker.stop()

    # Safely extract the exact Energy Consumed (Fallback to 0.0 if execution was too fast to measure)
    try:
        emissions_data = tracker.final_emissions_data
        energy_kwh = emissions_data.energy_consumed if emissions_data else 0.0
    except AttributeError:
        energy_kwh = 0.0

    if not execution_success:
        feedback = f"The code threw an error during execution: {execution_error}. Fix the logic."
        return {"status": "FAIL", "cyclomatic_complexity": complexity, "energy_consumed": 0.0, "feedback": feedback}

    print(f"Detected Complexity: {complexity:.2f}")
    print(f"Real Energy Consumed: {energy_kwh:.15f} kWh")

    # Evaluate against thresholds
    max_allowed_complexity = state.get("max_allowed_complexity", 3.0)

    if complexity > max_allowed_complexity:
        feedback = f"Cyclomatic complexity is {complexity}, exceeding the limit of {max_allowed_complexity}. Simplify the logic."
        return {"status": "FAIL", "cyclomatic_complexity": complexity, "energy_consumed": energy_kwh, "feedback": feedback}
    else:
        return {"status": "PASS", "cyclomatic_complexity": complexity, "energy_consumed": energy_kwh, "feedback": "Metrics within green thresholds."}

# 4. Conditional Edge routing


def route_audit(state: AuditorState):
    # Stop if it passes OR if we hit the limit to prevent infinite loops
    if state["status"] == "PASS" or state["iteration_count"] >= 3:
        return END
    return "generate_code_node"


# 5. Build the Graph
workflow = StateGraph(AuditorState)
workflow.add_node("generate_code_node", generate_code_node)
workflow.add_node("audit_code_node", audit_code_node)
workflow.set_entry_point("generate_code_node")
workflow.add_edge("generate_code_node", "audit_code_node")
workflow.add_conditional_edges("audit_code_node", route_audit)

# Compile the framework
green_auditor_app = workflow.compile()

# --- Execution Test ---
if __name__ == "__main__":
    initial_state = {
        "task_prompt": "Write a Python script to sort an array using bubble sort. You MUST include a test case at the bottom that generates an array of 6000 random integers and sorts them so the execution takes a measurable amount of time (at least a few seconds).",
        "iteration_count": 0,
        "feedback": "",
        "status": "",
        "generated_code": "",
        "cyclomatic_complexity": 0.0,
        "energy_consumed": 0.0
    }

    print("Starting SMART-GTD Green Auditor Workflow...")
    final_state = green_auditor_app.invoke(initial_state)

    print("\n================ FINAL RESULT ================")
    print(f"Final Code:\n{final_state['generated_code']}\n")
    print(f"Final Complexity: {final_state['cyclomatic_complexity']}")
    print(f"Total Iterations: {final_state['iteration_count']}")
    print(f"Status: {final_state['status']}")
