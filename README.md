# Flashcard AI trainer
A voice-based flashcard AI trainer using the pyneuphonic library. The agent interacts with users by asking flashcard-style questions on the topic chosen by the user, evaluates their responses, and provides feedback. 
Key features include:
- Synthesized voice responses
- Real-time voice input recording
- Logs of interactions saved to a `{topic}.txt` file for review

Users can end the session by saying "stop," and the agent will provide a summary of their performance and tips for improvement.


## Prerequisites
- Python version: **3.10+**

Ensure that your environment meets the required version to run the Flashcard AI Trainer.

---

## Getting Started

1. **Set Up a Virtual Environment**
   Open a terminal and navigate to the project directory. Run the following commands:
   ```bash
   python -m venv FlashcardAgent
   source FlashcardAgent/bin/activate  # For Linux/macOS
   pip install -r requirements.txt


2. **Run the Agent**
    In the same environment, execute the FlashcardAgent.py script:

    ```bash
   python FlashcardAgent.py