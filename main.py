import os

from dotenv import load_dotenv
from sarvamai import SarvamAI

load_dotenv()


def main():
    client = SarvamAI(api_subscription_key=os.environ["SARVAM_API_KEY"])

    response = client.chat.completions(
        model="sarvam-30b",
        messages=[{"role": "user", "content": "What is the capital of India?"}],
    )

    print(response.choices[0].message.content)


if __name__ == "__main__":
    main()
