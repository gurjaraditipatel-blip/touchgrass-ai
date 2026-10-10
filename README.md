# 🌱 TouchGrass AI

**AI that gets you away from AI.**

TouchGrass AI is a local-first outdoor adventure generator powered by Python, Streamlit, Ollama, and the Qwen2.5:3b open-weight language model.

## Why I Built This

Many AI applications encourage people to spend more time on screens. TouchGrass AI uses AI for the opposite purpose: generate an outdoor adventure, complete real-world missions, and return to track your progress.

## Features

- Personalized outdoor adventure generation
- Four AI-generated missions and a final challenge
- Mission completion checkboxes
- TouchGrass score out of 100
- Go Outside Mode
- Local text generation through Ollama
- Optional future support for local vision AI

## Tech Stack

- Python
- Streamlit
- Ollama
- Qwen2.5:3b

## Requirements

- A compatible Windows, macOS, or Linux computer
- Python
- Ollama
- The `qwen2.5:3b` model
- Enough available memory and disk space

## Installation

1. Install Python and Ollama.
2. Download the model:

   `ollama pull qwen2.5:3b`

3. Clone this repository:

   `git clone YOUR_REPOSITORY_URL`

4. Open the project folder:

   `cd touchgrass-ai`

5. Create a virtual environment:

   `python -m venv .venv`

6. Activate it on Windows:

   `.venv\Scripts\activate.bat`

7. Install dependencies:

   `python -m pip install -r requirements.txt`

8. Start the app:

   `python -m streamlit run app.py`

9. Open the local URL shown in the terminal.

## How It Works

Users choose their available time, environment, difficulty, and interests. Python sends these preferences to the locally running Ollama model. The generated adventure appears in the Streamlit interface, where users can track missions and their score.

## Local AI and Open Innovation

The project uses local inference instead of requiring a hosted AI API for adventure generation. Its code can be inspected and extended by the community. After installation and model download, the core generation flow may work offline; this should be verified on the target computer.

## Screenshots

![TouchGrass AI app](screenshots/home.png)

## Limitations

- Mission completion is self-reported.
- AI-generated missions require human judgement.
- Plant and animal identification is not included in the current version.
- Performance depends on available system memory and CPU.

## Future Improvements

- Optional local vision AI
- More languages and accessibility improvements
- Mission history and progress tracking
- More personalized outdoor activities

## License

See the `LICENSE` file.
