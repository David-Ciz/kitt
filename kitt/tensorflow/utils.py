def gpu_share_memory():
    import tensorflow as tf

    for device in tf.config.list_physical_devices("GPU"):
        tf.config.experimental.set_memory_growth(device, True)
