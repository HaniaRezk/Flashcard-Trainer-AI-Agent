from pyneuphonic import Neuphonic, TTSConfig, save_audio, AgentConfig, WebsocketEvents
from pyneuphonic.player import AsyncAudioPlayer, AsyncAudioRecorder
from pyneuphonic.models import APIResponse, AgentResponse
import os
import asyncio

# Replace with your actual API key
api_key = "349f94878940882495d46ff2289d1891e0eae3438b5c7688de43a69356b9e8b8.b0b9a82c-870b-48d3-9768-f37f4287b67b"  
LOG_FILE = 'flashcard.log'

FLASHCARD_PROMPT = """
You are a trainer. Your task is to:
1. Ask flashcard-style questions on the topic provided.
2. Wait for user response and don't show the next question until evaluating the user\'s response.
3. Evaluate user responses (through voice input) and provide clear feedback, marking the answers as 'Correct', 'Partially Correct', or 'Incorrect'.
4. Output the correct answer if the user\'s answer is wrong.
6. If the user says "stop" end the session.
7. At the end of the session provide a score based on the user\'s responses.
8. Provide a summary of what can be done to improve performance.  
9. Tell the user that the questions and the answers are saved to a file called '{topic}.txt'.
10. When the session ends say "stop" out loud.

Topic: "{topic}"
"""


async def create_agent_speech(client, topic):
    """
    Creates a Neuphonic agent tailored for flashcard training on the specified topic.
    """
    prompt = FLASHCARD_PROMPT.format(topic=topic)
    agent = client.agents.create(
        name="Voice-Based Flashcard Trainer",
        prompt=prompt,
        greeting=f"Hi! I am your flashcard trainer for the topic: '{topic}'. I will ask you flashcard-style questions and evaluate your responses based on your input. To end the session, simply say stop. Let's start! Are you ready?",
    )
    return agent.data["id"]


async def flashcard_session_speech():
    topic = input("Enter the topic for the flashcard session: ")
    client = Neuphonic(api_key=api_key)
    log_file_path = f"{topic}.txt"  # File to save LLM texts

    try:
        # Ensure the log file is empty or new
        with open(log_file_path, "w") as file:
            file.write(f"Flashcard session for topic: {topic}\n")
            file.write("=" * 40 + "\n")

        agent_id = await create_agent_speech(client, topic)

        # Configure the agent with audio handling
        agent_config = AgentConfig(
            agent_id=agent_id,
            tts_model='neu_hq',
            sampling_rate=16000
        )

        # Initialize WebSocket, Audio Player, and Recorder
        ws = client.agents.AsyncWebsocketClient()
        player = AsyncAudioPlayer()
        recorder = AsyncAudioRecorder(sampling_rate=16000, websocket=ws, player=player)

        async def on_message(message: APIResponse[AgentResponse]):
            """
            Handle messages from the server.
            """
            if message.data.type == 'audio_response':
                await player.play(message.data.audio)
            elif message.data.type == 'user_transcript':
                print(f'User: {message.data.text}')
                with open(log_file_path, "a") as file:
                    file.write(f"User: {message.data.text}\n")
                    
            elif message.data.type == 'llm_response':
                print(f'Agent: {message.data.text}')

                #Ensures the agent stops when user says stop
                if 'stop' in message.data.text.lower():
                    await recorder.close()
                    await ws.close()
                    await player.close()
               
                # Save LLM response to file
                with open(log_file_path, "a") as file:
                    file.write(f"Agent: {message.data.text}\n")

        async def on_close():
            """
            Clean up resources on WebSocket close.
            """
            await player.close()
            await recorder.close()

        # Attach WebSocket handlers
        ws.on(WebsocketEvents.MESSAGE, on_message)
        ws.on(WebsocketEvents.CLOSE, on_close)

        # Start audio playback and recording
        await player.open()
        await ws.open(agent_config=agent_config)
        await recorder.record()

        print(f"Flashcard session started for topic: {topic}! Press Ctrl+C to stop.")

        try:
            # Keep session alive
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            # Handle interruption
            print("\nSession interrupted by user.")
            await ws.close()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        print("Session ended.")
        print(f"All responses saved to {log_file_path}.")


if __name__ == "__main__":
    #Main code
    print("""
         _______
        |       |
        |  (-)  |
        |       |
        |_______|
          |   |
          |___|
    """)

    asyncio.run(flashcard_session_speech())