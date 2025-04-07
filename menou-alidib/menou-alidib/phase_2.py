# ------------------------------
# Library Imports + config
# ------------------------------
import os
import sys
import subprocess

from inspect_ai import Task, task
from inspect_ai.dataset import csv_dataset
from inspect_ai.scorer import match
from inspect_ai.solver import (basic_agent, system_message, user_message,use_tools,chain,Solver,solver)
from inspect_ai.tool import (bash,tool)
from inspect_ai.model import get_model

from utils import (
    save_to_txt,
    save_to_py,
    run_full_python,
    read_code_from_file,
    audit_code_tool
)
from prompts_phase_2 import MAIN_SYSTEM_PROMPT
sys.stdout.reconfigure(line_buffering=True)
# The path to the original code file that is subject to improvement.
original_code = read_code_from_file("./phase_1.py")
#-------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------


@tool
def run_phase_1():
    async def execute(filename: str) -> str:
        """
        Executes Inspect code with access to installed packages.
        Args:
            filename (str): The python filename to execute with inspect.
        Returns:
            str: The standard output or error message from execution.
        """
        try:
            evaluation_command = f"inspect eval {filename} --model {get_model()} --limit 500 --max-connections 20 --working-limit 250 --temperature 0."
            process = subprocess.run(evaluation_command,shell=True, capture_output=False)

        except Exception as e:
            pass
        
    return execute



@task
def code_improvement_task(solver: Solver | None = None):
    if solver is None:
        solver = basic_agent(
                    init=[system_message(MAIN_SYSTEM_PROMPT),user_message("{input}") ],
                    tools=[bash(timeout=180), run_full_python(),audit_code_tool(),save_to_txt(),save_to_py(),run_phase_1()],
                    max_attempts=1,)
    else:
        solver = chain(
            use_tools([bash(timeout=180), run_full_python(),audit_code_tool(),save_to_txt(),save_to_py(),run_phase_1()]),
            solver
        )
    return Task(
        dataset = csv_dataset("dataset_2.csv"),         
        solver = solver,
        scorer = match(numeric=True),
        sandbox = "local"
    )