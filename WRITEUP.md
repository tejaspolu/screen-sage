## Approach

I started from a real pain point: screenshots accumulate with no context. My goal was to convert each new screenshot into structured knowledge and action. I designed a pipeline with four stages: detect, analyze, organize, and document.

- Detect: a file watcher observes a user-specified folder (e.g., `~/Downloads/Screenshots`) for new screenshots.
- Analyze: a vision + LLM model produces robust JSON with title, summary, tasks, tags, and a sensitivity flag.
- Organize: the image is renamed in place using a slugified title; collisions are avoided by appending a numeric suffix. A hidden sidecar file is written to prevent double-processing.
- Document: a markdown note is created linking to the image with a checklist of tasks and metadata.

## Use of AI Tools

- Ideation: I used Cursor to brainstorm pain points and converge on a unique, personally relevant automation beyond generic email/chatbot examples.
- Coding: I leaned on AI-assisted completions for scaffolding, schema prompts, and CLI ergonomics, while editing for clarity and reliability.
- Vision: OpenAI’s `gpt-4o` model handles image understanding. The prompt strongly constrains output to JSON and includes a schema to minimize parsing failures.

## Challenges and Solutions

- Reliable JSON from LLMs: I added explicit JSON-only instructions, schema examples, and a validator. If parsing fails, the code attempts bracket extraction and minimal repair.
- File collisions and naming: I used slugified titles with timestamps and a uniqueness check to avoid overwrites.
- Latency: File handling is done on a background thread from the watcher so the handler returns quickly; the model call and I/O do not block file events.
- Portability: Defaults rely on environment variables and a YAML config; paths expand `~` and are created on demand.

## Results

The prototype runs locally on macOS, auto-triaging screenshots in real time. Each image is renamed in place with a human-meaningful slug, a sidecar prevents reprocessing, and a structured note captures the “why” and “what next,” reducing clutter and missed follow-ups.

## Next Steps

- Add project routing rules based on detected tags (e.g., send UI screenshots to a design folder).
- Integrate with task tools (e.g., append tasks to Things/Reminders/Notion via API).
- Provide a small menu bar app for toggling and status.




