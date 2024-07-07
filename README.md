# ComfyUI-IF_AI_HFDownloaderNode
Download HF repos from comfy 
Possible faster download install this extra package from HF
activate your comfyui environment and  
'pip install huggingface_hub[hf_transfer]'
and export your variable
nano ~/.bashrc
export HF_HUB_ENABLE_HF_TRANSFER=1
windows press win+r type systempropertiesadvanced
![SystemPropertiesAdvanced_LBxcaibjOE](https://github.com/if-ai/ComfyUI-IF_AI_HFDownloaderNode/assets/21185218/d6177287-3cb7-42bf-b216-14acb91fb3e1)
neme your new system variable 'HF_HUB_ENABLE_HF_TRANSFER'
variable value '1'
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
