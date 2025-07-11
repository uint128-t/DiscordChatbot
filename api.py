import aiohttp
import json
from . import config

async def completion(hist,ctx=50):
    rq = {
        "model":config.OLLAMA_AI_MODEL,
        "messages":[
            {
                "role":r, # "user" or "assistant" or "system"
                "content":c
            } for r,c in hist
        ],
        "options":{
            "temperature":config.TEMPERATURE,
            "num_ctx":ctx
        }
    }
    async with aiohttp.ClientSession() as session:
        async with session.post("http://localhost:11434/api/chat",json=rq) as resp:
            async for line in resp.content:
                gen = json.loads(line.decode())
                try:
                    print(gen["message"]["content"],end="",flush=True)
                    yield gen["message"]["content"]
                except KeyError:
                    print(gen)
    print()