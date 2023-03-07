import os
import stt
import wave
import numpy as np
import collections, queue
import pyaudio
import webrtcvad
from halo import Halo
from datetime import datetime

class ArmSpeech_STT:
    def __init__(self):

        current_dir = os.path.dirname(os.path.realpath(__file__))

        model_path = os.path.join(current_dir, 'model', 'model.tflite')
        #scorer_path = os.path.join(current_dir, 'model', 'model.scorer')

        self.__model = stt.Model(model_path)
        #self.__model.enableExternalScorer(scorer_path)

        self.__rate = 16000
        self.__channels = 1
        self.__buffer_queue = queue.Queue()

    def set_beam_width(self, beam_width: int) -> int:
        return self.__model.setBeamWidth(beam_width)

    def set_scorer_alpha_beta(self, alpha: float, beta: float) -> int:
        return self.__model.setScorerAlphaBeta(alpha, beta)

    def __convert_wav(self, wav_path: str) -> np.array:
        audio_data = wave.open(wav_path, 'rb')
        sample_rate = audio_data.getframerate()

        if sample_rate != self.__rate:
            print("Warning: original sample rate ({}) is different than {}hz. Resampling might produce erratic speech recognition.".format(sample_rate, self.__rate))

        audio = np.frombuffer(audio_data.readframes(audio_data.getnframes()), np.int16)
        return audio

    def __write_wav(self, filename: str, data: bytearray) -> None:
        wf = wave.open(filename, 'wb')
        wf.setnchannels(self.__channels)
        wf.setsampwidth(2)
        wf.setframerate(self.__rate)
        wf.writeframes(data)
        wf.close()

    def __render(self, metadata: stt.Metadata) -> list:
        transcripts = metadata.transcripts
        tokens = transcripts[0].tokens

        confidence = transcripts[0].confidence
        transcript = "".join((str(item.text) for item in tokens))

        result = ()
        result += (transcript,)
        result += (confidence,)

        timestamp = ()
        for i in tokens:
            timestamp += ((i.text, i.start_time,),)

        result += (timestamp)

        return result

    def from_wav(self, wav_path: str, get_metadata: bool = False) -> str:
        audio = self.__convert_wav(wav_path)

        if get_metadata:
            result = self.__model.sttWithMetadata(audio)
            if result != '':
                result = self.__render(result)
        else:
            result = self.__model.stt(audio)

        return result

    def __proxy_callback(self, in_data, frame_count, time_info, status) -> tuple:
        #pylint: disable=unused-argument
        self.__buffer_queue.put(in_data)
        return (None, pyaudio.paContinue)


    def __vad_collector(self, aggressivness, block_size, padding_ms=300, ratio=0.75):
        """Generator that yields series of consecutive audio frames comprising each utterence, separated by yielding a single None.
            Determines voice activity by ratio of frames in padding_ms. Uses a buffer to include padding_ms prior to being triggered.
            Example: (frame, ..., frame, None, frame, ..., frame, None, ...)
                      |---utterence---|        |---utterence---|
        """

        vad = webrtcvad.Vad(aggressivness)

        num_padding_frames = padding_ms // (1000 * block_size // self.__rate)
        ring_buffer = collections.deque(maxlen=num_padding_frames)
        triggered = False

        while 1:
            frame = self.__buffer_queue.get()
            if len(frame) < 640:
                return

            is_speech = vad.is_speech(frame, self.__rate)
            if not triggered:
                ring_buffer.append((frame, is_speech))
                num_voiced = len([f for f, speech in ring_buffer if speech])
                if num_voiced > ratio * ring_buffer.maxlen:
                    triggered = True
                    for f, s in ring_buffer:
                        yield f
                    ring_buffer.clear()
            else:
                yield frame
                ring_buffer.append((frame, is_speech))
                num_unvoiced = len([f for f, speech in ring_buffer if not speech])
                if num_unvoiced > ratio * ring_buffer.maxlen:
                    triggered = False
                    yield None
                    ring_buffer.clear()

    def from_mic(self, vad_aggresivness: int = 3, spinner: bool = False, wav_save_path: str = None, get_metadata = False):
        format = pyaudio.paInt16
        blocks_per_second = 50
        block_size = int(self.__rate / float(blocks_per_second))
        block_size_input = int(self.__rate / float(blocks_per_second))

        kwargs = {
            'format': format,
            'channels': self.__channels,
            'rate': self.__rate,
            'input': True,
            'frames_per_buffer': block_size_input,
            'stream_callback': self.__proxy_callback,
        }

        stream_context = self.__model.createStream()

        pa = pyaudio.PyAudio()
        stream = pa.open(**kwargs)
        stream.start_stream()
        if spinner: spinner = Halo(spinner='bouncingBall')

        wav_data = bytearray()

        try:
            for frame in self.__vad_collector(vad_aggresivness, block_size):
                if frame is not None:
                    if spinner: spinner.start()
                    stream_context.feedAudioContent(np.frombuffer(frame, np.int16))
                    if wav_save_path is not None: wav_data.extend(frame)
                else:
                    if spinner: spinner.stop()

                    if wav_save_path is not None:
                        self.__write_wav(os.path.join(wav_save_path, datetime.now().strftime("savewav_%Y-%m-%d_%H-%M-%S_%f.wav")), wav_data)
                        wav_data = bytearray()

                    stream.stop_stream()

                    if get_metadata:
                        result = stream_context.finishStreamWithMetadata()
                        if result != '':
                            result = self.__render(result)
                    else:
                        result = stream_context.finishStream()

                    yield result

                    stream.start_stream()
                    stream_context = self.__model.createStream()

        except Exception:
            print('Exception raised while streaming from the microphone.')
        finally:
            if not stream.is_stopped():
                stream.stop_stream()
            stream.close()
            pa.terminate()
            return
