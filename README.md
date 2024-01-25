# Civitai Model
## Stable Diffusion Automatic1111 Extension

## Overview

This extension enhances the capabilities of Stable Diffusion Automatic1111 by adding features to interact with various models from the "civitai" website. It includes functionalities like viewing model details, downloading model files directly from the extension with a progress bar,settings customization, and prompt generator.

## Features

1. **Model Display:**
    - Checkpoint
    - Textual Inversion
    - Hypernetwork
    - Aesthetic Gradient
    - LORA
    - Controlnet
    - Poses
    - Prompt Generator

2. **Download Model:**
    - Download model files directly from the extension.
    - Progress bar in the console for download status.
    - Models saved in relevant directories (e.g., LORA in 'lora' directory, Checkpoint in 'Stable-diffusion' directory).
    - AestheticGradient and Poses saved into common_files dir that will be auto created.

3. **View Model Details:**
    - Easily navigate to the civitai website to view detailed information about the selected model.

4. **Settings:**
    - Proxy configuration
    - Civitai API key input <small>to get [API Key](https://github.com/grim-reapper/aci-sd-webui-civitai-models#civitai-api-key)</small>
    - Choose the path to save model files
    - If the path is empty, models are saved to the respective automatic1111 relevant directories.

5. **Aspect Ratio:**
    - Choose from predefined aspect ratios for images.

## Getting Started

1. **Installation:**
   - Go to SD webui's extension tab, go to `Install from url` sub-tab.
   - Copy this project's url into it, click install.
   - Alternatively, download this project as a zip file, and unzip it to `Your SD webui folder/extensions`.
   - Everytime you install or update this extension, you need to shutdown SD Webui and Relaunch it. Just "Reload UI" won't work for this extension.
   
   Done.


2. **Configuration:**
    - Open the extension settings.
    - Set up proxy, civitai API key, and choose the path to save model files.

3. **Usage:**
    - Navigate through the extension tabs to access various features.
    - Download models, view details, and customize aspect ratios.

## Download
To download a model:
* You will find a download button model on card, just click to download.

### Civitai API Key
You need to login civitai to download some models. To do this with Civitai API, you need to create an API Key in your account settings on Civitai's website.

follow link for this: [wiki](https://github.com/zixaphir/Stable-Diffusion-Webui-Civitai-Helper/wiki/Civitai-API-Key).

Here is a simple tutorial:
* Login civitai.com
* go to [your account's setting page](https://civitai.com/user/account)
* At the bottom of that page, find the "API Keys" section.
* Click "Add API Key" button, give a name.
* Copy the api key string, paste to this extension's setting page -> Civitai API Key section.
* Save setting and Reload SD webui

## Screenshots
### Setting
![Civitai Model settings](images/settings.jpeg?raw=true "Civitai Model settings")
### Civitai Model tab <small>(as you click on model tab it will load model, so wait for few seconds)</small>
![Civitai Model tab](images/tab.jpeg?raw=true "Civitai Model tab")
### Civitai Model aspect ratio
![Civitai Model aspect ratio](images/aspect-ratio.jpeg?raw=true "Civitai Model aspect ratio")
### Built in prompt generator
![Civitai Model aspect ratio](images/prompt_generator.jpeg?raw=true "Prompt Generator")
## Contributing
Feel free to contribute by submitting bug reports, feature requests, or even pull requests. Your input is highly appreciated!

## License
This project is licensed under the [MIT License](./LICENSE).