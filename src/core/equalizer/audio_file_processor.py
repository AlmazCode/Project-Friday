from collections import deque
import numpy as np
import pygame
import os

from modules.console import Console


class AudioFileProcessor:
    """
    Manages loading, playback, and real-time FFT analysis of audio files.

    This class is designed for applications (e.g., games or music players)
    that require frequency spectrum data from the currently playing audio
    for visualization purposes.

    It uses a `deque` to manage a playlist, `pygame.mixer` for playback,
    and `numpy` for FFT calculations.

    Key Features:
    - Queued playback.
    - Manual, but accurate playback time tracking (with pause handling).
    - Real-time FFT calculation.
    - Multiple layers of spectrum data smoothing.

    Attributes:
        NUM_BANDS (int): The target number of frequency bands for the analyzer.
        SMOOTHING_FACTOR (float): Smoothing factor (0.0-1.0) for the 
                                  exponential moving average.
        DECAY_RATE (float): The rate (0.0-1.0) at which "peak"
                            frequency values decay.
        HISTORY_LEN (int): The number of FFT frames to average to 
                           stabilize the output.
        FFT_CHUNK_SIZE (int): The window size (in samples) for a single
                              FFT calculation.
        GAIN (int): A multiplier to boost the FFT signal before normalization.
    """

    def __init__(self, num_bands=32):
        """
        Initializes the AudioFileProcessor.

        Args:
            num_bands (int): The number of frequency bands to split the
                             spectrum into. Defaults to 32.
        """
        # --- Tweakables ---
        self.NUM_BANDS: int = num_bands
        self.SMOOTHING_FACTOR: float = 0.7  # (0.0-1.0) Smoothing. Closer to 1.0 = slower
        self.DECAY_RATE: float = 0.95     # (0.0-1.0) Decay rate for "peaks"
        self.HISTORY_LEN: int = 5         # (int) N frames for smoothing
        self.FFT_CHUNK_SIZE: int = 4096   # FFT window size
        self.GAIN: int = 200              # Signal gain

        # --- Queue State ---
        self.queue: deque = deque()
        self.audio_file: str | None = None  # Path to the current file (for deletion)

        # --- Playback State (managed manually) ---
        self.playing: bool = False
        self.paused: bool = False
        self.start_time_ms: int = 0       # (ticks) Start time of the last play/unpause
        self.elapsed_at_pause: int = 0    # (ms) How much time elapsed before pausing

        # --- Pygame & Audio Data ---
        self.sound: pygame.mixer.Sound | None = None
        self.channel: pygame.mixer.Channel | None = None
        self.audio_data: np.ndarray | None = None
        self.sample_rate: int = 0
        self.channels: int = 0
        self.total_samples: int = 0
        self.duration: float = 0.0

        # --- FFT & Smoothing Data ---
        self.fft_window: np.ndarray | None = None
        self.freq_history: deque = deque(maxlen=self.HISTORY_LEN)
        self.current_frequencies: np.ndarray = np.zeros(self.NUM_BANDS)
        self.peak_frequencies: np.ndarray = np.zeros(self.NUM_BANDS)

        # Ensure all state variables are reset
        self._reset_track_state()


    def _reset_track_state(self):
        """
        (Internal) Resets all track-specific variables to their
        default values.
        """
        if self.channel:
            self.channel.stop()

        self.sound = None
        self.channel = None
        self.audio_data = None
        self.sample_rate = 0
        self.channels = 0
        self.total_samples = 0
        self.duration = 0.0
        
        # Reset player state
        self.playing = False
        self.paused = False
        self.start_time_ms = 0
        self.elapsed_at_pause = 0
        
        # Reset FFT state
        self.fft_window = np.hanning(self.FFT_CHUNK_SIZE)
        self.freq_history = deque(maxlen=self.HISTORY_LEN)
        self.current_frequencies = np.zeros(self.NUM_BANDS)
        self.peak_frequencies = np.zeros(self.NUM_BANDS)
        
    def _calculate_fft(self, time_seconds: float) -> np.ndarray:
        """
        Calculates the FFT for a given timestamp.

        It extracts a chunk of audio data, applies a Hanning window,
        performs an rFFT, groups frequencies into bins,
        and normalizes the result.

        Args:
            time_seconds (float): The current playback position in seconds.

        Returns:
            np.ndarray: A normalized array of `self.NUM_BANDS`
                        frequency values (from 0.0 to 1.0).
        """
        if self.audio_data is None:
            return np.zeros(self.NUM_BANDS)

        # 1. Determine the chunk center
        current_sample = int(time_seconds * self.sample_rate)
        
        # 2. Calculate chunk boundaries
        start = max(0, current_sample - self.FFT_CHUNK_SIZE // 2)
        end = min(self.total_samples, current_sample + self.FFT_CHUNK_SIZE // 2)
        chunk = self.audio_data[start:end]

        # 3. Pad with zeros if the chunk is at the file edge (start or end)
        if len(chunk) < self.FFT_CHUNK_SIZE:
            pad_len = self.FFT_CHUNK_SIZE - len(chunk)
            # Pad with zeros on the right
            chunk = np.pad(chunk, (0, pad_len), 'constant')

        # 4. Apply a Hanning window to smooth the edges
        chunk = chunk * self.fft_window

        # 5. Perform FFT (rfft for real signals)
        fft_raw = np.fft.rfft(chunk)
        fft_magnitude = np.abs(fft_raw)

        # 6. Binning (grouping) frequencies
        
        # Define bin edges linearly across the FFT *indices*.
        # This naturally creates logarithmic-like bins
        # (more resolution for lower frequencies).
        max_freq_index = len(fft_magnitude)
        bin_edges = np.linspace(0, max_freq_index, self.NUM_BANDS + 1).astype(int)
        
        binned_spectrum = np.zeros(self.NUM_BANDS)
        
        for i in range(self.NUM_BANDS):
            start_idx = bin_edges[i]
            end_idx = bin_edges[i+1]
            if start_idx == end_idx:
                binned_spectrum[i] = 0
            else:
                # Average the values within the bin
                binned_spectrum[i] = np.mean(fft_magnitude[start_idx:end_idx])

        # 7. Scaling and Normalization
        binned_spectrum += 1e-9  # Avoid log(0) if using a log scale later
        
        # Scale with gain and window size
        scaled_spectrum = binned_spectrum * (self.GAIN / self.FFT_CHUNK_SIZE)
        
        # Apply square root to "compress" the dynamic range
        # (closer to how we perceive loudness)
        processed_spectrum = np.sqrt(scaled_spectrum)
        
        # Clip values between 0.0 and 1.0
        normalized_spectrum = np.clip(processed_spectrum, 0, 1)

        return normalized_spectrum

    def _get_current_time_ms(self) -> int:
        """
        Returns the current playback position in milliseconds.

        This method manually tracks time, accounting for pauses.
        Returns -1 if playback is stopped or finished.

        Returns:
            int: The current position in ms, or -1.
        """
        # 1. If not playing (stopped), return -1
        if not self.playing:
            return -1

        # 2. If paused, return the "frozen" time
        if self.paused:
            return self.elapsed_at_pause

        # 3. If playing, calculate: (time_before_pause + (current_time - start_time))
        current_elapsed = self.elapsed_at_pause + (pygame.time.get_ticks() - self.start_time_ms)
        
        # 4. Check if the track has finished
        if current_elapsed / 1000.0 > self.duration:
            return -1
            
        return current_elapsed

    def process(self) -> np.ndarray:
        """
        The main update method. Should be called every frame of the game loop.

        It gets the current time, calculates the FFT, and applies smoothing.
        It also handles automatically playing the next track in the queue.

        Returns:
            np.ndarray: An array of `self.NUM_BANDS` smoothed frequency values.
        """
        current_pos_ms = self._get_current_time_ms()
        frequencies = np.zeros(self.NUM_BANDS)

        if current_pos_ms < 0:
            # Time is up (track ended) or the player is stopped
            if self.playing:
                # The track just finished
                self.stop()
                if self.queue:
                    self.get_next_audio_file()
                    self.play()
            
            # If not playing, just return zeros
            frequencies = np.zeros(self.NUM_BANDS)

        else:
            # Music is playing, generate the spectrum
            time_seconds = current_pos_ms / 1000.0
            frequencies = self._calculate_fft(time_seconds)

        # --- Smoothing ---

        # 1. History smoothing (averaging the last N frames)
        self.freq_history.append(frequencies)
        history_smoothed = np.mean(list(self.freq_history), axis=0)
        
        # 2. Peaks (for "sticky" visualizer peaks)
        self.peak_frequencies = np.maximum(
            self.peak_frequencies * self.DECAY_RATE,
            history_smoothed
        )

        # 3. Exponential moving average (for smooth animation)
        self.current_frequencies = (
            self.SMOOTHING_FACTOR * self.current_frequencies +
            (1 - self.SMOOTHING_FACTOR) * history_smoothed
        )

        return self.current_frequencies

    def get_duration(self) -> float:
        """Returns the total duration of the current audio in seconds."""
        return self.duration

    def get_current_position(self) -> float:
        """Returns the current playback position in seconds."""
        pos_ms = self._get_current_time_ms()
        if pos_ms < 0:
            return 0.0
        return pos_ms / 1000.0

    def add_audio(self, audio_file: str) -> None:
        """
        Adds an audio file to the playback queue.

        If nothing is currently playing, it immediately loads this file.

        Args:
            audio_file (str): The path to the audio file.
        """
        self.queue.append(audio_file)

        # If the player is idle, load this track
        if not self.playing and self.sound is None:
            self.get_next_audio_file()

    def get_next_audio_file(self) -> None:
        """
        Loads the next audio file from the queue.

        This method does all the "heavy lifting":
        - Loads the Sound
        - Extracts audio data into an `np.ndarray`
        - Converts to mono
        - Normalizes the data
        - Resets all player and FFT states.
        """
        if not self.queue:
            Console.warning("Queue is empty. Nothing to load.")
            return

        # First, reset all previous states
        self._reset_track_state()

        audio_file_path = self.queue.popleft()

        try:
            self.sound = pygame.mixer.Sound(audio_file_path)
            self.audio_file = audio_file_path
        except pygame.error as e:
            Console.error(f"AudioFileProcessor: Error loading audio: {e}")
            return

        self.duration = self.sound.get_length()

        # Get mixer parameters
        freq, _, channels = pygame.mixer.get_init()
        self.sample_rate = freq
        self.channels = channels

        try:
            # Convert the sound to a NumPy array
            raw_array = pygame.sndarray.array(self.sound)
        except ValueError:
            Console.error("AudioFileProcessor: sndarray error. Ensure NumPy is installed.")
            return

        # Convert to mono (by averaging channels) and normalize
        if self.channels == 2:
            self.audio_data = np.mean(raw_array, axis=1)
        else:
            self.audio_data = raw_array
        
        # Normalize 16-bit audio (from -32768 to 32767) to the range [-1.0, 1.0]
        self.audio_data = self.audio_data.astype(np.float32) / 32767.0
        self.total_samples = len(self.audio_data)


    def play(self, loops=0):
        """
        Starts playback of the currently loaded track.

        If a track is already playing, this does nothing.

        Args:
            loops (int): Number of repeats (0 = play 1 time).
        """
        if self.playing:
            Console.warning("AudioFileProcessor: Already playing, 'play' command ignored.")
            return
            
        if not self.sound:
            Console.error("AudioFileProcessor: Nothing to play. Add audio first.")
            return
            
        self.channel = self.sound.play(loops)
        self.playing = True
        self.paused = False
        self.start_time_ms = pygame.time.get_ticks()
        self.elapsed_at_pause = 0


    def stop(self):
        """
        Completely stops playback and resets the state.

        Also deletes the associated audio file (assuming it's temporary).
        """
        if self.channel:
            self.channel.stop()
            
        self.playing = False
        self.paused = False
        self.channel = None
        self.start_time_ms = 0
        self.elapsed_at_pause = 0

        # IMPORTANT: This block deletes the file.
        if self.audio_file is not None:
            try:
                os.remove(self.audio_file)
                self.audio_file = None
            except OSError as e:
                Console.error(f"AudioFileProcessor: Failed to remove file {self.audio_file} on stop: {e}")
        
        # Reset FFT data
        self.freq_history.clear()
        self.current_frequencies.fill(0)
        self.peak_frequencies.fill(0)
        
        # Reset the sound, but not the queue
        self.sound = None 
        self.audio_data = None