# ArmSpeech: Armenian Speech Recogition Library.

ArmSpeech is an offline Armenian speech recognition library (speech-to-text) and CLI tool based on [Coqui STT (🐸STT)](https://stt.readthedocs.io/en/latest/) and trained on the [ArmSpeech](https://www.ijscia.com/full-text-volume-3-issue-3-may-jun-2022-454-459/) dataset. [Coqui STT (🐸STT)](https://stt.readthedocs.io/en/latest/) is an open-source implementation of Baidu’s Deep Speech deep neural network. The engine is based on a recurrent neural network (RNN) and consists of 5 layers of hidden units.

The acoustic model and language model work together to produce better accuracy of prediction. The acoustic model uses a sequence-to-sequence algorithm, to learn which acoustic signals correspond to which letters in the language alphabet (outputs probabilities for each class of character, not at the word level). To distinguish homonyms (words that sound the same but are spelled differently), a language model comes to the rescue, which predicts which words will follow each other in a sequence (n-gram modeling).

For acoustic model training and validating used ArmSpeech Armenian spoken language corpus total of 15.7 hours. Language model training is based on the [KenLM Language Model Toolkit](https://kheafield.com/code/kenlm/) library. Necessary data for language model training was scraped from Armenian news websites articles about medicine, sport, culture, lifestyle, and politics.

If want to help me to increase the accuracy of transcriptions, then <a href="https://www.buymeacoffee.com/U2jtXgrwj4"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=U2jtXgrwj4&button_colour=FFDD00&font_colour=000000&font_family=Lato&outline_colour=000000&coffee_colour=ffffff" /></a>

## API

ArmSpeech can be used both as a Python module and a CLI tool. The library can be used in two ways:
* transcribe wav audio file,
* transcribe audio stream from microphone.

In both cases audio has the same parameters:
* wav audio format,
* mono channel,
* 16000hz sample rate.

### Python

| Function name | Description                    |
| ------------- | ------------------------------ |
| `set_beam_width(self, beam_width: int) -> int`      | Set the beam width value of the model (beam width used in the CTC decoder when building candidate transcriptions). A larger beam width value generates better results but increases decoding time. The function takes an integer (`beam_width`) and returns zero on success, and non-zero on failure. The default value is 1024.       |
| `set_scorer_alpha_beta(alpha: float, beta: float) -> int`   | Set hyperparameters alpha and beta of the external scorer (language model weight (`alpha`) and word insertion weight (`beta`) of the decoder. The function takes two floats (`alpha`, `beta`) and returns zero on success, and non-zero on failure. The default values are 0.931289039105002 for the `alpha` and 1.1834137581510284 for the `beta`.     |
| `from_wav(self, wav_path: str, get_metadata: bool = False) -> str`   | Transcribe wav audio file. The function takes two parameters: the absolute path of the audio file (`wav_path`) and a boolean parameter (`get_metadata`) for enabling metadata generation. `get_metadata` parameter is optional and the default value is false. The function returns either the transcript or a tuple of metadata, which includes the transcript too.     |
| `from_mic(self, vad_aggresivness: int = 3, spinner: bool = False, wav_save_path: str = None, get_metadata = False)`   | Transcribe audio stream taken from microphone. The generator function takes four parameters: an integer number (`vad_aggresivness`) in a range of [0, 3] for voice activity detection aggressiveness, a boolean for showing spinner (`spinner`) in the console while detected voice activity, an absolute path (`wav_save_path`) to save transcribed speeches, and a boolean parameter (`get_metadata`) for enabling metadata generation. All the parameters are optional (value of 3 for `vad_aggresivness`, false for `get_metadata` and `spinner`, and empty for `wav_save_path`. The function returns either the transcript or a tuple of metadata, which includes the transcript too.     |

The `from_mic()` generator function uses voice activity detection technology to detect speech by simply distinguishing between silence and speech. This is done by using Python free “webrtcvad” module, which is a Python interface to the WebRTC Voice Activity Detector (VAD) developed by Google. The application determines voice activity by a ratio of not null and null frames in 300 milliseconds. The portion of not null frames in given milliseconds must be equal to or greater than 75%.

In `from_mic()` and `from_wav()` functions setting the `get_metada` parameter to true, returns metadata of the audio file or stream, which includes the transcript, confidence score, and position of the token in seconds. An example of returned metadata is below:

`('հայերն աշխարհի հնագույն ազգերից մեկն են', -7.672598838806152, ('հ', 0.29999998211860657), ('ա', 0.41999998688697815), ('յ', 0.4399999976158142), ('ե', 0.5), ('ր', 0.5199999809265137), ('ն', 0.5399999618530273), (' ', 0.6800000071525574), ('ա', 0.699999988079071), ('շ', 0.7400000095367432), ('խ', 0.8999999761581421), ('ա', 0.9399999976158142), ('ր', 0.9599999785423279), ('հ', 1.0), ('ի', 1.0399999618530273), (' ', 1.1799999475479126), ('հ', 1.1999999284744263), ('ն', 1.2400000095367432), ('ա', 1.399999976158142), ('գ', 1.5), ('ո', 1.5199999809265137), ('ւ', 1.5799999237060547), ('յ', 1.6799999475479126), ('ն', 1.7799999713897705), (' ', 1.7999999523162842), ('ա', 2.0799999237060547), ('զ', 2.0999999046325684), ('գ', 2.2200000286102295), ('ե', 2.3399999141693115), ('ր', 2.379999876022339), ('ի', 2.4600000381469727), ('ց', 2.4800000190734863), (' ', 2.5), ('մ', 2.679999828338623), ('ե', 2.700000047683716), ('կ', 2.8399999141693115), ('ն', 2.93999981880188), (' ', 2.9600000381469727), ('ե', 2.9800000190734863), ('ն', 3.319999933242798))`

### CLI

CLI API took 7 optional parameters: `wav_path`, `beam_width`, `alpha_beta`, `get_metadata`, `spinner`, `vad_aggresivness`, and `wav_save_path`. Descriptions and return values are the same as for Python API. If the `wav_path` parameter is not empty, then the audio file will be transcribed, else microphone streaming will start.

## Install

```
pip install armspeech
```

## Usage examples

### Python

```
#Import library
from armspeech import ArmSpeech_STT

#Create object
armspeech_stt = ArmSpeech_STT()

#Transcribe wav audio file
result = armspeech_stt.from_wav(wav_path = 'path/to/wav/audio', get_metadata = True)
print(result)

#Start microphone streaming
for result in armspeech_stt.from_mic (vad_aggresivness = 2, spinner = True, wav_save_path = 'path/to/transcribed/speeches', get_metadata = False):
    print(result)
```

### CLI

```
armspeech_stt_cli --wav_path path/to/wav/audio --beam_width 2048 --alpha_beta 0.7 1.3 --get_metadata True
```

## Author's profiles

- [GitHub](https://github.com/Varuzhan97)
- [LinkedIn](linkedin.com/in/varuzhan-baghdasaryan-74b064147)
- [Email](www.varuzh2014@gmail.com)

## Acknowledgements

 - [ArmSpeech: Armenian Spoken Language Corpus](https://www.ijscia.com/full-text-volume-3-issue-3-may-jun-2022-454-459/)
 - [Extended ArmSpeech: Armenian Spoken Language Corpus](https://www.ijscia.com/full-text-volume-3-issue-4-jul-aug-2022-573-576/)
 - [Armenian Speech Recognition System: Acoustic and Language Models](https://www.ijscia.com/full-text-volume-3-issue-5-sep-oct-2022-719-724/)
