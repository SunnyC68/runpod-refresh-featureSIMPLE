
# Start from the RunPod Pytorch image you tested with
FROM runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04

# Set the working directory
WORKDIR /workspace

# Copy your installer script into the image
COPY install_comfyui_3.12_2.7+12.8_.sh .

# Run your script to set up ComfyUI. This happens only ONCE during build.
RUN chmod +x ./install_comfyui_3.12_2.7+12.8_.sh && ./install_comfyui_3.12_2.7+12.8_.sh

# Install required custom nodes
RUN cd /workspace/ComfyUI && \
    git clone --recursive --depth 1 https://github.com/Fannovel16/comfyui_controlnet_aux.git ./custom_nodes/comfyui_controlnet_aux && \
    git clone --depth 1 https://github.com/asagi4/comfyui-adaptive-guidance.git ./custom_nodes/comfyui-adaptive-guidance && \
    git clone --depth 1 https://github.com/cubiq/ComfyUI_essentials.git ./custom_nodes/ComfyUI_essentials && \
    git clone --depth 1 https://github.com/kijai/ComfyUI-KJNodes.git ./custom_nodes/ComfyUI-KJNodes && \
    git clone --depth 1 https://github.com/chibiace/ComfyUI-Chibi-Nodes.git ./custom_nodes/ComfyUI-Chibi-Nodes && \
    git clone --depth 1 https://github.com/TheBill2001/comfyui-upscale-by-model.git ./custom_nodes/comfyui-upscale-by-model && \
    git clone --depth 1 https://github.com/Goktug/comfyui-saveimage-plus.git ./custom_nodes/Save-Image-Plus && \
    git clone --depth 1 https://github.com/Ltamann/ComfyUI-TBG-ETUR.git ./custom_nodes/ComfyUI-TBG-ETUR && \
    git clone --depth 1 https://github.com/mit-han-lab/ComfyUI-nunchaku.git ./custom_nodes/nunchaku_nodes

# Install custom node dependencies using the --no-deps strategy
RUN . /workspace/ComfyUI/venv/bin/activate && \
    pip install easy-dwpose --no-deps && \
    pip install \
        onnxruntime-gpu==1.18.0 \
        -r /workspace/ComfyUI/custom_nodes/comfyui_controlnet_aux/requirements.txt \
        -r /workspace/ComfyUI/custom_nodes/ComfyUI_essentials/requirements.txt \
        -r /workspace/ComfyUI/custom_nodes/nunchaku_nodes/requirements.txt && \
    pip install https://huggingface.co/mit-han-lab/nunchaku/resolve/main/nunchaku-0.3.1%2Btorch2.7-cp312-cp312-linux_x86_64.whl

# Create symlinks from the default ComfyUI model directories to the /runpod-volume
RUN cd /workspace/ComfyUI/models && \
    for dir in checkpoints configs vae loras upscale_models embeddings hypernetworks controlnet clip clip_vision style_models unet text_encoders photomaker diffusion_models gligen; do \
        mkdir -p /runpod-volume/ComfyUI/models/$dir; \
        rm -rf $dir; \
        ln -s /runpod-volume/ComfyUI/models/$dir $dir; \
    done



# Copy requirements and install handler dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Now, copy your Python handler that will run on every API call
COPY rp_handler.py .

# This is the command that starts your serverless worker
# The handler will automatically start ComfyUI and then initialize the RunPod worker
CMD ["python", "-u", "/workspace/rp_handler.py"]