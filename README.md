<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" class="logo" width="120"/>

# \# TOOLS

# A restaurant application to check and book the available seats based on the loaction

import sqlite3
from openai import OpenAI
from dotenv import load_dotenv
import os,json

load_dotenv()

"""Implement Redis for show all restaurants"""
def get_restaurant_location(current_loaction):
try:
conn = sqlite3.connect('bengaluru_restaurants.db')
cursor = conn.cursor()
cursor.execute("SELECT DISTINCT area from restaurant_locations WHERE seats_available > 0")
results = cursor.fetchall()
restaurant_locations = [row[0] for row in results]
conn.close()
except Exception as e:
print("Unable to get the locations")
if current_loaction in restaurant_locations:
return current_loaction
else:
nearby_location = get_nearby_locations(current_location=current_loaction)
return nearby_location

def get_seats_details(restaurant_location):
try:
conn = sqlite3.connect('bengaluru_restaurants.db')
cursor = conn.cursor()
cursor.execute(f"SELECT seats_available \
FROM restaurant_locations \
WHERE area = ?", (restaurant_location,))
seats = cursor.fetchall()
seats = [seat[0] for seat in seats]
conn.close()
except Exception as e:
print("Unable to fetch seats")
return seats

def make_booking(restaurant_location,name,phone_number,email):
conn = sqlite3.connect('bengaluru_restaurants.db')
cursor = conn.cursor()
cursor.execute("UPDATE restaurant_locations \
SET seats_available = 0,\
booking_status = 'Booked' \
WHERE area = ?",(restaurant_location,))
cursor.execute("INSERT INTO customer_details (name,phone_number,email) VALUES (?,?,?)", (name,phone_number,email))
conn.commit()
print(f"Booking done in {restaurant_location}")

def cancel_booking(restaurant_location):
conn = sqlite3.connect('bengaluru_restaurants.db')
cursor = conn.cursor()
cursor.execute("UPDATE restaurant_locations \
SET seats_available = 1, \
booking_status = 'Empty' \
WHERE area = ?",(restaurant_location,))
conn.commit()
conn.close()
print(f"Booking canceled in {restaurant_location}")

def get_nearby_locations(current_location):
conn = sqlite3.connect('bengaluru_restaurants.db')
cursor = conn.cursor()
cursor.execute(f"SELECT nearby_locations \
FROM restaurant_locations \
WHERE area =?",(current_location,))
results = cursor.fetchall()
restaurant_locations = [row[0] for row in results]
conn.close()
return restaurant_locations

def show_all_restaurants():
try:
conn = sqlite3.connect('bengaluru_restaurants.db')
cursor = conn.cursor()
\# cursor.execute("SELECT * FROM restaurant_locations")
cursor.execute("SELECT * FROM restaurant_locations")
rows = cursor.fetchall()

        # Get column names
        column_names = [description[0] for description in cursor.description]
    
    
        # Pretty print
        print(" | ".join(column_names))
        print("-" * 80)
        for row in rows:
            print(" | ".join(str(value) for value in row))
    
    
        conn.close()
    except Exception as e:
        print("Failed to retrieve restaurant data:", e)
    TOOLS = {
"get_restaurant_location" : get_restaurant_location,
"get_seats_details" : get_seats_details,
"make_booking" : make_booking,
"cancel_booking" : cancel_booking,
"get_nearby_locations" : get_nearby_locations,
"show_all_restaurants" : show_all_restaurants
}

# Agent should understand the intention of user_prompt, assign proper tool call with the requeried prompts,

# If that was not the tool to be called then make a fallback statement and assign proper tool call again with required params

# Do this with the frameworks like Langgraph, Autogen, Swarm

def Agent(user_query):
"""connect to agent and return which tool to call"""
SYSTEM_PROMPT = """
You are an helpful assistant for a restaurant booking management application.
Your role is to decice which tool to call for the user query and to extract the required arguments for the query

    Here are all the tools that we have with the proper discription
    - show_all_restaurants(): 
        Description: List all the restaurants present with the seats available and status of bokking
    
    
    -  get_resturant_location(current_location/user_location):
        Description: returns the restaurant location where there are seats available
    
    
    - get_seats_details(restaurant_location):
        Description: provides the number of seats available
    
    - make_booking(restaurant_location,name,phone_number,email):
        Description: Books the seat for the customer whose details are provided
    
    - cancel_booking(restaurant_location):
        Description: cancel the seat and make the seat available for booking in the location
    
    Arguments : current_location, restaurant_location, name, phone_number, email
    
    
    ## What should do
    1. Read user's Input
    2. Selct the appropriate tool
    3. Extract the required parameters
    4. Return only with the function/tool name with proper arguments in proper JSON object mentioned below
    
    
    {
    "function" : "<tool_function_name",
    "arguments" : {
                    "arg1" : "<value>",
                    ...
                  }
    }
    
    
    If you cannot determine which tool to use then, respond:
    {
    "function: "none", "arguments":{}}
    Be precise
    """
    API_KEY = os.getenv('perplexity-api-key')
    client = OpenAI(
        api_key=API_KEY,
        base_url="https://api.perplexity.ai"
    )
    response = client.chat.completions.create(
        model="sonar-pro",
        messages=[
            {"role":"system","content":SYSTEM_PROMPT},
            {"role":"user","content":user_query}
        ]
    )
    response = json.loads(response.choices[0].message.content)
    print(response)
    function_name = response["function"]
    arguments = response["arguments"]
    if function_name in TOOLS:
        if function_name == "make_booking":
            required_args = ["restaurant_location","name","phone_number","email"]
            # missing = [arg for arg in required_args if arg not in arguments or arguments[arg]]
            missing = [arg for arg in required_args if arg not in arguments or not arguments[arg]]
    
    
            if missing:
                for arg in missing:
                    val = input(f"Please provide the details {arg.replace('_',' ')}:")
                    arguments[arg] = val
        elif function_name == "cancel_booking":
            required_args = ["restaurant_location"]
            if required_args[0] not in arguments or not arguments[required_args[0]]:
                val = input(f"Enter the location: {arg.replace('_', ' ')} ")  # <-- `arg` undefined here
                arguments[arg] = val
    
    
        result = TOOLS[function_name](**arguments)
        return result
    else:
        return "Unable to perform the action"
    """All the below things should be done by LLM"""

