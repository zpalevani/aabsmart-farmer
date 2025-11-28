# Quick Start Guide

## Setup (5 minutes)

1. **Clone the repository**:
   ```bash
   git clone https://github.com/zpalevani/aabsmart-farmer.git
   cd aabsmart-farmer
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set your API key**:
   ```bash
   export GEMINI_API_KEY="your-api-key"
   ```
   
   Or create a `.env` file:
   ```bash
   cp .env.example .env
   # Edit .env and add your API key
   ```

4. **Run the demo**:
   ```bash
   python examples/demo.py
   ```

## Usage

```python
from aabsmart import run_turn
from aabsmart.gemini_client import initialize_gemini

initialize_gemini()
result = run_turn("farmer_001", "سلام. من گندم می‌کارم.")
```

## Key Functions

- `run_turn(farmer_id, user_message)`: Main entry point
- `run_golden()`: Run evaluation tests
- `MEMORY.profiles`: Access stored profiles
- `SESSION.get_session(farmer_id)`: Get conversation history
- `LOGS`: View interaction logs

## Architecture Flow

1. User message → `run_turn()`
2. `run_turn()` → `planner_agent()`
3. `planner_agent()` orchestrates:
   - Profiler Agent (extract info)
   - Water Footprint Agent (calculate water)
   - Agronomy RAG Agent (retrieve tips)
   - Scenario Agent (generate scenarios)
   - Coach Agent (generate bilingual response)
4. Response returned with all metadata

## Testing

Run golden test cases:
```python
from aabsmart.evaluation import run_golden
test_results = run_golden()
```
