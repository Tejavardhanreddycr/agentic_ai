<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" class="logo" width="120"/>

# \# TOOLS

# A restaurant application to check and book the available seats based on the loaction

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

