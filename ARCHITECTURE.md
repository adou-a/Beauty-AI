# Beauty-AI Architecture

## 1. Project Overview

Beauty-AI is a cosmetic domain AI Agent system.

The goal is to provide intelligent cosmetic ingredient analysis and skincare assistance through:

- LLM reasoning
- Agent workflow
- Tool execution
- RAG knowledge retrieval
- Validation mechanism

The system is designed as an Agent application rather than a simple chatbot.


---

# 2. Overall System Architecture


User Input

↓

API Layer

↓

Planning Gate

↓

Decision:

SIMPLE
or
COMPLEX


## SIMPLE Flow

Planning Gate

↓

BeautyAgent

↓

Tool / RAG

↓

Final Answer


## COMPLEX Flow

Planning Gate

↓

WorkflowRunner

↓

Planner

↓

Plan

↓

PlanExecutor

↓

AgentStepExecutor

↓

BeautyAgent

↓

Tool Execution

↓

RAG Retrieval

↓

Step Results

↓

FinalAnswer

↓

Validator

↓

WorkflowResult


---

# 3. Core Module Responsibilities


## API Layer

Responsibility:

- Receive user requests
- Provide external interfaces


Does NOT:

- execute Agent logic
- manage workflow


---

# Planning Gate

Responsibility:

- Decide whether a task needs workflow execution


Input:

- user_input


Output:

- SIMPLE
- COMPLEX


Does NOT:

- execute tasks
- generate answers


---

# Planner

Responsibility:

- Decompose complex user goals
- Generate execution plan


Input:

- user goal


Output:

- Plan


Responsible for:

- task decomposition
- step description


Does NOT:

- execute tools
- call RAG
- generate final answers
- manage execution status


---

# Plan

Domain model representing an execution plan.


Contains:

- goal
- steps


---

# PlanStep

Represents one executable task.


Contains:

- id
- description
- status
- result


Lifecycle:

PENDING

↓

RUNNING

↓

COMPLETED / FAILED


---

# WorkflowRunner

Responsibility:

Workflow orchestration entry point.


Responsible for:

- calling Planner
- creating workflow execution
- connecting Planner and Executor
- returning workflow result


Does NOT:

- execute tools
- select tools
- modify step logic


---

# PlanExecutor

Responsibility:

Execute PlanSteps.


Responsible for:

- step execution order
- updating execution progress
- collecting results


Does NOT:

- create plans
- reason about user goals


---

# AgentStepExecutor

Responsibility:

Execute one specific PlanStep.


Responsible for:

- connecting Workflow execution and Agent
- passing context
- calling BeautyAgent


Does NOT:

- decide overall plan
- select workflow strategy


---

# BeautyAgent

Responsibility:

Agent reasoning layer.


Responsible for:

- understanding current task
- selecting tools
- generating responses


Flow:

Think

↓

Act

↓

Observe


---

# Tool Layer

Responsibility:

Execute external capabilities.


Examples:

- ingredient search
- risk checking
- knowledge retrieval


Tools return information.

They do NOT generate final answers.


---

# RAG System


Flow:

Knowledge Documents

↓

Loader

↓

Chunker

↓

Embedding

↓

Vector Store

↓

Retriever

↓

RAG Tool


Responsibility:

Provide domain knowledge.


Does NOT:

- decide user goals
- generate final response


---

# Final Answer


Responsibility:

Synthesize execution results into user-facing response.


Input:

- user_input
- execution results


Output:

- final answer


---

# Validator


Responsibility:

Judge whether final answer satisfies user's goal.


Input:

- user_input
- goal
- final_answer


Output:

ValidationResult


Rules:

success=True

requires:

reasons=[]


Validator checks:

- goal completion


Validator does NOT check:

- factual correctness


---

# Workflow State Management


WorkflowState represents workflow execution state.


Contains:

- workflow status
- current step
- error information


Status:

PENDING

↓

RUNNING

↓

COMPLETED / FAILED


Principle:

Avoid duplicate sources of truth.

PlanStep stores step execution status.

WorkflowState stores workflow-level status.


---

# 4. Important Design Decisions


## Planning and Execution Separation

Planner creates plans.

Executor executes plans.


Reason:

Avoid mixing decision and execution responsibilities.


---

## Agent Does Not Replace Workflow

Simple tasks can directly use Agent.

Complex tasks require Workflow.


---

## Domain Model Separation

LLM output schema and internal domain model are separated.


Reason:

LLM output is external data.

Domain model controls system behavior.


---

## Error Propagation

System errors should propagate upward.

Examples:

- LLM failure
- Tool failure
- Execution failure


Business judgment failures should be represented normally.


Example:

Validator:

success=False


is not a system error.


---

# 5. Current Development Phase


Current Phase:

Phase 6 — Agent Workflow & Planning


Completed:

- Planner
- Plan
- PlanStep
- PlanExecutor
- AgentStepExecutor
- WorkflowRunner
- WorkflowState
- FinalAnswer
- Validator


Next Phase:

Phase 7 — Persistent State & Memory


Focus:

- user profile
- session memory improvement
- persistent workflow context