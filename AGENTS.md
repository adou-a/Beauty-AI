# Beauty-AI Agent Instructions

## Project Goal

Beauty-AI is a cosmetic domain AI Agent.

The system should help users analyze:
- cosmetic ingredients
- ingredient effects
- skin suitability
- product-related questions


## Tech Stack

- Python 3.13
- FastAPI
- Pydantic
- pytest
- LLM
- RAG


## Architecture Rules

### Planner

Responsible for:
- understanding user goals
- generating execution plans

Must NOT:
- execute tools
- call RAG
- generate final answers


### PlanExecutor

Responsible for:
- executing PlanStep sequentially
- managing execution flow


### AgentStepExecutor

Responsible for:
- executing one PlanStep
- connecting Workflow and Agent


### BeautyAgent

Responsible for:
- reasoning
- selecting tools
- generating responses


### WorkflowRunner

Responsible for:
- workflow orchestration
- connecting Planner and Executor

Must NOT:
- execute tools directly
- modify PlanStep logic


## Coding Rules

- Use type hints
- Keep domain models strict
- Add tests for new features
- Preserve existing architecture
- Prefer explicit error propagation


## Do Not

Do not:
- merge modules with different responsibilities
- rewrite architecture without discussion
- remove tests to make code pass
- change data flow without explanation


## Testing

Before finishing changes:

Run:

pytest

Ensure:
- existing tests pass
- new behavior has coverage

## Environment

Python version:
3.13.9

Virtual environment:

.venv

Setup:

Create environment:

python -m venv .venv


Install dependencies:

pip install -r requirements.txt


Run tests:

pytest