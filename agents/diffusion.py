import datetime
from enum import Enum

from diffusers import StableDiffusionXLPipeline
import torch
import datetime

from llama_cpp_agent import LlamaCppAgent
from llama_cpp_agent.function_calling import LlamaCppFunctionTool

from llama_cpp_agent.llm_output_settings import LlmStructuredOutputSettings
from llama_cpp_agent.providers import LlamaCppServerProvider, LlamaCppSamplingSettings


#pipeline = DiffusionPipeline.from_pretrained("rubbrband/epicrealismXL_v5Ultimate", torch_dtype=torch.bfloat16).to(
#    'cuda')

pipeline = StableDiffusionXLPipeline.from_pretrained('dataautogpt3/OpenDalleV1.1', torch_dtype=torch.bfloat16).to('cuda')


class ImageSize(Enum):
    small = "512"
    medium = "768"
    large = "1024"


def generate_image(prompt: str, negative_prompt: str, width: ImageSize, height: ImageSize):
    """
    Generate an image given a prompt and a negative prompt and the width and height of the image.
    Args:
        prompt (str): The prompt for the image to be generated. Should be multiple keywords.
        negative_prompt(str): The negative prompt for the things that should not be in the generated image. Should be multiple keywords. Like: 'deformed', 'ugly', 'missing fingers' etc.
        width (ImageSize): Image width.
        height (ImageSize): Image height.
    Returns:
        str: The path to the generated image.
    """
    height = int(height.value)
    width = int(width.value)

    generated_images = pipeline(prompt=prompt, negative_prompt=negative_prompt, height=height, width=width).images

    timestamp = datetime.datetime.now().strftime("%Y.%m.%d_%H-%M-%S")
    generated_images[0].save(f"./{timestamp}_generated_image.png")
    return f"./{timestamp}_generated_image.png"


generate_image_tool = LlamaCppFunctionTool(generate_image)

model = LlamaCppServerProvider(
    "http://localhost:8080"
)
generation_settings = LlamaCppSamplingSettings(
    temperature=0.45, top_k=60, top_p=0.85, repeat_penalty=1.1, repeat_last_n=128,
    min_p=0.1, tfs_z=0.975, stream=True)

structured_output = LlmStructuredOutputSettings.from_functions([generate_image], add_thoughts_and_reasoning_field=False)

agent = LlamaCppAgent(model, system_prompt="""Use this formula to create a 3-prompts list for an art idea. Make sure to connect the parts so they read like a single sentence.


Here's the formula: [Appropriate Type of Artwork] [Location] in portrait orientation. [Scene], [Bottom Text], [Color Scheme], [Mood or Emotion]

[Appropriate Type of Artwork]: Choose "Vintage Travel Poster for".

[Location]: Main location to travel in the poster. Example: Venus or Paris

[Scene]: Illustrate the dense, yellowish clouds of Venus as the backdrop. Include a captivating silhouette of a vintage rocket ship approaching the planet. Integrate enigmatic shapes suggesting mountains and valleys beneath the clouds.

[Bottom Text]: Place the text 'Explore Venus: Beauty Behind the Mist' at the bottom of the poster.

[Color Scheme]: Use a color scheme predominantly comprised of golds, yellows, and soft oranges to evoke a sense of wonder and curiosity.

[Mood or Emotion]: Tell how the art should make people feel. Example: Happy and relaxed.


Special Note: Always give me 3 prompts based on the subject I provide. Each prompt should be different and use the formula above. Keep it under 40 words. Use only commas to separate parts.""", debug_output=True)


result = agent.get_chat_response("Create 3 vivid images of the dawning of the age of aquarius in a spiritual way fulfilled by the arrive of large language models. Always use different prompts and negative prompts for each image!", structured_output_settings=structured_output, llm_sampling_settings=generation_settings)

print(result)