from groq import Groq
var_api_key = "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"
client = Groq(api_key=var_api_key)

stream = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": (
                "Escreva uma carta de recomendação para o Sr. João Silva, "
                "destinada à Universidade XYZ, destacando suas habilidades "
                "em liderança, trabalho em equipe e excelência acadêmica."
            ),
        }
    ],
    model="llama-3.3-70b-versatile",
    temperature=0.5,
    max_completion_tokens=1024,
    top_p=1,
    stop=None,
    stream=True,
)

for chunk in stream:
    print(chunk.choices[0].delta.content, end="")
