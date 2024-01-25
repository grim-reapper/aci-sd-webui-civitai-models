import json
import random
from pathlib import Path
import modules.scripts as scripts


result_prompt = ""
base_dir = scripts.basedir()
dropdown_options_file = Path(base_dir, "content/dropdown_options.json")
category_data_file = Path(base_dir, "content/category_data.json")
style_data_file = Path(base_dir, "content/style_data.json")
prefix_data_file = Path(base_dir, "content/prefix_data.json")
lighting_data_file = Path(base_dir, "content/lighting_data.json")
lens_data_file = Path(base_dir, "content/lens_data.json")

def populate_options():
    with open(dropdown_options_file, 'r') as f:
        data = json.load(f)
    category_choices = data['category']
    style_choices = data['style']
    lighting_choices = data['lighting']
    lens_choices = data['lens']
    return tuple(category_choices), tuple(style_choices), tuple(lighting_choices), tuple(lens_choices)

def get_random_prompt(data):
    random_key = random.choice(list(data.keys()))
    random_array = random.choice(data[random_key])
    random_strings = random.sample(random_array, 3)
    return random_strings

def add_to_prompt(*args):
    prompt, use_default_negative_prompt = args
    default_negative_prompt = "(worst quality:1.2), (low quality:1.2), (lowres:1.1), (monochrome:1.1), (greyscale), multiple views, comic, sketch, (((bad anatomy))), (((deformed))), (((disfigured))), watermark, multiple_views, mutation hands, mutation fingers, extra fingers, missing fingers, watermark"
    if(use_default_negative_prompt):
        return prompt, default_negative_prompt
    else:
        return prompt, ''

def get_correct_prompt(data, selected_dropdown):
    correct_array = data[selected_dropdown]
    random_array = random.choice(correct_array)
    random_strings = random.sample(random_array, 3)
    random_strings.insert(0, selected_dropdown)

    return random_strings

def generate_prompt_output(*args):
    # all imported files
    prefix_path = prefix_data_file
    category_path = category_data_file
    style_path = style_data_file
    lighting_path = lighting_data_file
    lens_path = lens_data_file

    # destructure args
    category, style, lighting, lens, negative_prompt = args

    # Convert variables to lowercase
    category = category.lower()
    style = style.lower()
    lighting = lighting.lower()
    lens = lens.lower()

    # Open category_data.json and grab correct text
    with open(prefix_path, 'r') as f:
        prefix_data = json.load(f)
        prefix_prompt = random.sample(prefix_data, 6)
        modified_prefix_prompt = [f"(({item}))" for item in prefix_prompt]

    # Open category_data.json and grab correct text
    with open(category_path, 'r') as f2:
        category_data = json.load(f2)

    if category == "none":
        category_prompt = ""
    elif category == "random":
        category_prompt = get_random_prompt(category_data)
    else:
        category_prompt = get_correct_prompt(category_data, category)

    # Open style_data.json and grab correct text
    with open(style_path, 'r') as f3:
        style_data = json.load(f3)

    if style == "none":
        style_prompt = ""
    elif style == "random":
        style_prompt = get_random_prompt(style_data)
    else:
        style_prompt = get_correct_prompt(style_data, style)

    # Open lighting_data.json and grab correct text
    with open(lighting_path, 'r') as f4:
        lighting_data = json.load(f4)

    if lighting == "none":
        lighting_prompt = ""
    elif lighting == "random":
        lighting_prompt = get_random_prompt(lighting_data)
    else:
        lighting_prompt = get_correct_prompt(lighting_data, lighting)

    # Open lens_data.json and grab correct text
    with open(lens_path, 'r') as f5:
        lens_data = json.load(f5)

    if lens == "none":
        lens_prompt = ""
    elif lens == "random":
        lens_prompt = get_random_prompt(lens_data)
    else:
        lens_prompt = get_correct_prompt(lens_data, lens)

    prompt_output = modified_prefix_prompt, category_prompt, style_prompt, lighting_prompt, lens_prompt
    prompt_strings = []

    for sublist in prompt_output:
        # Join the sublist elements into a single string
        prompt_string = ", ".join(str(item) for item in sublist)
        if prompt_string:  # Check if the prompt_string is not empty
            prompt_strings.append(prompt_string)

    # Join the non-empty prompt_strings
    final_output = ", ".join(prompt_strings)

    return final_output

