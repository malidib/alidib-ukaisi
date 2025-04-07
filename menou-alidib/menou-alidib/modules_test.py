# Evaluation tests.
import subprocess
import os


# Test create dataset
script_path = os.path.join(os.path.dirname(__file__), './', 'create_dataset.py')
subprocess.run(['python', script_path])


# Basic test phase_1.py (user_facing_task)
evaluation_command = f"inspect eval phase_1.py --model openai/gpt-4o-mini --limit 5 --max-connections 10 --working-limit 250 --temperature 0.1"
process = subprocess.run(evaluation_command,shell=True, capture_output=False)
# This should return a user_facing_task in /logs/ accessible with inspect view


# Basic test phase_2.py (code_improvement_task)
evaluation_command = f"inspect eval phase_2.py --model openai/gpt-4o-mini --limit 5 --max-connections 10 --working-limit 250 --temperature 0.1"
process = subprocess.run(evaluation_command,shell=True, capture_output=False)
# This will run for a while and should return a code_improvement_task in /logs/ accessible with inspect view in addition
#      to multiple user_facing_task logs and other (.db and .py) files. 


# Basic test full pipeline
evaluation_command = f"inspect eval phase_2.py --model openai/o3-mini --limit 5 --max-connections 10 --working-limit 250"
process = subprocess.run(evaluation_command,shell=True, capture_output=False)
# This will run for a while and should return a code_improvement_task in /logs/ accessible with inspect view in addition
#      to multiple user_facing_task logs and other (.db and .py) files. 


# Test postprocessing (after testing the full pipeline)
script_path = os.path.join(os.path.dirname(__file__), './', 'postprocessing_results.py')
subprocess.run(['python', script_path])
