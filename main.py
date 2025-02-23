from fastapi import FastAPI, HTTPException, Query
# from get_search_results.generated_code_get_search_results import make_uber_eats_post_request, parse_restaurants_with_openai
import subprocess
import logging
import os
import signal
import shutil

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)

# Access the OpenAI API key from environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")

if not openai_api_key:
    raise RuntimeError("OpenAI API key is not set. Please set the OPENAI_API_KEY environment variable.")

# @app.get("/run-script")
# def run_script_endpoint(dish_type: str = Query(..., description="Type of dish to search for")):
#     try:
#         # Construct the command to run the script with the parameter
#         command = ["python", "get_search_results/generated_code_get_search_results.py", dish_type]
        
#         # Run the command and capture the output
#         result = subprocess.run(command, capture_output=True, text=True, check=True)
        
#         # Return the output of the script
#         return {"output": result.stdout}
#     except subprocess.CalledProcessError as e:
#         raise HTTPException(status_code=500, detail=f"Script error: {e.stderr}")
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

@app.get("/run-integuru")
def run_integuru_endpoint(api_usage_needed: str = Query(..., description="API usage needed")):
    try:
        logging.info("Starting the process to create HAR file.")
        # Run the command to create HAR file
        subprocess.run(["poetry", "run", "python", "create_har.py"], check=True)
        logging.info("HAR file created successfully.")
        
        logging.info("Running integuru with the provided API usage prompt.")
        # Run the command to run integuru
        result = subprocess.run(["poetry", "run", "integuru", "--prompt", api_usage_needed, "--model", "gpt-4o", "--generate-code", "--max_steps", "30"], capture_output=True, text=True, check=True)
        logging.info("Integuru ran successfully.")
        
        # Return the output of integuru
        return {"output": result.stdout}
    except subprocess.CalledProcessError as e:
        logging.error(f"Integuru error: {e.stderr}")
        raise HTTPException(status_code=500, detail=f"Integuru error: {e.stderr}")
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/run-steam-rec")
def run_steam_rec(game_type: str = Query(..., description="Type of game to search for")):
    try:
        # Pass the game_type as an argument to the script
        results = subprocess.run(
            ["poetry", "run", "python", "steam_rec/generated_code.py", game_type],
            check=True, capture_output=True, text=True
        )
        return {"status": "Steam rec script ran successfully", "results": results.stdout}
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Steam rec script error: {e.stderr}")

@app.get("/deploy-tool")
def deploy_tool_endpoint(tool_name: str = Query(..., description="Name of the tool to deploy")):
    try:
        logging.info(f"Attempting to deploy tool: {tool_name}")
        # Create a copy of generated_code.py with the desired name
        shutil.copy("generated_code.py", f"{tool_name}_generated_code.py")
        logging.info(f"Renamed generated_code.py to {tool_name}_generated_code.py")

        # Add a new endpoint for the tool
        with open("main.py", "r") as file:
            main_py_code = file.read()
        
        # Ensure prompt is a string
        prompt = (
            f"Create a new endpoint named {tool_name} for this file, similar to the existing endpoints in this file. "
            f"Here is the current code:\n{main_py_code}. "
            f"Note the new generated code is called {tool_name}_generated_code.py and in the same directory as this file. "
            f"ONLY return the code to append to the file, NO OTHER TEXT!!!."
        )
        
        from openai import OpenAI
        client = OpenAI()
        completion = client.chat.completions.create(
          model="gpt-4o",
          messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}  # Ensure prompt is a string
          ],
        )
        code_to_append = completion.choices[0].message.content
        # Remove the potential wrapper of ```python ... ``` for the generated code
        code_to_append = code_to_append.replace("```python\n", "").replace("\n```", "")
        code_to_append = "\n" + code_to_append + "\n"
        logging.info(f"Generated code for {tool_name} endpoint: {code_to_append}")

        with open("main.py", "a") as file:
            file.write(code_to_append)
        logging.info(f"Appended code for {tool_name} endpoint to main.py")

        file_directory = "/Users/alfredlong/Documents/onetool-demo/app/(preview)/api/chat/route.ts"
        # Read the route.ts file
        with open(file_directory, "r") as file:
            route_ts_code = file.read()
        
        # Ensure prompt is a string
        prompt = (
            f"Create a new route code for the tool named {tool_name} in the route.ts file. "
            f"Here is the current code:\n{route_ts_code}. "
            f"Here is the new backend code:\n{code_to_append}. "
            f"Note the new tool is called {tool_name} and should be added to the existing routes. "
            f"ONLY return the new full route code, NO OTHER TEXT!!!."
        )
        
        # Use OpenAI to generate the new route code
        from openai import OpenAI
        client = OpenAI()
        completion = client.chat.completions.create(
          model="gpt-4o",
          messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}  # Ensure prompt is a string
          ],
        )
        new_route_code = completion.choices[0].message.content
        # Remove the potential wrapper of ```typescript ... ``` for the generated code
        new_route_code = new_route_code.replace("```typescript\n", "").replace("\n```", "")
        logging.info(f"Generated new route code for {tool_name}: {new_route_code}")

        # Save a copy of the original file
        shutil.copy(file_directory, f"{file_directory}.bak")
        logging.info(f"Saved a copy of {file_directory} as {file_directory}.bak")

        # Append the new route code to the original file
        with open(file_directory, "w") as file:
            file.write(new_route_code)
        logging.info(f"Appended new route code for {tool_name} to {file_directory}")

        return {"status": f"{tool_name} deployed successfully"}
    except Exception as e:
        logging.error(f"Failed to deploy tool: {tool_name}. Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))




@app.get("/ubereats-sushi-recommendations")
def ubereats_sushi_recommendations(dish_type: str = Query("sushi", description="Type of dish to search for")):
    try:
        logging.info(f"Fetching sushi recommendations from UberEats for dish type: {dish_type}")
        # Pass the dish_type as an argument to the script
        results = subprocess.run(
            ["python", "UberEatsSushiRecommendations_generated_code.py", dish_type],
            check=True, capture_output=True, text=True
        )
        logging.info(f"Sushi recommendations fetched successfully: {results.stdout}")
        return {"status": "Request processed successfully", "results": results.stdout}
    except subprocess.CalledProcessError as e:
        error_msg = f"Error during fetching sushi recommendations: {e.stderr}"
        logging.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logging.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)
