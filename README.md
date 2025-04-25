# SupportForChat

**SupportForChat** is a lightweight tool that helps teams quickly summarize and analyze customer support tickets using AI.
It’s built with Streamlit for the interface and OpenAI models for generating the ticket summaries.

The goal is simple: make it easier for support teams and businesses to spot problems, trends, and customer pain points without digging through thousands of lines of feedback manually.

---

## How it Works

- Reads support ticket data from a CSV file
- Uses OpenAI to create short, clear summaries
- Displays everything in an easy-to-use web app (Streamlit)
- Outputs summaries into a `.txt` file for saving or further review

---

## Getting Started

### 1. Clone the project
```bash
git clone https://github.com/ItsRezaOk/SupportForChat.git
cd SupportForChat
```

### 2. (Optional) Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install the required Python packages
```bash
pip install -r requirements.txt
```

### 4. Set your OpenAI API key
You'll need an OpenAI API key to run the app. Set it in your terminal like this:
```bash
export OPENAI_API_KEY=your_api_key_here   # (Windows: set OPENAI_API_KEY=your_api_key_here)
```

---

## Running the App

Once everything’s installed, just run:
```bash
streamlit run main.py
```
It'll open up a web browser where you can upload support tickets, generate summaries, and download the results.

If you don't have support ticket data, you can generate a dummy dataset for testing:
```bash
python generate_data.py
```

---

## Project Layout

```
SupportForChat/
├── .gitignore
├── generate_data.py        # Script to generate sample tickets
├── main.py                 # Streamlit app
├── support_tickets.csv     # Example support ticket data
├── summaries.txt           # Output file with summaries
```

---

## Why I Built This

Handling customer feedback manually is time-consuming.
This tool was made to speed up that process by using AI — so businesses can focus more on solving issues and less on reading endless tickets.

---

## License

MIT License – free to use, change, or build on.

---

## Future Ideas

- Add support for multiple AI models
- Visualize ticket trends (common topics, keywords)
- Automatic tagging and categorization
- Real-time integration with support platforms

---

If you have suggestions or run into any problems, feel free to open an issue!

