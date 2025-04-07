# ------------------------------
# Standard Library Imports
# ------------------------------
import os
import re
import subprocess
from typing import Callable
import os

from inspect_ai.model import get_model
# ------------------------------
# Inspect AI Tool Decorator
# ------------------------------
from inspect_ai.tool import tool
from inspect_ai.solver import generate

from prompts_phase_2 import audit_prompt_base


def universal_extract_text(response):
    """
    Attempts to extract the 'assistant text' from a wide variety of LLM response
    formats (OpenAI, Anthropic, Google PaLM, Cohere, AI21, or custom classes).
    
    1) If 'response' is a dict, check common dict-based fields.
    2) Otherwise, treat 'response' as an object with attributes.
    3) If all else fails, return str(response).
    """

    # ------------------------------
    # 1) If 'response' is a dictionary
    # ------------------------------
    if isinstance(response, dict):
        # --- OpenAI ChatCompletion style:
        #     response["choices"][0]["message"]["content"]
        try:
            return response["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError):
            pass

        # --- OpenAI older Completion style:
        #     response["choices"][0]["text"]
        try:
            return response["choices"][0]["text"]
        except (KeyError, IndexError, TypeError):
            pass

        # --- Anthropic style: response["completion"]
        try:
            return response["completion"]
        except (KeyError, TypeError):
            pass

        # --- Google PaLM style: response["candidates"][0]["content"]
        try:
            return response["candidates"][0]["content"]
        except (KeyError, IndexError, TypeError):
            pass

        # --- Cohere style: response["generations"][0]["text"]
        try:
            return response["generations"][0]["text"]
        except (KeyError, IndexError, TypeError):
            pass

        # --- AI21 style: response["completions"][0]["data"]["text"]
        try:
            return response["completions"][0]["data"]["text"]
        except (KeyError, IndexError, TypeError):
            pass

    # ------------------------------
    # 2) If 'response' is NOT a dictionary, try object-style
    # ------------------------------
    else:
        # For custom classes or namedtuples, we look for similar patterns:

        # OpenAI ChatCompletion object style:
        #   response.choices[0].message.content
        try:
            return response.choices[0].message.content
        except Exception:
            pass

        # OpenAI older Completion object style:
        #   response.choices[0].text
        try:
            return response.choices[0].text
        except Exception:
            pass

        # Anthropic object style:
        #   response.completion
        try:
            return response.completion
        except Exception:
            pass

        # (Add more checks here if you have other known object fields)

    # ------------------------------
    # 3) Fallback: return entire response as string
    # ------------------------------
    return str(response)



@tool
def save_to_txt():
    """
    A tool that saves input text to a file.
    Args:
        text: The text content to be saved.
    Returns:
        A confirmation message indicating success.
    """

    async def execute(text: str) -> str:
        """
        A tool that saves input text to a file.
        Args:
            text: The text content to be saved.
        Returns:
            A confirmation message indicating success.
        """


        file_path = "audit_log.txt"
        
        try:
            # Open the file in append mode
            with open(file_path, "a", encoding="utf-8") as file:
                file.write(text + "\n")  # Append new text with a newline
            return f"Successfully saved to {file_path}."
        except Exception as e:
            return f"Error saving to file: {str(e)}"

    return execute


@tool
def save_to_py() -> Callable[[str, str], str]:
    async def execute(filename: str, text: str) -> str:
        """
        Asynchronously saves a given text string to a specified `.py` file.

        Parameters:
            filename (str): The name of the Python file to save to. 
                            It must end with `.py`, for example: "my_script.py".
            text (str): The content to be written into the file. This is typically Python source code.

        Returns:
            str: A confirmation message indicating the result of the save operation.

        Example Usage:
            tool: save_to_py(filename="hello_world.py", text="print('Hello, world!')")

        Notes:
            - Both 'filename' and 'text' are required parameters.
            - If 'filename' does not end with '.py', an error message will be returned.
        """
        if not filename.endswith(".py"):
            return "Error: Filename must end with '.py'."

        file_path = os.path.abspath(filename)

        try:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(text.rstrip() + "\n")
            return f"Successfully saved to `{file_path}`."
        except Exception as e:
            return f"Error saving to file: {str(e)}"

    return execute


def read_code_from_file(path: str) -> str:
    """
    Reads and returns the content of the file at the specified path.
    Raises FileNotFoundError if the file does not exist.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Cannot find the file: {path}")
    try:
        with open(path, "r", encoding="utf-8") as file:
            return file.read()
    except OSError as error:
        raise RuntimeError(f"Error reading from {path}: {str(error)}")


# ----------------------------------------
# Helper Functions for File I/O and Code Extraction
# ----------------------------------------

def write_content_to_file(path: str, content: str):
    """
    Writes the provided content to the file located at the specified path.
    Creates necessary directories if they do not exist.
    """
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as file:
            file.write(content)
    except OSError as error:
        raise RuntimeError(f"Error writing to {path}: {str(error)}")

def extract_python_code(response_text: str) -> str:
    """
    Extracts Python code from a triple-backtick block labeled as python.
    If no such code block is found, returns the entire response text.
    """
    pattern = r"```python\n(.*?)```"
    match_obj = re.search(pattern, response_text, re.DOTALL)
    if match_obj:
        return match_obj.group(1).strip()
    else:
        return response_text



@tool
def run_full_python():
    """
    Executes Python code with access to installed packages.

    Args:
        script (str): The Python script to execute.

    Returns:
        str: The standard output or error message from execution.
    """
    async def execute(script: str) -> str:
        """
        Executes Python code with access to installed packages.

        Args:
            script (str): The Python script to execute.

        Returns:
            str: The standard output or error message from execution.
        """

        try:
            process = subprocess.run(
                ["python3", "-c", script], capture_output=True, text=True
            )
            return process.stdout if process.returncode == 0 else process.stderr
        except Exception as e:
            return f"Execution Error: {str(e)}"

    return execute



@tool
def audit_code_tool():
    async def execute(code_snippet: str):
        """
        Analyzes a given code snippet for security vulnerabilities.

        Args:
            code_snippet (str): The source code to be analyzed for security vulnerabilities.

        Returns:
            str: "1" if malicious, "0" if safe.
        """


        model = get_model()

        audit_prompt=audit_prompt_base +\
        f"""
        Code:
        ```python
        {code_snippet}
        ```
        """
        
        response = await model.generate(audit_prompt)
        return universal_extract_text(response)

    return execute