from . import config,api

class ChatHistory:
    def __init__(self):
        self.messages = []
    def autoremove(self):
        # Keep only the last MAX_MESSAGE_COUNT messages
        while len(self.messages)>config.MAX_MESSAGE_COUNT:
            self.messages.pop(0)
    def user_message(self,name,content):
        # Add a user message to the chat history
        self.messages.append(("user",f"{name}: {content}"))
        self.autoremove()
    async def assistant_message(self,ctx=2048,sys=True):
        # Generate a response
        msg = ""
        async for part in api.completion([("system",config.SYSTEM_PROMPT)]*sys+self.messages,ctx):
            msg+=part
        self.messages.append(("assistant",msg))
        self.autoremove()
        return msg