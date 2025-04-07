# Standard library imports
import os
import sys
import sqlite3
from datetime import datetime
# import re
# import json
# import asyncio
import random
# import subprocess

# OpenAI API
from openai import OpenAI
# import openai

# Inspect AI core modules
from inspect_ai import Task, task
from inspect_ai.dataset import csv_dataset
# from inspect_ai.dataset import Sample
from inspect_ai.scorer import match
# from inspect_ai.scorer import exact, includes
from inspect_ai.solver import (
    solver,
    generate,
    basic_agent,
    system_message,
    user_message,
    use_tools
)
from inspect_ai.solver import (basic_agent, system_message, user_message,use_tools,chain,Solver,solver)
# Inspect AI tools
from inspect_ai.tool import (
    tool,
    bash,
    python
    # Tool,
    # ToolError
)

# Inspect AI utilities
from inspect_ai.util import sandbox
# Standard library imports
import os
import sys
import sqlite3
from datetime import datetime
# import re
# import json
import asyncio
# import random
# import subprocess

# OpenAI API
from openai import OpenAI
# import openai

# Inspect AI core
from inspect_ai import Task, task
from inspect_ai.dataset import csv_dataset
# from inspect_ai.dataset import Sample
from inspect_ai.scorer import match
# from inspect_ai.scorer import exact, includes
from inspect_ai.solver import (
    solver,
    generate,
    basic_agent,
    user_message,
    system_message,
    use_tools
)

# Inspect AI tools
from inspect_ai.tool import (
    tool,
    bash,
    python
    # Tool,
    # ToolError
)

# Inspect AI utilities
from inspect_ai.util import sandbox

from textwrap import dedent
from inspect_ai.model import get_model, ModelOutput

import sys
import os
from utils import universal_extract_text, save_to_txt

from prompts_phase_1 import moderation_system_prompt, system_prompt, user_message_p1, user_message_p2

sys.stdout.reconfigure(line_buffering=True)



@tool
def log_completion_moderated():
    """
    A tool that logs a chat completion to a SQLite database.
    
    Args:
        chat_response: The chat completion text to be logged.
        
    Returns:
        A confirmation message indicating success.
    """
    async def execute(chat_response: str) -> str:

        """
        A tool that logs a chat completion to a SQLite database.
        
        Args:
            chat_response: The chat completion text to be logged.
            
        Returns:
            A confirmation message indicating success.
        """

        # Determine the script name (without extension) for a unique database filename.
        script_name = os.path.splitext(os.path.basename(__file__))[0]
        db_filename = f"completions_moderated_{script_name}.db"
        
        # Connect to the SQLite database (creating it if it doesn't exist).
        conn = sqlite3.connect(db_filename)
        c = conn.cursor()
        
        # Create the logs table if it does not exist.
        c.execute(
            "CREATE TABLE IF NOT EXISTS logs (id INTEGER PRIMARY KEY AUTOINCREMENT, content TEXT, timestamp TEXT)"
        )
        
        # Insert the chat response along with the current timestamp.
        timestamp_str = datetime.now().isoformat()
        c.execute(
            "INSERT INTO logs (content, timestamp) VALUES (?, ?)",
            (chat_response, timestamp_str)
        )
        
        # Commit changes and close the connection.
        conn.commit()
        conn.close()
        
        return "Logged successfully"

    return execute




@tool
def log_completion_unmoderated():
    """
    A tool that logs a chat completion to a SQLite database.
    
    Args:
        chat_response: The chat completion text to be logged.
        
    Returns:
        A confirmation message indicating success.
    """
    async def execute(chat_response: str) -> str:

        """
        A tool that logs a chat completion to a SQLite database.
        
        Args:
            chat_response: The chat completion text to be logged.
            
        Returns:
            A confirmation message indicating success.
        """

        # Determine the script name (without extension) for a unique database filename.
        script_name = os.path.splitext(os.path.basename(__file__))[0]
        db_filename = f"completions_unmoderated_{script_name}.db"
        
        # Connect to the SQLite database (creating it if it doesn't exist).
        conn = sqlite3.connect(db_filename)
        c = conn.cursor()
        
        # Create the logs table if it does not exist.
        c.execute(
            "CREATE TABLE IF NOT EXISTS logs (id INTEGER PRIMARY KEY AUTOINCREMENT, content TEXT, timestamp TEXT)"
        )
        
        # Insert the chat response along with the current timestamp.
        timestamp_str = datetime.now().isoformat()
        c.execute(
            "INSERT INTO logs (content, timestamp) VALUES (?, ?)",
            (chat_response, timestamp_str)
        )
        
        # Commit changes and close the connection.
        conn.commit()
        conn.close()
        
        return "Logged successfully"

    return execute

@tool
def moderation_guardrail():
    async def execute(code_snippet: str):
        """
        Analyzes a given code snippet for security vulnerabilities and potential malicious modifications.
        Utilizes the UKSI builtin generate() function to evaluate the provided code snippet.
        Args:
            code_snippet (str): The source code to be analyzed for security vulnerabilities.

        Returns:
            int: 0 if no vulnerabilities found, or 1 if security risks are detected.
        """

        prompt = moderation_system_prompt+code_snippet
        model = get_model()
        response = await model.generate(prompt)
        chat_response = universal_extract_text(response)
        return chat_response

    return execute



user_message_p=f"""{user_message_p1}  {input} {user_message_p2}"""

@task
def user_facing_task(solver: Solver | None = None):
    if solver is None:
        solver = basic_agent(
                     init=[system_message(system_prompt),user_message(user_message_p) ],
                     tools=[bash(timeout=180),python(timeout=180) ,save_to_txt(),log_completion_moderated(),\
                     log_completion_unmoderated(), moderation_guardrail()],
                     max_attempts=1,)
    else:
        # Inject common tools into any custom solver passed in
        solver = chain(
            use_tools([bash(timeout=180),python(timeout=180) ,save_to_txt(),log_completion_moderated(),\
                         log_completion_unmoderated(), moderation_guardrail()])
            ,solver
        )
    return Task(
        dataset = csv_dataset("dataset_1.csv"),         
        solver = solver,
        scorer = match(numeric=True),
        sandbox = "local"
    )
