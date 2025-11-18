# Holographic Chatbot

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**Interactive 3D AI Chatbot with Real-Time Holographic LED Fan Integration**

Transform conversational AI into a stunning holographic experience! This production-ready application combines OpenAI's ChatGPT with 3D animations, text-to-speech synthesis, and holographic LED fan display technology to create an immersive, futuristic chatbot interface.

![Demo](./assets/video.gif)

## 🌟 Features

- **🤖 AI-Powered Conversations**: Leverages OpenAI's ChatGPT for intelligent, context-aware responses
- **🎨 3D Rendering**: Real-time 3D text animations using matplotlib
- **🔊 Text-to-Speech**: Natural voice synthesis with Google TTS
- **👄 Lip Synchronization**: Phoneme-based lip sync for realistic mouth movements
- **📡 Holographic Display**: Stream animations to Missyou/GIWOX LED holographic fans
- **🎬 Frame Processing**: Advanced image optimization for LED fan compatibility
- **⚙️ Fully Configurable**: Environment-based configuration with pydantic
- **🧪 Production-Ready**: Type hints, comprehensive error handling, and logging
- **📊 Interactive Mode**: Real-time chat interface with statistics

## 📋 Table of Contents

- [Features](#-features)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Architecture](#-architecture)
- [Development](#-development)
- [Testing](#-testing)
- [Contributing](#-contributing)
- [License](#-license)
- [Author](#-author)

## 🔧 Prerequisites

### System Requirements

- **Python**: 3.9 or higher
- **Operating System**: Linux, macOS, or Windows
- **Hardware**: Holographic LED Fan (Missyou or GIWOX) - optional for testing

### System Dependencies

Install the following system packages:

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y ffmpeg espeak-ng mpg123

# macOS (with Homebrew)
brew install ffmpeg espeak-ng mpg123

# Windows
# Download and install ffmpeg, espeak-ng manually
```

### API Keys

- **OpenAI API Key**: Sign up at [OpenAI](https://platform.openai.com/) and generate an API key

## 📦 Installation

### Option 1: Using `uv` (Recommended)

[uv](https://github.com/astral-sh/uv) is a fast Python package manager by Astral.

```bash
# Install uv
pip install uv

# Clone the repository
git clone https://github.com/ruslanmv/3D-AI-Chatbot-with-Real-Time-LED-Holographic.git
cd 3D-AI-Chatbot-with-Real-Time-LED-Holographic

# Install dependencies
make install

# Or for development with all extras
make install-dev
```

### Option 2: Using pip

```bash
# Clone the repository
git clone https://github.com/ruslanmv/3D-AI-Chatbot-with-Real-Time-LED-Holographic.git
cd 3D-AI-Chatbot-with-Real-Time-LED-Holographic

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install the package
pip install -e .

# Or for development
pip install -e ".[dev,docs]"
```

### Complete Setup

For complete setup including system dependencies:

```bash
make setup
```

## 🚀 Quick Start

### 1. Configure Environment

Copy the example environment file and edit with your settings:

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:

```env
OPENAI_API_KEY=sk-your-api-key-here
FAN_API_URL=http://192.168.1.100  # Your fan's IP address
```

### 2. Run the Application

#### Interactive Mode (Default)

```bash
# Using the installed command
holographic-chatbot

# Or using make
make run

# Or using Python module
python -m holographic_chatbot.main
```

#### Test System Components

```bash
holographic-chatbot --test
```

### 3. Example Session

```
🌟 Holographic Chatbot - Interactive Mode 🌟

Welcome! Type your messages below (or 'quit' to exit)
Commands:
  - 'quit' or 'exit': Exit the application
  - 'clear': Clear conversation history
  - 'stats': Show statistics

🎤 You: Hello, how are you?

🤖 Bot: Hello! I'm doing great, thank you for asking! I'm excited
to help you explore the fascinating world of holographic AI.
How can I assist you today?
```

## ⚙️ Configuration

All configuration is managed through environment variables (`.env` file) or command-line settings.

### Key Configuration Options

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key (required) | - |
| `OPENAI_MODEL` | GPT model to use | `gpt-4` |
| `FAN_API_URL` | Holographic fan API base URL | `http://192.168.1.100` |
| `FAN_FRAME_RATE` | Animation frame rate (fps) | `30` |
| `FAN_RESOLUTION_WIDTH` | Frame width in pixels | `256` |
| `FAN_RESOLUTION_HEIGHT` | Frame height in pixels | `256` |
| `LOG_LEVEL` | Logging verbosity | `INFO` |
| `ENABLE_AUDIO` | Enable text-to-speech | `true` |
| `ENABLE_LIP_SYNC` | Enable lip synchronization | `true` |
| `ENABLE_FAN_STREAMING` | Enable fan streaming | `true` |

See [.env.example](.env.example) for complete configuration options.

## 📖 Usage

### Python API

```python
from holographic_chatbot.main import HolographicChatbot

# Initialize the chatbot
bot = HolographicChatbot()

# Process a single input
response = bot.process_user_input("What's the weather like?")
print(response)

# Run interactive mode
bot.interactive_mode()

# Clean up resources
bot.cleanup()
```

### Component Usage

#### ChatGPT Integration

```python
from holographic_chatbot.chatbot import ChatGPTClient
from holographic_chatbot.config import get_settings

settings = get_settings()
client = ChatGPTClient(settings)

response = client.get_response("Tell me a joke")
print(response)
```

#### 3D Rendering

```python
from holographic_chatbot.animation import Renderer3D
from holographic_chatbot.config import get_settings

settings = get_settings()
renderer = Renderer3D(settings)

frame = renderer.generate_frame("Hello World", angle=45)
renderer.save_frame(frame, Path("output.png"))
```

#### Speech Synthesis

```python
from holographic_chatbot.audio import SpeechSynthesizer
from holographic_chatbot.config import get_settings

settings = get_settings()
synthesizer = SpeechSynthesizer(settings)

audio_path = synthesizer.synthesize("Hello, welcome!")
print(f"Audio saved to: {audio_path}")
```

For detailed examples, see [docs/TUTORIAL.md](docs/TUTORIAL.md).

## 🏗️ Architecture

```
holographic-chatbot/
├── src/holographic_chatbot/
│   ├── __init__.py           # Package initialization
│   ├── config.py             # Configuration management
│   ├── main.py               # Application entry point
│   ├── chatbot/              # ChatGPT integration
│   │   ├── __init__.py
│   │   └── gpt_integration.py
│   ├── animation/            # 3D rendering & models
│   │   ├── __init__.py
│   │   ├── renderer.py
│   │   └── model_loader.py
│   ├── fan/                  # Holographic fan integration
│   │   ├── __init__.py
│   │   ├── api_client.py
│   │   └── frame_converter.py
│   ├── audio/                # Speech synthesis & phonemes
│   │   ├── __init__.py
│   │   ├── speech_synthesis.py
│   │   └── phoneme_analyzer.py
│   └── utils/                # Utilities
│       ├── __init__.py
│       └── logger.py
├── tests/                    # Unit tests
├── docs/                     # Documentation
├── examples/                 # Example scripts
├── models/                   # 3D model files (glTF/GLB)
├── assets/                   # Media assets
├── pyproject.toml            # Project metadata & dependencies
├── Makefile                  # Build automation
└── README.md                 # This file
```

### Data Flow

```
User Input → ChatGPT → Response Text
                ↓
        ┌───────┴────────┐
        ↓                ↓
    TTS Audio      3D Animation
        ↓                ↓
    Phonemes      Frame Rendering
        ↓                ↓
    Lip Sync ←───→ Frame Processing
                     ↓
              Holographic Fan
```

## 🛠️ Development

### Setup Development Environment

```bash
make install-dev
```

### Code Quality Tools

```bash
# Format code
make format

# Run linters
make lint

# Type checking
make type-check

# Run all quality checks
make quality
```

### Project Commands

```bash
# Show all available commands
make help

# Run tests
make test

# Run tests with coverage
make test-cov

# Build distribution
make build

# Clean build artifacts
make clean
```

## 🧪 Testing

```bash
# Run all tests
make test

# Run with coverage report
make test-cov

# Run specific test file
pytest tests/test_config.py -v

# Run with specific marker
pytest -m "not slow" -v
```

Coverage reports are generated in `htmlcov/index.html`.

## 📝 License

This project is licensed under the **Apache License 2.0** - see the [LICENSE](LICENSE) file for details.

```
Copyright 2025 Ruslan Magana

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0
```

## 👤 Author

**Ruslan Magana**

- Website: [ruslanmv.com](https://ruslanmv.com)
- GitHub: [@ruslanmv](https://github.com/ruslanmv)

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please ensure:
- Code follows PEP 8 style guidelines
- All tests pass (`make test`)
- Type hints are included
- Documentation is updated

## 🙏 Acknowledgments

- **OpenAI** for ChatGPT API
- **Missyou & GIWOX** for holographic LED fan technology
- **3D holographic fan-Cindy** for inspiration and demo content
- The open-source community for amazing tools and libraries

## 📚 Resources

- [Step-by-Step Tutorial](docs/TUTORIAL.md) - Comprehensive tutorial
- [API Documentation](docs/API.md) - Detailed API reference (coming soon)
- [OpenAI API Docs](https://platform.openai.com/docs)
- [Holographic Fan Setup Guide](docs/FAN_SETUP.md) (coming soon)

## 📊 Project Status

**Version**: 1.0.0
**Status**: Production Ready ✅

---

**Made with ❤️ by [Ruslan Magana](https://ruslanmv.com)**
