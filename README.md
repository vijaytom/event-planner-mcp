🇮🇳 Event Planner AI (MCP Server)
Think of our Event Planner AI as your personal, smart assistant for planning all kinds of social events in India! Whether it's a grand wedding, a fun birthday bash, or a vibrant festival celebration, this AI helps you organize everything from start to finish. It's designed to make your event planning easier and stress-free.
✨ What it Does for You
Easy Conversation: Just chat with it like you would with a friend! It asks you simple questions to understand what you need for your event.
Smart Understanding: It intelligently picks up on key details about your event, like the type of celebration, where it will be, how many guests you expect, and your budget – even if you just say "50k" or "1 lakh"!
Custom Event Plans: Once it has all the details, it creates a personalized plan just for you, including a checklist of everything you'll need.
Finds the Best Vendors: Looking for a photographer or caterer? It can search and recommend local vendors based on your event's needs and budget, helping you find the right people for the job.
Secure & Private: Your event details are handled safely and securely.
🚀 Technologies Used
Python 3.11+
FastMCP: A high-level Python framework for building MCP servers.
Pydantic: For data validation and settings management.
python-dotenv: To manage environment variables securely.
SerpAPI: For real-time search capabilities to find vendors.


4. Create JSON Data Files
Create the following JSON files in your project's root directory:
indian_events.json
{
  "events": [
    {
      "name": "Wedding",
      "keywords": ["wedding", "marriage", "shaadi", "vivah"]
    },
    {
      "name": "Birthday Party",
      "keywords": ["birthday", "b'day", "janmadin"]
    },
    {
      "name": "Anniversary Party",
      "keywords": ["anniversary", "saalgirah"]
    },
    ....
  ]
}


indian_locations.json
{
  "locations": [
    {
      "name": "Tiruchirappalli, Tamil Nadu",
      "keywords": ["tiruchirappalli", "trichy", "trichirapalli"]
    },
    {
      "name": "Chennai, Tamil Nadu",
      "keywords": ["chennai", "madras"]
    },
    {
      "name": "Delhi, NCR",
      "keywords": ["delhi", "ncr", "new delhi", "delhi ncr"]
    },
    ....
  ]
}


5. Install Dependencies
Open your terminal or command prompt, navigate to your project directory, and run the following command to install the required Python packages:
pip install fastmcp pydantic python-dotenv serpapi google-search-results


6. Run the Server
Save the main Python code (provided in previous turns) as server.py (or any other .py file name you prefer). Then, run the server using:
python server.py


The server will start and listen for requests, typically on http://0.0.0.0:8086.
🤝 How People Can Use It
This AI is designed to work with a special kind of AI app (an MCP client). When you chat with that app, it will connect to this Event Planner AI server in the background to help you plan your event.
Here's how it generally works:
Start a chat: You'll begin by telling the AI app you want to plan an event.
AI asks questions: The AI will then ask you step-by-step questions about your event, like "What kind of event are you planning?" or "How many guests?".
You provide details: You simply respond naturally, and the AI understands your answers, even if you use common Indian terms for money or places.
Get your plan: Once all the necessary information is gathered, the AI will give you a personalized event plan and a checklist of things you'll need.
Find help: You can even ask the AI to "find wedding photographers in Chennai for a moderate budget," and it will look up recommendations for you!
📜 License
This project is licensed under the Apache License, Version 2.0. This means you are free to use, change, and share this code, even for commercial purposes, as long as you follow the terms of the Apache 2.0 License. A copy of the license is included in this repository.
💡 Contributing
We welcome your ideas and help! If you have suggestions for how to make this Event Planner AI even better, find any issues, or want to add new features, please contribute by opening an issue or submitting a pull request on GitHub.
