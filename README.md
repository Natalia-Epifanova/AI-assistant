# AI Assistant Test Task

This repository contains a small MVP for the blogger search test task.

## Project structure

- `data/input/` stores original input files from the employer.
- `data/demo/` stores a local demo dataset for safe MVP development without paid APIs.
- `src/` stores the pipeline code.
- `prompts/` stores prompt templates for analysis and offer generation.
- `docs/` stores supporting notes and diagrams.
- `outputs/` stores generated results.

## Текущее состояние

Сейчас проект уже умеет:

- читать исходную таблицу блогеров;
- нормализовать ссылки и usernames;
- сохранять очищенные данные;
- собирать базовые признаки по базе;
- строить простой агрегированный профиль;
- подбирать похожих кандидатов из демо-датасета;
- генерировать персональные черновики офферов;
- выполнять первый живой поиск по YouTube API, если ключ добавлен в `.env`.

## Как запустить

```powershell
& 'C:\Users\user\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' .\main.py
```

## Настройка YouTube API

1. Создай файл `.env` в корне проекта.
2. Добавь в него строку:

```env
YOUTUBE_API_KEY=your_real_key_here
```

Ключ уже игнорируется через `.gitignore`, поэтому в git он не попадет.
Для примера в проект добавлен `.env.example`.
Переменные загружаются через стандартный `load_dotenv()`.

## Как проверить результат

После запуска должны появиться файлы:

- `outputs/source_bloggers_cleaned.json`
- `outputs/source_bloggers_needs_review.json`
- `outputs/source_bloggers_features.json`
- `outputs/ideal_blogger_profile.json`
- `outputs/top_candidate_matches.json`
- `outputs/outreach_offers.json`
- `outputs/youtube_search_results.json` если ключ YouTube найден и запрос выполнился

Проверять содержимое лучше через Python:

```powershell
& 'C:\Users\user\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -c "from pathlib import Path; print(Path('outputs/youtube_search_results.json').read_text(encoding='utf-8'))"
```
