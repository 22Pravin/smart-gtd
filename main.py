from developer_feedback_agent import generate_developer_feedback
from green_auditor import green_auditor_app
from contextual_orchestrator import orchestrate_architecture
import os
import argparse
import warnings

# Suppress warnings for a clean terminal output
warnings.filterwarnings("ignore", category=UserWarning, module="codecarbon")
warnings.filterwarnings("ignore", category=FutureWarning, module="codecarbon")

# Import the agents from your local files


def run_smart_gtd_pipeline(developer_task: str, complexity_limit: float):
    print("\n🚀 ======================================================= 🚀")
    print("         STARTING SMART-GTD MULTI-AGENT PIPELINE")
    print("🚀 ======================================================= 🚀\n")

    # ---------------------------------------------------------
    # PHASE 1: Contextual Orchestrator (Repository Mapping)
    # ---------------------------------------------------------
    current_dir = os.getcwd()
    print(f"[1/3] Triggering Contextual Orchestrator on {current_dir}...")

    orchestrator_rules = orchestrate_architecture(current_dir)

    if not orchestrator_rules:
        orchestrator_rules = "No specific architectural rules found. Proceed with standard green coding practices."

    # ---------------------------------------------------------
    # PHASE 2: Green Auditor (Generation & Execution Loop)
    # ---------------------------------------------------------
    print("\n[2/3] Triggering Green Auditor (LangGraph Execution Loop)...")

    enriched_prompt = f"""
    Task: {developer_task}
    
    CRITICAL: You must follow these architectural rules and context mappings:
    {orchestrator_rules}
    """

    # The state is now fully dynamic, including the threshold
    initial_state = {
        "task_prompt": enriched_prompt,
        "iteration_count": 0,
        "feedback": "",
        "status": "",
        "generated_code": "",
        "cyclomatic_complexity": 0.0,
        "energy_consumed": 0.0,
        "max_allowed_complexity": complexity_limit
    }

    final_auditor_state = green_auditor_app.invoke(initial_state)

    # ---------------------------------------------------------
    # PHASE 3: Developer Feedback Agent (UI Translation)
    # ---------------------------------------------------------
    print("\n[3/3] Triggering Developer Feedback Agent (Groq UI Translation)...")

    dashboard_output = generate_developer_feedback(final_auditor_state)

    print("\n" + "="*60)
    print("               🎯 FINAL SMART-GTD DASHBOARD 🎯")
    print("="*60)
    print(dashboard_output)

    print("\n[SYSTEM] Pipeline execution complete. Ready for next developer task.")


if __name__ == "__main__":
    # Setup Command Line Argument Parsing
    parser = argparse.ArgumentParser(
        description="Run the SMART-GTD framework on a specific algorithmic task.")
    parser.add_argument(
        "--task",
        type=str,
        choices=["easy", "medium", "hard"],
        default="easy",
        help="Select the difficulty of the coding task to run."
    )
    args = parser.parse_args()

    # Define the Trial Tasks and their corresponding strictness
    tasks = {
        "easy": {
            "prompt": "Write a Python function to calculate the 35th Fibonacci number. You MUST include a test case at the bottom that executes the function 100 times in a loop so the execution takes a measurable amount of time.",
            "threshold": 3.0  # Strict: Force simple iteration
        },
        "medium": {
            "prompt": "Write a Python script to solve the 0/1 Knapsack problem. You MUST include a test case at the bottom that generates 50 items with random weights and values, and a large knapsack capacity, executing it so it takes a measurable amount of time.",
            "threshold": 5.0  # Moderate: Allow DP tables
        },
        "hard": {
            "prompt": "Write a Python script to solve the N-Queens problem. You MUST include a test case at the bottom that solves for N=11 and calculates the total number of valid board states, ensuring the execution takes a measurable amount of time.",
            "threshold": 7.0  # Relaxed: Allow recursive backtracking loops
        }
    }

    selected_task = tasks[args.task]["prompt"]
    selected_threshold = tasks[args.task]["threshold"]

    print(
        f"Initializing Trial Task: [{args.task.upper()}] with Complexity Limit: [{selected_threshold}]")

    run_smart_gtd_pipeline(selected_task, selected_threshold)
