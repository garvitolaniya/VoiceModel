# VoiceModel

A comprehensive voice recording and model training system for collecting and processing voice data.

## 👥 Authors

- **Garvit** - [Garvit Olaniya](https://github.com/garvitolaniya)
- **Keshav** - [Keshav Khandelwal ](https://github.com/KeshavX3)

## 📋 Project Overview

VoiceModel is a Python-based application designed to facilitate the collection of voice recordings for training voice recognition models. The project includes tools for recording voice samples, organizing data, and preparing it for model training.

## 🖼️ Screenshots

### Welcome Page
![Welcome Page](https://github.com/garvitolaniya/VoiceModel/blob/65b06d73ca9290849227a87411317311d967602f/Screenshot/Screenshot%202025-05-06%20144109.png)

### Main Recording Page
![Main Page](https://github.com/garvitolaniya/VoiceModel/blob/75e24b06b8fc88f4245d284e99fdd552a5a067cf/Screenshot/Screenshot%202025-05-06%20144118.png)

## 🗂️ Project Structure

```
VoiceModel/
├── data/                  # Directory for storing voice recordings
│   └── recordings/        # Individual voice recordings
├── scripts/               # Python scripts
│   └── record.py         # Main recording script
├── word_sources/         # Source word lists
│   ├── numbers.txt       # Number words
│   └── small_words.txt   # Common words
└── wordlist.txt          # Main word list for recording
```

## 🚀 Features

- Voice recording interface with configurable duration
- Support for multiple word lists and categories
- Organized storage of voice recordings
- Easy-to-use command-line interface
- Configurable recording parameters (sample rate, duration)

## 🛠️ Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/VoiceModel.git
cd VoiceModel
```

2. Install required dependencies:
```bash
pip install sounddevice numpy wave
pip install flask==3.0.0 numpy==1.24.3 sounddevice==0.4.6 scipy==1.10.1 python-dotenv==1.0.0

```

## 💻 Usage

1. Prepare your word list in `wordlist.txt` or use the provided word sources
2. Run the recording script:
```bash
python app.py
```
3. Follow the prompts to record voice samples for each word

## 📝 Word Sources

The project includes several word source files:
- `word_sources/numbers.txt`: Numbers 1-5 (Can be edited)
- `word_sources/small_words.txt`: Common words and phrases (Can be edited) 

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- SoundDevice library for audio recording capabilities
- Whisper model for voice recognition inspiration
