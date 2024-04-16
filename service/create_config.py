import json
from TTS.tts.configs.tacotron_config import TacotronConfig

# Instantiate Tacotron2Config
config = TacotronConfig()

# Modify max_decoder_steps
config.max_decoder_steps = 1000
config.max_audio_len = 40

# Write the configuration to a file
with open('config.json', 'w') as f:
    json.dump(config, f, default=lambda o: o.__dict__, sort_keys=True, indent=4)
