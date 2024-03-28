import json  # Import the json module

# Here is an example of a config file for the Flask app:

config = {
    "model_path": "path_to_your_model.pth",
    "config_path": "path_to_your_config.json",
    "use_cuda": False,
    "audio": {
        "num_mels": 80,
        "num_freq": 1025,
        "sample_rate": 22050,
        "frame_length_ms": 50,
        "frame_shift_ms": 12.5,
        "preemphasis": 0.97,
        "min_level_db": -100,
        "ref_level_db": 20,
        "power": 1.5,
        "griffin_lim_iters": 60,
        "signal_norm": True,
        "symmetric_norm": True,
        "max_norm": 4.0,
        "clip_norm": True,
        "mel_fmin": 0.0,
        "mel_fmax": 8000.0,
        "do_trim_silence": True,
        "trim_db": 60,
        "do_sound_norm": False,
        "stats_path": None,
        "base_directory": "/path/to/your/base/directory"
    }
}

# Save the config to a file
with open('config.json', 'w') as f:
    json.dump(config, f, indent=4)

# Print a success message
print("The config file was successfully created and saved as config.json.")
