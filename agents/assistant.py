from llama_cpp_agent.messages_formatter import MessagesFormatterType
from app.config import config
from app.messages import MessageHandler
from agents.memgpt import MemGptAgent

provider = config.chat_provider
chat_template = MessageHandler.get_messages_formatter_type(config.chat_llm_type)

mem_gpt_agent = MemGptAgent(provider, debug_output=True, core_memory_file="../data/core_memory.json",
                            event_queue_file="../data/event_queue.json",
                            messages_formatter_type=chat_template
                            )

while True:
    user_input = input(">")

    mem_gpt_agent.get_response(user_input)
    mem_gpt_agent.save()