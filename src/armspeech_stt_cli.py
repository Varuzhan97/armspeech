import argparse
from .armspeech import ArmSpeech_STT

def main() -> None:
    parser = argparse.ArgumentParser(description='ArmSpeech is an offline Armenian speech recognition library (speech-to-text) and CLI tool based on Coqui STT (🐸STT) (https://stt.readthedocs.io/en/latest/) and trained on ArmSpeech dataset (https://www.ijscia.com/full-text-volume-3-issue-3-may-jun-2022-454-459/, https://www.ijscia.com/full-text-volume-3-issue-4-jul-aug-2022-573-576/).')

    parser.add_argument('--wav_path', default = None, type = str,
                        help='The absolute path of wav audio file to be transcribed. The type is string, the default value is none.')

    parser.add_argument('--beam_width', default = None, type = int,
                        help='Set the beam width value of the model (beam width used in the CTC decoder when building candidate transcriptions). A larger beam width value generates better results but increases decoding time. The type is integer, the default value is 1024.')

    parser.add_argument('--alpha_beta', default = None, nargs='+', type=float,
                        help='Set hyperparameters alpha and beta of the external scorer (language model weight (`alpha`) and word insertion weight (`beta`) of the decoder. Both are floats, the default values are 0.931289039105002 for the `alpha` and 1.1834137581510284 for the `beta`.')

    parser.add_argument('--get_metadata', default = False, type = bool,
                        help='Enable/Disable getting confidence, transcript, and each word, along with its timing information. The type is boolean, the default value is false.')

    parser.add_argument('--spinner', default = False, type = bool,
                        help='Enable/disable the spinner (`spinner`) in the console while detected voice activity. The type is boolean, the default value is false.')

    parser.add_argument('--vad_aggresivness', default = 3, type = int,
                        help='An integer number in a range of [0, 3] for voice activity detection aggressiveness while streaming from the microphone. The type is integer, the default value is 3.')

    parser.add_argument('--wav_save_path', default = None, type = str,
                        help='An absolute path to save wav files during streaming from the microphone. The type is string, the default value is none.')

    args = parser.parse_args()

    armspeech_stt = ArmSpeech_STT()

    if args.beam_width is not None:
        armspeech_stt.set_beam_width(args.beam_width)

    if args.alpha_beta is not None:
        alpha_beta = tuple(args.alpha_beta)
        armspeech_stt.set_scorer_alpha_beta(alpha_beta[0], alpha_beta[1])

    if args.wav_path is None:
        for result in armspeech_stt.from_mic(vad_aggresivness = args.vad_aggresivness, spinner = args.spinner, wav_save_path = args.wav_save_path, get_metadata = args.get_metadata):
            print(result)
    else:
        result = armspeech_stt.from_wav(wav_path = args.wav_path, get_metadata = args.get_metadata)
        print(result)

if __name__ == "__main__":
    main()
