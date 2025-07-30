# TOOLS
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
        # cursor.execute("SELECT * FROM restaurant_locations")
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
