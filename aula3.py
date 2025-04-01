from groq import Groq
var_api_key = "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"
client = Groq(api_key=var_api_key)

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": "Você é uma especialista em saude animal ajude o usuario a tratar bem do seu pets."
        },
        {
            "role": "user",
            "content": "O que posso dá para o meu cachorro doente?",
        }
    ],
    model="deepseek-r1-distill-qwen-32b",
    temperature=0.5,
    max_completion_tokens=1024,
    top_p=1,
    stop=None,
    stream=False,
)

print(chat_completion.choices[0].message.content)
