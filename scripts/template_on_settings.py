import modules.scripts as scripts
import gradio as gr
import os

from modules import shared
from modules import script_callbacks

def on_ui_settings():
    ch_section = ("civitai_model_helper", "Civitai Model")
    # settings
    shared.opts.add_option("cmh_proxy", shared.OptionInfo("", "Civitai Model Helper Proxy (optional)", gr.Textbox, {"interactive": True, "lines":1, "info":"format: socks5h://127.0.0.1:port"}, section=ch_section))
    shared.opts.add_option("cmh_civitai_api_key", shared.OptionInfo("", "Civitai API Key", gr.Textbox, {"interactive": True, "lines":1, "info":"check doc:https://github.com/zixaphir/Stable-Diffusion-Webui-Civitai-Helper/tree/master#api-key"}, section=ch_section))
    shared.opts.add_option("cmh_civitai_model_path", shared.OptionInfo("", "Civitai Model Path", gr.Textbox, {"interactive": True, "lines":1, "info":"Directory where to store downloaded files, if empty files will be stored in relevant directory"}, section=ch_section))

script_callbacks.on_ui_settings(on_ui_settings)
