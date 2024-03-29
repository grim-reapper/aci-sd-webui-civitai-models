import modules.scripts as scripts
import gradio as gr
import os
import requests
from constants import EXTENSION_NAME, API_URL, MAX_RETRIES, BACKOFF_FACTOR, API_MODEL_ENDPOINT, MODEL_URL, COMMON_PATH
from modules import script_callbacks
from scripts import downloader, util
from modules import shared
import modules
from pathlib import Path
from scripts.prompt_generator import populate_options, generate_prompt_output, add_to_prompt

lora_dir = Path(shared.cmd_opts.lora_dir).resolve()
base_dir = Path(shared.data_path).resolve()

if not os.path.exists(os.path.join(base_dir, COMMON_PATH)):
    os.makedirs(os.path.join(base_dir, COMMON_PATH))

def on_ui_tabs():
    txt2img_prompt = modules.ui.txt2img_paste_fields[0][0]
    img2img_prompt = modules.ui.img2img_paste_fields[0][0]

    txt2img_negative_prompt = modules.ui.txt2img_paste_fields[1][0]
    img2img_negative_prompt = modules.ui.img2img_paste_fields[1][0]

    with gr.Blocks(analytics_enabled=False) as ui_component:
        js_download_model_box = gr.Textbox(lines=1, visible=False, value="", show_label=False, elem_id="gr_js_download_model_url")
        js_page_number_box = gr.Textbox(lines=1, visible=False, value="1", show_label=False, elem_id="gr_js_page_number")
        js_download_btn = gr.Button(
            value="Search",
            variant="primary",
            size="sm",
            scale=0,
            elem_id="gr_download_btn",
            visible=False
        )
        with gr.Tab("Civitai Models"):
            with gr.Row():
                model_type = gr.Radio(["All", "Checkpoint", "TextualInversion", "Hypernetwork", "AestheticGradient", "LORA", "Controlnet", "Poses"], label="Model Types", info="Model type you want to filter out", value="All", elem_id="gr_model_types")
                model_name = gr.Textbox(
                    label="Model name",
                    info="filter by model name (Optional)",
                    lines=1,
                    elem_id="gr_model_name",
                    type="text",
                )
            with gr.Row():
                model_limit = gr.Slider(minimum=10, maximum=100, step=10, label="Limit", value=10,info="Choose between 10 and 100", elem_id="gr-page-limit")
                btn = gr.Button(
                    value="Search",
                    variant="primary",
                    size="sm",
                    scale=0,
                    elem_id="gr_search_btn",
                    visible=False
                )

            btn.click(
                gradio_interface,
                inputs=[model_type, model_name, model_limit, js_page_number_box],
                outputs=gr.HTML()
            )

            js_download_btn.click(download_handler, inputs=[js_download_model_box], outputs=gr.HTML())
            cmh_proxy = shared.opts.data.get("cmh_proxy", "")
            cmh_civitai_api_key = shared.opts.data.get("cmh_civitai_api_key", "")

            # set civitai_api_key
            has_api_key = False
            if cmh_civitai_api_key:
                has_api_key = True
                util.civitai_api_key = cmh_civitai_api_key
                util.def_headers["Authorization"] = f"Bearer {cmh_civitai_api_key}"

            util.printD(f"use civitai api key: {has_api_key}")

            # set proxy
            if cmh_proxy:
                util.proxies = {
                    "http": proxy,
                    "https": proxy,
                }

        with gr.Tab("Prompt Generator"):
            with gr.Row():
                with gr.Column():
                    category_choices, style_choices, lighting_choices, lens_choices = populate_options()
                    with gr.Row():
                        gr.HTML('''<h2 id="input_header">Input</h2>''')
                    with gr.Row().style(equal_height=True):
                        category_dropdown = gr.Dropdown(
                            choices=category_choices,
                            value=category_choices[1],
                            label="Category", show_label=True
                        )

                        style_dropdown = gr.Dropdown(
                            choices=style_choices,
                            value=style_choices[1],
                            label="Style", show_label=True
                        )
                    with gr.Row():
                        lighting_dropdown = gr.Dropdown(
                            choices=lighting_choices,
                            value=lighting_choices[1],
                            label="Lighting", show_label=True
                        )

                        lens_dropdown = gr.Dropdown(
                            choices=lens_choices,
                            value=lens_choices[1],
                            label="Lens", show_label=True
                        )
                    with gr.Row():
                        gr.HTML('''
                        <hr class="rounded" id="divider">
                    ''')
                    with gr.Row():
                        gr.HTML('''
                            <h2><a href="https://www.patreon.com/aiartsnaps764" target="_blank">Become a Patreon</a></h2>
                            <h2><a href="https://www.buymeacoffee.com/imi291" target="_blank">Buy me a Coffee</a></h2>
                            <h2><a href="https://www.instagram.com/aiartsnaps764/" target="_blank">Instagram</a></h2>
                            <h2><a href="https://www.pinterest.com/imranali125/" target="_blank">Pinterest</a></h2>
                            <h2><a href="https://civitai.com/user/silentlips007" target="_blank">CivitAi</a></h2>
                    ''')
                with gr.Column():
                    with gr.Row():
                        gr.HTML('''<h2 id="output_header">Output</h2>''')
                    result_textbox = gr.Textbox(
                        label="Generated Prompt", lines=3)
                    use_default_negative_prompt = gr.Checkbox(
                        label="Include Negative Prompt", value=True, interactive=True, elem_id="negative_prompt_checkbox")
                    setattr(use_default_negative_prompt,
                            "do_not_save_to_config", True)
                    with gr.Row():
                        txt2img = gr.Button("Send to txt2img")
                        img2img = gr.Button("Send to img2img")
                    # Create a button to trigger text generation
                    txt2img.click(add_to_prompt, inputs=[result_textbox, use_default_negative_prompt], outputs=[
                        txt2img_prompt, txt2img_negative_prompt]).then(None, _js='switch_to_txt2img', inputs=None, outputs=None)
                    img2img.click(add_to_prompt, inputs=[result_textbox, use_default_negative_prompt], outputs=[
                        img2img_prompt, img2img_negative_prompt]).then(None, _js='switch_to_img2img', inputs=None, outputs=None)
                    generate_button = gr.Button(
                        value="Generate", elem_id="generate_button", variant="primary")
        generate_button.click(fn=generate_prompt_output, inputs=[
                category_dropdown, style_dropdown, lighting_dropdown, lens_dropdown, use_default_negative_prompt], outputs=[result_textbox])

    return [(ui_component, EXTENSION_NAME, "gr_extension_tab")]


