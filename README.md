# AI Assistant Test Task

This repository contains a small MVP for the blogger search test task.

## Project structure

- `data/input/` stores original input files from the employer.
- `data/demo/` stores a local demo dataset for safe MVP development without paid APIs.
- `src/` stores the pipeline code.
- `prompts/` stores prompt templates for analysis and offer generation.
- `docs/` stores supporting notes and diagrams.
- `outputs/` stores generated results.

## Current status

The project skeleton is prepared, and the first input loader is wired.

## What the loader does

- reads the first sheet from `data/input/bloggers.xlsx`;
- extracts Instagram links from raw spreadsheet values;
- derives usernames from URLs or `@handle` mentions;
- marks problematic rows as `needs_review`.
