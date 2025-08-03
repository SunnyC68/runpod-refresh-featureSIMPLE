
# Start from the RunPod Pytorch image you tested with
FROM runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04

# Set the working directory
WORKDIR /workspace

# Copy your installer script into the image
COPY install_comfyui_3.12_2.7+12.8_.sh .

# Run your script to set up ComfyUI. This happens only ONCE during build.
RUN chmod +x ./install_comfyui_3.12_2.7+12.8_.sh && ./install_comfyui_3.12_2.7+12.8_.sh

# Now, copy your Python handler that will run on every API call
COPY rp_handler.py .

# This is the command that starts your serverless worker
CMD python -u /workspace/rp_handler.py