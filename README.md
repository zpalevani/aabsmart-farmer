# AabSmart Farmer
![Nano Banana Generated Image November 27, 2025 - 6_34PM](https://github.com/user-attachments/assets/4055526a-d0e1-48f1-9d37-2afee66e8691)

An agricultural advisory system for small farmers in water-limited conditions. Built as a multi-agent system powered by Google Gemini.

## Overview

AabSmart Farmer is an agentic AI system that provides personalized, water-efficient farming advice. It uses a multi-agent architecture with tools, memory, and observability to help farmers optimize their crop selection and irrigation practices.

## Features

- **Multi-Agent Architecture**: Coordinated agents for profiling, water footprint analysis, agronomy advice, scenario generation, and coaching
- **Custom Tools**: Water footprint calculator and mini-RAG retrieval system
- **Memory & Sessions**: Persistent farmer profiles and conversation history
- **Clear English Responses**: Practical, actionable advice in simple English
- **Observability**: Interaction logging and system state inspection
- **Evaluation**: Golden test cases and LLM-as-judge critic

## Architecture

### Agents

1. **Profiler Agent**: Extracts farmer information (crops, land size, irrigation type, water level)
2. **Water Footprint Agent**: Calculates water usage per crop and total water footprint
3. **Agronomy RAG Agent**: Retrieves relevant agricultural tips from knowledge base
4. **Scenario Agent**: Generates conservative and water-saving crop scenarios
5. **Coach Agent**: Generates clear, practical responses using Gemini
6. **Planner Agent**: Orchestrates all agents in sequence

### Tools

- **Water Footprint Tool**: Calculates water requirements based on crop ETc values and irrigation efficiency
- **Mini-RAG Tool**: Retrieves practical irrigation tips from a local corpus

### Memory

- **MemoryBank**: Stores farmer profiles and generated scenarios
- **SessionStore**: Maintains conversation history per farmer

## Installation

### Prerequisites

- Python 3.8 or higher
- Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

### Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/zpalevani/aabsmart-farmer.git
   cd aabsmart-farmer
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set your Gemini API key as an environment variable:
   
   **Linux/Mac:**
   ```bash
   export GEMINI_API_KEY="your-api-key-here"
   ```
   
   **Windows (PowerShell):**
   ```powershell
   $env:GEMINI_API_KEY="your-api-key-here"
   ```
   
   **Windows (Command Prompt):**
   ```cmd
   set GEMINI_API_KEY=your-api-key-here
   ```
   
   **Or create a `.env` file** (make sure it's in `.gitignore`):
   ```
   GEMINI_API_KEY=your-api-key-here
   ```

4. Run the example script:
   ```bash
   python examples/demo.py
   ```
   
   Or use the Jupyter notebook:
   ```bash
   jupyter notebook AabSmart_Farmer.ipynb
   ```

## Usage

### Basic Usage

```python
from aabsmart import run_turn
from aabsmart.gemini_client import initialize_gemini

# Initialize Gemini API
initialize_gemini()

# Run a conversation turn
result = run_turn(
    farmer_id="farmer_001",
    user_message="I have 5 hectares of land and grow wheat and barley. Water is limited."
)

# Access results
print(result["answer"])  # Agricultural advice
print(result["water_footprint"])  # Water calculations
print(result["scenarios"])  # Generated scenarios
```

### Running Golden Tests

```python
from aabsmart.evaluation import run_golden

# Run predefined test cases
test_results = run_golden()
```

### Inspecting System State

```python
from aabsmart import MEMORY, SESSION, LOGS

# View profiles
for farmer_id, profile in MEMORY.profiles.items():
    print(f"{farmer_id}: {profile.main_crops}")

# View sessions
session = SESSION.get_session("farmer_001")

# View logs
for log in LOGS:
    print(log)
```

## Project Structure

```
.
├── aabsmart/
│   ├── __init__.py           # Package initialization
│   ├── data_structures.py    # FarmerProfile, Scenario, ETc tables
│   ├── memory.py             # MemoryBank, SessionStore
│   ├── tools.py              # Water footprint, Mini-RAG
│   ├── gemini_client.py      # Gemini API integration
│   ├── agents.py             # All agent implementations
│   ├── runner.py             # Main orchestrator
│   ├── observability.py      # Logging and monitoring
│   └── evaluation.py         # Golden tests and critic
├── examples/
│   └── demo.py               # Standalone demo script
├── AabSmart_Farmer.ipynb     # Jupyter notebook
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Key Components

### Data Structures

- `FarmerProfile`: Stores farmer information (crops, land size, irrigation type, etc.)
- `Scenario`: Represents a crop mix scenario with water footprint calculations
- `ETC_TABLES`: Crop evapotranspiration values for common crops
- `IRRIGATION_EFFICIENCY`: Efficiency factors for different irrigation types

### Memory Layer

- `MemoryBank`: Singleton storing profiles and scenarios
- `SessionStore`: Singleton storing conversation history

### Tools

- `calculate_water_footprint()`: Computes water requirements
- `retrieve_agronomy_tips()`: Retrieves relevant tips from knowledge base

## Course Concepts Demonstrated

1. **Multi-Agent System**: Multiple specialized agents working together
2. **Tools**: Custom tools for water calculations and RAG retrieval
3. **Sessions & Memory**: Persistent storage of profiles and conversations
4. **Observability**: Logging and system state inspection
5. **Evaluation**: Golden test cases and LLM-as-judge critic

## API Key Setup

### Get Your API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key or use an existing one
3. Set it as an environment variable (see Installation section above)

### Note for Kaggle Users

If you're running this in Kaggle, the system will automatically try to load the API key from Kaggle Secrets as a fallback. However, environment variables are the primary method.

## Example Output

The system generates clear, practical advice:

```
Based on your profile, we recommend reducing rice cultivation area by 50% and switching to drip irrigation. This could save approximately 30% of your total water usage while maintaining crop diversity.

Here are some practical steps:
1. Consider replacing 50% of your rice area with lower-water crops like wheat or barley
2. Invest in a drip irrigation system - it can reduce water waste by up to 40%
3. Monitor soil moisture before irrigation to avoid over-watering
...
```

## Contributing

This is a capstone project. For improvements:

1. Expand crop ETc tables for more regions
2. Enhance agronomy tips corpus
3. Add more sophisticated scenario generation
4. Implement feedback mechanisms

## License

This project is for educational purposes as part of a capstone course.

## Acknowledgments

- Google Gemini API for LLM capabilities
- Agricultural research for ETc values and irrigation efficiency data

