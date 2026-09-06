# Shell Company Screening Agent

A Deep Research Agent for identifying and evaluating listed shell company candidates as potential acquisition targets.

## Overview

The agent supports a structured shell company screening process, from candidate discovery to due diligence, transaction feasibility assessment, prioritization, and report generation.

## Research Workflow

```text
Research Planning
      ↓
Candidate Universe Construction
      ↓
Hard Screening
      ↓
Deep Due Diligence
      ↓
Transaction Feasibility and Economics
      ↓
Candidate Prioritization
      ↓
Report Generation
```

The workflow is designed to first identify a broad candidate universe, then progressively narrow and evaluate candidates based on transaction requirements and supporting evidence.

## Inputs

Task requirements are defined in `default_settings.md`, including:

* client name
* target listed market
* research cut-off date
* control requirements
* capital-structure and dilution preferences
* reporting, legal, and regulatory requirements
* market-cap requirements
* transaction objective
* additional requirements and context

## Output

The agent produces a structured Shell Company Screening Report covering:

* candidate universe and hard-screening results
* candidate comparison
* deep due diligence
* transaction feasibility
* candidate prioritization
* key risks and unresolved issues
* supporting sources

See `output_spec.md` for the report structure.

## Runtime Flow

```text
Client Settings
      ↓
Prompt Builder
      ↓
Core Prompt + Output Specification
      ↓
Deep Research Runtime
      ↓
Shell Company Screening Report
```

The runtime layer assembles the task configuration, agent prompt, and output specification before sending the research task to a Deep Research environment.

## Repository Structure

```text
.
├── README.md
├── agent_card.md
├── default_settings.md
├── prompt.md
├── output_spec.md
└── runtime/
    ├── config.yaml
    ├── prompt_builder.py
    ├── agent_runner.py
    └── output_handler.py
```

## Runtime Status

The current runtime is a prototype.

The agent specification, task configuration, research workflow, output format, and execution interface are defined. Deep Research API integration can be added once the target deployment environment is confirmed.

