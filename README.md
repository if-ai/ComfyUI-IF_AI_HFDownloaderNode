# ComfyUI-IF_AI_HFDownloaderNode

Download HF repos from comfy.

## Faster Download

To enable faster downloads, install the extra package from Hugging Face.

1. Activate your ComfyUI environment and install the package:

    ```bash
    pip install huggingface_hub[hf_transfer]
    ```

2. Export the environment variable:

    ```bash
    nano ~/.bashrc
    ```

    Add the following line:

    ```bash
    export HF_HUB_ENABLE_HF_TRANSFER=1
    ```

    Save and close the file, then reload your bash configuration:

    ```bash
    source ~/.bashrc
    ```

3. For Windows:

    - Press `Win + R` and type `systempropertiesadvanced`.
    - Click on the "Environment Variables" button.

    ![SystemPropertiesAdvanced_LBxcaibjOE](https://github.com/if-ai/ComfyUI-IF_AI_HFDownloaderNode/assets/21185218/d6177287-3cb7-42bf-b216-14acb91fb3e1)

    - Create a new system variable with the name `HF_HUB_ENABLE_HF_TRANSFER` and the value `1`.

    ![SystemPropertiesAdvanced_S1aWUb9EwP](https://github.com/if-ai/ComfyUI-IF_AI_HFDownloaderNode/assets/21185218/129ba069-928e-40f5-b44f-80f5579fb6da)




## Prerequisites
HuggingFAce hub from the reqs

1. Get the repo ID from Hugging face
2. select individual or whole repo on the switch
3. copy the name of the individual file
4. create a folder where you want to download the files or repo
5. download everything
6. might need to add a HF Token
7. 🚨Do not save or share your workflows with the TOKENS weritten
   in fact do not share WF using this Node⚠️
8.Once downloaded you can drag the files out to the correct location 

## Tutorial 
[Video Title](https://youtu.be/0KWy3xiPado)


## Related Tools
- [IF_prompt_MKR](https://github.com/if-ai/IF_prompt_MKR) - A similar tool available for Stable Diffusion WebUI
- [IF_AI_tools](https://github.com/if-ai/ComfyUI-IF_AI_tools) - LLM Nodes for chating and Creating SD prompts locally with Ollama or Via APIs
