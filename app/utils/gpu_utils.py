import onnxruntime as ort
from app.utils.logger import setup_logger

logger = setup_logger("gpu_utils", "central.log")

def get_onnx_execution_providers(use_gpu: bool = False):
    """
    Returns the execution providers for ONNXRuntime.
    If use_gpu is True and CUDA is available, returns ['CUDAExecutionProvider', 'CPUExecutionProvider'].
    Otherwise, returns ['CPUExecutionProvider'].
    """
    available_providers = ort.get_available_providers()
    logger.info(f"Available ONNXRuntime providers: {available_providers}")
    
    if use_gpu and "CUDAExecutionProvider" in available_providers:
        logger.info("ONNXRuntime GPU acceleration (CUDA) is available and enabled.")
        return ["CUDAExecutionProvider", "CPUExecutionProvider"]
    
    logger.info("ONNXRuntime CPU execution provider is used.")
    return ["CPUExecutionProvider"]

def is_gpu_available() -> bool:
    """Returns True if CUDA is available in ONNXRuntime providers."""
    return "CUDAExecutionProvider" in ort.get_available_providers()
