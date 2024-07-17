# ComfyUI-IF_AI_HFDownloaderNode

Download HF repos from comfy.
![HFDownloader](https://github.com/user-attachments/assets/10232d11-24f6-4787-a434-4e428942bb76)

## Installation

- You can clone this repo to your comfy custom nodes folder.

    ```bash
    git clone https://github.com/if-ai/ComfyUI-IF_AI_HFDownloaderNode.git
    ```
    
1. Activate your ComfyUI environment and install the package:

    ```bash
    pip install requirements.txt
    ```

2. Export the environment variable:

    ```bash
    nano ~/.bashrc
    ```

    Add the following line:

    ```bash
    export HF_TOKEN=Your_Access_Token_from_your_HF_account
    ```

    Save and close the file, then reload your bash configuration:

    ```bash
    source ~/.bashrc
    ```

3. For Windows:

    - Press `Win + R` and type `systempropertiesadvanced`.
    - Click on the "Environment Variables" button.
![explorer_1PjxFBzcXz](https://github.com/user-attachments/assets/d631a16c-2b72-4fc7-9f33-89ea4263d428)

   
![SystemPropertiesAdvanced_tj1x4S8xwX](https://github.com/user-attachments/assets/479ea5d9-8716-4110-93bb-c9866d56649b)

    - Create a new system variable with the name `HF_TOKEN` and the value `Your_Access_Token_from_your_HF_account`.
![NVIDIA_Share_qehsri6Raq](https://github.com/user-attachments/assets/08616a97-cf13-4a3c-89c9-91e2b8629c3a)

    



## Prerequisites
HuggingFAce hub from the reqs

1-.Take a repo ID from HF it can be a HF Space too. example "Kwai-Kolors/Kolors"

2-. On the bottom you can select individual Mode here you can select a single or coma separate names from a repo "vae/diffusion_pytorch_model.bin,model_index.json" will download the vae model inside the vae folder and the model_index.json at the root of kolors  

3-. You can specify a path or use the default directory at the root of comfy ComfyUI/models/IF_AI with the same name as the repo you are downloading

4-. Exclude the files when on whole repo or space mode works the same as number 2 but exclude the files instead

5-. HuggingFace token you need to either write an access token here form the settings on your HF profile or create an environment variable for your user named HF_TOKEN, optionally
Create a .env file in the root directory of the node with HF_TOKEN=your_token_here 

6-. You can specify a folder to download

7-. Mode individual or download the full repo/space

🚨Do not save or share your workflows with the TOKENS weritten
   in fact do not share WF using this Node⚠️


## Tutorial 
[VIDEO USING THE NODE](https://youtu.be/0KWy3xiPado)


## Related Tools
- [IF_prompt_MKR](https://github.com/if-ai/IF_prompt_MKR) - A similar tool available for Stable Diffusion WebUI
- [IF_AI_tools](https://github.com/if-ai/ComfyUI-IF_AI_tools) - LLM Nodes for chating and Creating SD prompts locally with Ollama or Via APIs
