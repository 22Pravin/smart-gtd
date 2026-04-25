from codecarbon import track_emissions
from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv
import os

# This line loads the variables from the .env file into your system
load_dotenv()

# LangChain will automatically look for the ANTHROPIC_API_KEY environment variable
llm = ChatAnthropic(model="claude-3-5-sonnet-20241022")


@track_emissions(project_name="Baseline_Inference_NQueens")
def generate_code_with_llm(prompt):
    print("Requesting code from LLM...")
    response = llm.invoke(prompt)
    return response.content


if __name__ == "__main__":
    task_prompt = "Write a Python solution for the N-Queens problem. Output only the code."
    generated_code = generate_code_with_llm(task_prompt)

    with open("baseline_nqueens_output.py", "w") as f:
        f.write(generated_code)
    print("Baseline generation complete. Check emissions.csv for Inference Energy.")
