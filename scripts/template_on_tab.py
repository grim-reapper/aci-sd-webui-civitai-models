import modules.scripts as scripts
import gradio as gr
import os
import requests
from constants import EXTENSION_NAME, API_URL, MAX_RETRIES, BACKOFF_FACTOR, API_MODEL_ENDPOINT, MODEL_URL
from modules import script_callbacks
from scripts import downloader, util
from modules import shared
from pathlib import Path

lora_dir = Path(shared.cmd_opts.lora_dir).resolve()
base_dir = Path(shared.data_path).resolve()

def on_ui_tabs():
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
    return f"""
        <div class="card">
            <div class="gr_card_root">
            <div class="gr_wrapper">
                <div class="gr_model_type">{item['type']}</div>
                <img src="{item['modelVersions'][0]["images"][0]["url"] if len(item['modelVersions'][0]["images"]) else 'https://media.istockphoto.com/vectors/no-thumbnail-image-vector-graphic-vector-id1147544810?k=6&m=1147544810&s=612x612&w=0&h=LLdG9L4tfdum-uXqfrsw6VGkmQkw2Y_BnL9bYGczsfk='}" alt="Image" style="width:100%">
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