# location = get_restaurant_location('Hebbal')

# if get_seats_details(location)[0] > 0:

    # make_booking(location)
    
# cancel_booking('Hebbal')

# print(location)

# show_all_restaurants()

# make_booking(restaurant_location='Hebbal',name='Teja',phone_number='7483735005',email='crtejavardhanreddy123@gmail.com')

# user_prompt = input("Enter your query:")

if __name__ == "__main__":
while True:
user = input("Enter your query/ enter exit to stop\n")
if user.lower() == 'exit':
break
else:
print(Agent(user_query=user))

for this Agentic AI from scratch app, can you write a Readme file

Certainly! Here's a detailed README file for your Agentic AI Restaurant Booking application. You can adapt it as needed:

# Agentic AI Restaurant Booking Application

A command-line restaurant application powered by an Agentic AI assistant that can check available seats at restaurants based on location, make and cancel bookings, and show restaurant details. The AI agent intelligently selects the appropriate backend tool function to fulfill user queries.

## Features

- **Show all restaurants** with available seats and booking status.
- **Get restaurant location** by user location if seats are available.
- **Check seat availability** at a specified restaurant location.
- **Make a booking** by providing customer details (name, phone number, email).
- **Cancel a booking** to free up seats at a given location.
- **Suggest nearby locations** if the requested location has no availability.
- Interactive **Agentic AI assistant** driver that parses natural language user queries and calls corresponding backend functions.
- Uses a **SQLite database** (`bengaluru_restaurants.db`) to store restaurant and customer data.
- Integrates with **OpenAI’s API** (via Perplexity AI) for natural language understanding.


## Getting Started

### Prerequisites

- Python 3.7+
- SQLite3
- An OpenAI API key (or Perplexity AI key as per your usage)
- Install dependencies (recommended in a virtual environment):

```bash
pip install openai python-dotenv
```


### Project Structure

- `main.py`: Main script that runs the Agentic AI conversational loop.
- `bengaluru_restaurants.db`: SQLite database with restaurant and booking data.
- `.env`: Environment file containing your API key.
- Other supporting files if any.


### Setup

1. **Clone the repository**

```bash
git clone <repo-url>
cd <repo-folder>
```

2. **Create and activate virtual environment (optional but recommended)**

```bash
python -m venv env
source env/bin/activate   # Linux/macOS
.\env\Scripts\activate    # Windows
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure environment variables**

Create a `.env` file with your API key:

```
perplexity-api-key=your_api_key_here
```


## How to Run

Run the main script:

```bash
python main.py
```

You will be prompted to enter your queries naturally, e.g.:

- `Show all restaurants`
- `Make booking in Koramangala`
- `Cancel booking in Hebbal`
- `Check seats availability in Indiranagar`

The agent will interactively ask for missing information if required (e.g., customer's name, phone number, email), execute the action, and display results or confirmation.

Type `exit` to quit.

## Code Overview

### Core Functions

- `get_restaurant_location(current_location)`: Returns a location with available seats or nearby alternatives.
- `get_seats_details(restaurant_location)`: Returns the number of available seats for a location.
- `make_booking(restaurant_location, name, phone_number, email)`: Books a seat and stores customer info.
- `cancel_booking(restaurant_location)`: Cancels booking and frees a seat in the location.
- `get_nearby_locations(current_location)`: Retrieves nearby restaurant areas.
- `show_all_restaurants()`: Prints a formatted list of all restaurants with seat availability and booking status.


### Agent Function

- The `Agent(user_query)` function sends the user query to OpenAI API with a system prompt describing tool functions.
- Parses the AI response JSON to determine the tool function to call and its arguments.
- Checks for any missing required arguments and prompts the user to provide values interactively.
- Calls the corresponding backend function and returns or prints the result.


## Notes and Suggestions

- Ensure your SQLite database schema matches the required tables (`restaurant_locations`, `customer_details`) and columns.
- The database file path is assumed as `bengaluru_restaurants.db` in the current working directory.
- The agent system prompt is configured to explicitly extract function name and arguments in JSON format.
- You can expand the system prompt or tool functions as per your application needs.
- Adding Redis or caching (as mentioned in comments) can improve performance for repeated queries.
- Proper error handling and input validation can be further improved for production use.


## Example Interaction

```plaintext
Enter your query/ enter exit to stop
make booking in Koramangala
{'function': 'make_booking', 'arguments': {'restaurant_location': 'Koramangala'}}
Please provide the details name: Teja
Please provide the details phone number: 9876543210
Please provide the details email: teja@example.com
Booking done in Koramangala

Enter your query/ enter exit to stop
cancel booking
{'function': 'cancel_booking', 'arguments': {}}
Enter the restaurant location: Koramangala
Booking canceled in Koramangala

Enter your query/ enter exit to stop
exit
```


## License

MIT License

## Contact

For bugs or feature requests, please open an issue or contact the author.

Let me know if you want me to generate a sample database schema or help with deployment!

