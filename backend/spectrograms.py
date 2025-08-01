"""
Spectrogram Generation Utilities for Flask Motor Audio Analyzer
Generates six types of spectrograms optimized for motor audio analysis
"""


"""
SciPy-minimal Spectrogram Generator
Reduces SciPy dependency by using alternative implementations
"""

import librosa
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pywt
import base64
from io import BytesIO
import logging
import warnings

warnings.filterwarnings('ignore')
logger = logging.getLogger(__name__)

class SpectrogramGenerator:
    """Generate spectrograms with minimal SciPy usage"""
    
    def __init__(self, figsize=(12, 8), dpi=100):
        self.figsize = figsize
        self.dpi = dpi
    
    def _save_plot_to_base64(self, fig) -> str:
        """Convert matplotlib figure to base64"""
        try:
            buffer = BytesIO()
            fig.savefig(buffer, format='png', dpi=self.dpi, bbox_inches='tight',
                       facecolor='white', edgecolor='none')
            buffer.seek(0)
            img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            plt.close(fig)
            return img_base64
        except Exception as e:
            logger.error(f"Failed to save plot: {e}")
            plt.close(fig)
            raise
    
    def generate_mel_spectrogram(self, audio_data: np.ndarray, sample_rate: int) -> str:
        """Mel-spectrogram using librosa (SciPy-free)"""
        try:
            mel_spec = librosa.feature.melspectrogram(
                y=audio_data, sr=sample_rate, n_mels=128, n_fft=2048,
                hop_length=512, fmin=50, fmax=8000
            )
            mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
            
            fig, ax = plt.subplots(figsize=self.figsize)
            img = librosa.display.specshow(mel_spec_db, x_axis='time', y_axis='mel',
                                          sr=sample_rate, fmin=50, fmax=8000, ax=ax, cmap='viridis')
            ax.set_title('Mel-Spectrogram\n(Energy Distribution Analysis)', fontweight='bold')
            ax.set_xlabel('Time (seconds)')
            ax.set_ylabel('Mel Frequency')
            
            cbar = plt.colorbar(img, ax=ax, format='%+2.0f dB')
            cbar.set_label('Power (dB)', rotation=270, labelpad=15)
            plt.tight_layout()
            
            return self._save_plot_to_base64(fig)
        except Exception as e:
            logger.error(f"Mel-spectrogram generation failed: {e}")
            raise
    
    def generate_cqt(self, audio_data: np.ndarray, sample_rate: int) -> str:
        """CQT using librosa"""
        try:
            cqt = librosa.cqt(audio_data, sr=sample_rate, n_bins=84, bins_per_octave=12,
                             fmin=librosa.note_to_hz('C2'), hop_length=512)
            cqt_db = librosa.amplitude_to_db(np.abs(cqt), ref=np.max)
            
            fig, ax = plt.subplots(figsize=self.figsize)
            img = librosa.display.specshow(cqt_db, x_axis='time', y_axis='cqt_hz',
                                          sr=sample_rate, ax=ax, cmap='plasma')
            ax.set_title('Constant-Q Transform (CQT)\n(Harmonic Analysis)', fontweight='bold')
            ax.set_xlabel('Time (seconds)')
            ax.set_ylabel('Frequency (Hz)')
            
            cbar = plt.colorbar(img, ax=ax, format='%+2.0f dB')
            cbar.set_label('Magnitude (dB)', rotation=270, labelpad=15)
            plt.tight_layout()
            
            return self._save_plot_to_base64(fig)
        except Exception as e:
            logger.error(f"CQT generation failed: {e}")
            raise
    
    def generate_log_stft(self, audio_data: np.ndarray, sample_rate: int) -> str:
        """Log-STFT using librosa"""
        try:
            stft = librosa.stft(audio_data, n_fft=4096, hop_length=1024, window='hann')
            stft_db = librosa.amplitude_to_db(np.abs(stft), ref=np.max)
            
            fig, ax = plt.subplots(figsize=self.figsize)
            img = librosa.display.specshow(stft_db, x_axis='time', y_axis='log',
                                          sr=sample_rate, ax=ax, cmap='inferno')
            ax.set_title('Log-STFT Spectrogram\n(Low-Frequency Analysis)', fontweight='bold')
            ax.set_xlabel('Time (seconds)')
            ax.set_ylabel('Frequency (Hz, log scale)')
            ax.set_ylim([50, sample_rate/2])
            
            cbar = plt.colorbar(img, ax=ax, format='%+2.0f dB')
            cbar.set_label('Magnitude (dB)', rotation=270, labelpad=15)
            plt.tight_layout()
            
            return self._save_plot_to_base64(fig)
        except Exception as e:
            logger.error(f"Log-STFT generation failed: {e}")
            raise
    
    def generate_wavelet_scalogram(self, audio_data: np.ndarray, sample_rate: int) -> str:
        """Wavelet scalogram using PyWavelets"""
        try:
            # Use simple decimation instead of scipy.signal.decimate
            if len(audio_data) > 20000:
                downsample_factor = len(audio_data) // 20000
                audio_data = audio_data[::downsample_factor]  # Simple downsampling
                effective_sr = sample_rate // downsample_factor
            else:
                effective_sr = sample_rate
            
            scales = np.logspace(0.5, 3.5, 50)
            wavelet = 'cmor1.5-1.0'
            
            coefficients, frequencies = pywt.cwt(audio_data, scales, wavelet, 1/effective_sr)
            power = np.abs(coefficients) ** 2
            power_db = 10 * np.log10(power + np.finfo(float).eps)
            
            fig, ax = plt.subplots(figsize=self.figsize)
            time = np.linspace(0, len(audio_data)/effective_sr, len(audio_data))
            
            img = ax.imshow(power_db, extent=[0, time[-1], frequencies[0], frequencies[-1]], 
                           cmap='magma', aspect='auto', origin='lower', interpolation='bilinear')
            
            ax.set_title('Wavelet Scalogram\n(Transient Analysis)', fontweight='bold')
            ax.set_xlabel('Time (seconds)')
            ax.set_ylabel('Frequency (Hz)')
            ax.set_yscale('log')
            
            cbar = plt.colorbar(img, ax=ax)
            cbar.set_label('Power (dB)', rotation=270, labelpad=15)
            plt.tight_layout()
            
            return self._save_plot_to_base64(fig)
        except Exception as e:
            logger.error(f"Wavelet scalogram generation failed: {e}")
            raise
    
    def generate_spectral_kurtosis(self, audio_data: np.ndarray, sample_rate: int) -> str:
        """Spectral kurtosis using NumPy instead of scipy.stats"""
        try:
            # Simple STFT using NumPy
            nperseg = 2048
            noverlap = 1536
            hop_length = nperseg - noverlap
            
            # Manual STFT calculation
            stft = librosa.stft(audio_data, n_fft=nperseg, hop_length=hop_length, window='hann')
            f = librosa.fft_frequencies(sr=sample_rate, n_fft=nperseg)
            t = librosa.frames_to_time(np.arange(stft.shape[1]), sr=sample_rate, hop_length=hop_length)
            
            stft_magnitude = np.abs(stft)
            spectral_kurt = np.zeros_like(stft_magnitude)
            
            # Calculate kurtosis manually
            for freq_bin in range(stft_magnitude.shape[0]):
                if stft_magnitude.shape[1] > 3:
                    time_series = stft_magnitude[freq_bin, :]
                    if np.std(time_series) > 0:
                        # Manual kurtosis calculation
                        mean_val = np.mean(time_series)
                        std_val = np.std(time_series)
                        normalized = (time_series - mean_val) / std_val
                        spectral_kurt[freq_bin, :] = np.mean(normalized**4) - 3
            
            fig, ax = plt.subplots(figsize=self.figsize)
            img = ax.pcolormesh(t, f, spectral_kurt, shading='gouraud', cmap='RdYlBu_r',
                               vmin=np.percentile(spectral_kurt, 5),
                               vmax=np.percentile(spectral_kurt, 95))
            
            ax.set_title('Spectral Kurtosis\n(Impulse Detection)', fontweight='bold')
            ax.set_xlabel('Time (seconds)')
            ax.set_ylabel('Frequency (Hz)')
            ax.set_ylim([0, min(8000, sample_rate/2)])
            
            cbar = plt.colorbar(img, ax=ax)
            cbar.set_label('Kurtosis', rotation=270, labelpad=15)
            plt.tight_layout()
            
            return self._save_plot_to_base64(fig)
        except Exception as e:
            logger.error(f"Spectral kurtosis generation failed: {e}")
            raise
    
    def generate_modulation_spectrogram(self, audio_data: np.ndarray, sample_rate: int) -> str:
        """Modulation spectrogram using NumPy FFT"""
        try:
            stft = librosa.stft(audio_data, n_fft=2048, hop_length=512, window='hann')
            magnitude = np.abs(stft)
            
            # Simple smoothing using NumPy
            from scipy import ndimage
            try:
                magnitude_smooth = ndimage.gaussian_filter(magnitude, sigma=[0, 1])
            except ImportError:
                # Fallback: simple averaging filter
                magnitude_smooth = np.copy(magnitude)
                for i in range(1, magnitude_smooth.shape[1]-1):
                    magnitude_smooth[:, i] = (magnitude[:, i-1] + magnitude[:, i] + magnitude[:, i+1]) / 3
            
            mod_spec = np.zeros((magnitude_smooth.shape[0], magnitude_smooth.shape[1]//2))
            
            for freq_bin in range(magnitude_smooth.shape[0]):
                if magnitude_smooth.shape[1] > 1:
                    time_series = magnitude_smooth[freq_bin, :] - np.mean(magnitude_smooth[freq_bin, :])
                    # Apply simple window
                    window = np.hanning(len(time_series))
                    time_series = time_series * window
                    # FFT
                    mod_fft = np.fft.fft(time_series)
                    mod_spec[freq_bin, :] = np.abs(mod_fft[:mod_spec.shape[1]])
            
            mod_spec_db = librosa.amplitude_to_db(mod_spec + np.finfo(float).eps, ref=np.max)
            
            fig, ax = plt.subplots(figsize=self.figsize)
            modulation_freqs = np.fft.fftfreq(magnitude_smooth.shape[1], d=512/sample_rate)[:mod_spec.shape[1]]
            acoustic_freqs = librosa.fft_frequencies(sr=sample_rate, n_fft=2048)
            
            mod_freq_limit = 50
            mod_indices = modulation_freqs <= mod_freq_limit
            
            img = ax.imshow(mod_spec_db[:, mod_indices], 
                           extent=[0, mod_freq_limit, acoustic_freqs[-1], acoustic_freqs[0]], 
                           cmap='hot', aspect='auto', origin='upper', interpolation='bilinear')
            
            ax.set_title('Modulation Spectrogram\n(Sideband Analysis)', fontweight='bold')
            ax.set_xlabel('Modulation Frequency (Hz)')
            ax.set_ylabel('Acoustic Frequency (Hz)')
            ax.set_ylim([50, min(8000, sample_rate/2)])
            
            cbar = plt.colorbar(img, ax=ax)
            cbar.set_label('Magnitude (dB)', rotation=270, labelpad=15)
            plt.tight_layout()
            
            return self._save_plot_to_base64(fig)
        except Exception as e:
            logger.error(f"Modulation spectrogram generation failed: {e}")
            raise
