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

## Как запустить

```powershell
& 'C:\Users\user\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' .\main.py
```

## Как проверить результат

После запуска должны появиться файлы:

- `outputs/source_bloggers_cleaned.json`
- `outputs/source_bloggers_needs_review.json`
- `outputs/source_bloggers_features.json`
- `outputs/ideal_blogger_profile.json`
- `outputs/top_candidate_matches.json`

Проверить их содержимое лучше через Python, чтобы не столкнуться с проблемой кодировки в PowerShell:

```powershell
& 'C:\Users\user\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -c "from pathlib import Path; print(Path('outputs/source_bloggers_needs_review.json').read_text(encoding='utf-8'))"
```

Если все в порядке, ты увидишь проблемную строку в нормальном виде:

`МИША И КЕЙТ (@mishandkatya) • Instagram photos and videos`

## Что есть сейчас

На текущем этапе MVP уже умеет:

- читать исходную таблицу;
- нормализовать ссылки и usernames;
- сохранять очищенные данные;
- собирать базовые признаки по usernames для первого черновика портрета базы;
- сохранять простой агрегированный профиль базы блогеров;
- подбирать топ кандидатов из тестового датасета по простому скорингу.