def api_call(model_type, model_name, items_per_page=10, page=1):
    api_url = API_URL
    params = {
        "page": page,
        "limit": items_per_page
    }
    if model_type != "All":
        params['types'] = model_type

    if model_name != '':
        params['query'] = model_name

    response = requests.get(api_url, params=params)
    # Assuming the API returns a JSON response with a list of items
    result = response.json()
    return result

def gradio_interface(model_type, model_name, items_per_page=10, page=1):
    items = api_call(model_type, model_name, items_per_page, page)
    # Create a list of card objects for each item
    components = [
        generate_card(item) for item in items['items']
    ]
    join_cards = ''.join(components)
    pagination_str = pagination(items)
    return f"""
        <div class="gr-wrapper">
        {pagination_str}
         <div class="gr_model_cards">
         {join_cards}
         </div>
        </div>
    """

def pagination(items):
    if items:
        return f"""
            <div class="gr-pagination">
                {"<button class='gr-previous-page primary' data-url='"+items['metadata']['prevPage']+"'>Previous Page</button>" if 'prevPage' in items['metadata'] else ''}
                {"<button class='gr-next-page primary' data-url='"+items['metadata']['nextPage']+"'>Next Page</button>" if 'nextPage' in items['metadata'] else ''}
            </div>
        """
    return ""
def generate_card(item):
    src_type = ''
    if len(item['modelVersions'][0]["images"]):
        if item['modelVersions'][0]["images"][0]['type'] == 'video':
            src_type = f"""
                <video playsinline loop autoplay style="width:100%"><source src="{item['modelVersions'][0]["images"][0]["url"]}" type="video/mp4"></video>
            """
        else:
            src_type = f"""
                <img src="{item['modelVersions'][0]["images"][0]["url"]}" style="width:100%">
            """
    else:
        src_type = f"""<img src="https://media.istockphoto.com/vectors/no-thumbnail-image-vector-graphic-vector-id1147544810?k=6&m=1147544810&s=612x612&w=0&h=LLdG9L4tfdum-uXqfrsw6VGkmQkw2Y_BnL9bYGczsfk=" style="width:100%">"""

    return f"""
        <div class="card">
            <div class="gr_card_root">
            <div class="gr_wrapper">
                <div class="gr_model_type">{item['type']}</div>
                {src_type}
                <div class="container">
                    <h4><b>{item["name"]}</b></h4>
                    <div class="gr-action-btn">
                    <button onclick="download_handler('{item['modelVersions'][0]["id"]}', '{item['type']}')"><svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" class="tabler-icon tabler-icon-download"><path d="M4 17v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2 -2v-2"></path><path d="M7 11l5 5l5 -5"></path><path d="M12 4l0 12"></path></svg> Download</button>
                    <a target="_blank" href="{MODEL_URL+'/'+ str(item['modelVersions'][0]["modelId"])}" class="gr-civitai-url" title="Open this model's civitai url">🌐 View</a>
                    </div>
                </div>
            </div>
            </div>
        </div>
    """
def download_handler(file_id):
    cmh_civitai_model_path = shared.opts.data.get("cmh_civitai_model_path", "")

    if cmh_civitai_model_path and not os.path.isdir(cmh_civitai_model_path):
        util.printD("Specified path is not a folder: "+cmh_civitai_model_path)

    if cmh_civitai_model_path and not os.path.exists(cmh_civitai_model_path):
        os.makedirs(cmh_civitai_model_path)

    split_model = file_id.split(',')
    # Make a request to get a model file
    url = f"{API_MODEL_ENDPOINT}/{split_model[0]}"
    downloader.dl(url, cmh_civitai_model_path, None, None, model_type=split_model[1])

script_callbacks.on_ui_tabs(on_ui_tabs)