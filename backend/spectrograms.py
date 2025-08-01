"""
Spectrogram Generation Utilities for Flask Motor Audio Analyzer
Generates six types of spectrograms optimized for motor audio analysis
"""

import librosa
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from scipy import signal
from scipy.stats import kurtosis
import pywt
import base64
from io import BytesIO
import logging
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class SpectrogramGenerator:
    """Generate various spectrograms optimized for motor audio analysis"""
    
    def __init__(self, figsize=(12, 8), dpi=100):
        self.figsize = figsize
        self.dpi = dpi
        
        # Set consistent matplotlib style
        plt.style.use('default')
        matplotlib.rcParams.update({
            'font.size': 10,
            'axes.titlesize': 12,
            'axes.labelsize': 10,
            'xtick.labelsize': 9,
            'ytick.labelsize': 9,
            'figure.titlesize': 14
        })
    
    def _save_plot_to_base64(self, fig) -> str:
        """Convert matplotlib figure to base64 string for web display"""
        try:
            buffer = BytesIO()
            fig.savefig(buffer, 
                       format='png', 
                       dpi=self.dpi, 
                       bbox_inches='tight',
                       facecolor='white',
                       edgecolor='none')
            buffer.seek(0)
            img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            plt.close(fig)
            return img_base64
        except Exception as e:
            logger.error(f"Failed to save plot to base64: {e}")
            plt.close(fig)
            raise
    
    def generate_mel_spectrogram(self, audio_data: np.ndarray, sample_rate: int) -> str:
        """
        Generate Mel-spectrogram
        Optimal for: Energy imbalance, tonal shifts, soft degradation detection
        """
        try:
            # Compute mel-spectrogram with optimized parameters
            mel_spec = librosa.feature.melspectrogram(
                y=audio_data, 
                sr=sample_rate,
                n_mels=128,           # Good resolution for motor analysis
                n_fft=2048,           # Window size
                hop_length=512,       # Overlap
                fmin=50,              # Minimum frequency (exclude very low noise)
                fmax=8000             # Maximum frequency (motors typically <8kHz)
            )
            
            # Convert to dB scale
            mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
            
            # Create plot
            fig, ax = plt.subplots(figsize=self.figsize)
            img = librosa.display.specshow(
                mel_spec_db, 
                x_axis='time', 
                y_axis='mel', 
                sr=sample_rate,
                fmin=50,
                fmax=8000,
                ax=ax,
                cmap='viridis'
            )
            
            ax.set_title('Mel-Spectrogram\n(Energy Distribution Analysis)', fontweight='bold')
            ax.set_xlabel('Time (seconds)')
            ax.set_ylabel('Mel Frequency')
            
            # Add colorbar
            cbar = plt.colorbar(img, ax=ax, format='%+2.0f dB')
            cbar.set_label('Power (dB)', rotation=270, labelpad=15)
            
            plt.tight_layout()
            return self._save_plot_to_base64(fig)
            
        except Exception as e:
            logger.error(f"Mel-spectrogram generation failed: {e}")
            raise
    
    def generate_cqt(self, audio_data: np.ndarray, sample_rate: int) -> str:
        """
        Generate Constant-Q Transform spectrogram
        Optimal for: Harmonic noise detection, shifted frequency content analysis
        """
        try:
            # Compute CQT with logarithmic frequency resolution
            cqt = librosa.cqt(
                audio_data, 
                sr=sample_rate, 
                n_bins=84,              # 7 octaves * 12 bins per octave
                bins_per_octave=12,     # Musical semitone resolution
                fmin=librosa.note_to_hz('C2'),  # Start from C2 (~65Hz)
                hop_length=512
            )
            
            # Convert to dB scale
            cqt_db = librosa.amplitude_to_db(np.abs(cqt), ref=np.max)
            
            # Create plot
            fig, ax = plt.subplots(figsize=self.figsize)
            img = librosa.display.specshow(
                cqt_db, 
                x_axis='time', 
                y_axis='cqt_hz',
                sr=sample_rate,
                ax=ax,
                cmap='plasma'
            )
            
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
        """
        Generate Log-STFT spectrogram
        Optimal for: Low-frequency rumble detection (imbalance/looseness)
        """
        try:
            # Compute STFT with parameters optimized for low-frequency analysis
            stft = librosa.stft(
                audio_data, 
                n_fft=4096,           # Larger window for better low-freq resolution
                hop_length=1024,      # Less overlap for efficiency
                window='hann'
            )
            
            # Convert to dB scale
            stft_db = librosa.amplitude_to_db(np.abs(stft), ref=np.max)
            
            # Create plot with logarithmic frequency scale
            fig, ax = plt.subplots(figsize=self.figsize)
            img = librosa.display.specshow(
                stft_db, 
                x_axis='time', 
                y_axis='log',
                sr=sample_rate,
                ax=ax,
                cmap='inferno'
            )
            
            ax.set_title('Log-STFT Spectrogram\n(Low-Frequency Rumble Detection)', fontweight='bold')
            ax.set_xlabel('Time (seconds)')
            ax.set_ylabel('Frequency (Hz, log scale)')
            ax.set_ylim([50, sample_rate/2])  # Focus on relevant frequency range
            
            cbar = plt.colorbar(img, ax=ax, format='%+2.0f dB')
            cbar.set_label('Magnitude (dB)', rotation=270, labelpad=15)
            
            plt.tight_layout()
            return self._save_plot_to_base64(fig)
            
        except Exception as e:
            logger.error(f"Log-STFT generation failed: {e}")
            raise
    
    def generate_wavelet_scalogram(self, audio_data: np.ndarray, sample_rate: int) -> str:
        """
        Generate Wavelet Scalogram using Continuous Wavelet Transform
        Optimal for: Transient spike detection, short burst analysis
        """
        try:
            # Downsample for computational efficiency if needed
            if len(audio_data) > 20000:  # ~1 second at 22kHz
                downsample_factor = len(audio_data) // 20000
                audio_data = signal.decimate(audio_data, downsample_factor, zero_phase=True)
                effective_sr = sample_rate // downsample_factor
            else:
                effective_sr = sample_rate
            
            # Define scales for CWT (corresponding to different frequencies)
            scales = np.logspace(0.5, 3.5, 50)  # Logarithmic scale distribution
            wavelet = 'cmor1.5-1.0'  # Complex Morlet wavelet for good time-frequency resolution
            
            # Compute CWT
            coefficients, frequencies = pywt.cwt(audio_data, scales, wavelet, 1/effective_sr)
            
            # Convert to power and dB scale
            power = np.abs(coefficients) ** 2
            power_db = 10 * np.log10(power + np.finfo(float).eps)
            
            # Create plot
            fig, ax = plt.subplots(figsize=self.figsize)
            time = np.linspace(0, len(audio_data)/effective_sr, len(audio_data))
            
            # Create time-frequency plot
            img = ax.imshow(
                power_db, 
                extent=[0, time[-1], frequencies[0], frequencies[-1]], 
                cmap='magma', 
                aspect='auto',
                origin='lower',
                interpolation='bilinear'
            )
            
            ax.set_title('Wavelet Scalogram\n(Transient Spike Analysis)', fontweight='bold')
            ax.set_xlabel('Time (seconds)')
            ax.set_ylabel('Frequency (Hz)')
            ax.set_yscale('log')
            
            cbar = plt.colorbar(img, ax=ax, label='Power (dB)')
            cbar.set_label('Power (dB)', rotation=270, labelpad=15)
            
            plt.tight_layout()
            return self._save_plot_to_base64(fig)
            
        except Exception as e:
            logger.error(f"Wavelet scalogram generation failed: {e}")
            raise
    
    def generate_spectral_kurtosis(self, audio_data: np.ndarray, sample_rate: int) -> str:
        """
        Generate Spectral Kurtosis spectrogram
        Optimal for: Impulse detection, sudden power shift analysis
        """
        try:
            # Compute STFT
            f, t, stft = signal.stft(
                audio_data, 
                fs=sample_rate, 
                nperseg=2048,
                noverlap=1536,
                window='hann'
            )
            
            # Compute spectral kurtosis
            stft_magnitude = np.abs(stft)
            spectral_kurt = np.zeros_like(stft_magnitude)
            
            # Calculate kurtosis for each frequency bin across time
            for freq_bin in range(stft_magnitude.shape[0]):
                if stft_magnitude.shape[1] > 3:  # Need minimum samples for kurtosis
                    time_series = stft_magnitude[freq_bin, :]
                    if np.std(time_series) > 0:  # Avoid division by zero
                        spectral_kurt[freq_bin, :] = kurtosis(time_series, axis=None)
            
            # Create plot
            fig, ax = plt.subplots(figsize=self.figsize)
            img = ax.pcolormesh(
                t, f, spectral_kurt, 
                shading='gouraud', 
                cmap='RdYlBu_r',
                vmin=np.percentile(spectral_kurt, 5),
                vmax=np.percentile(spectral_kurt, 95)
            )
            
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
        """
        Generate Modulation Spectrogram
        Optimal for: Sideband modulation detection (winding faults)
        """
        try:
            # Compute STFT first
            stft = librosa.stft(audio_data, n_fft=2048, hop_length=512, window='hann')
            magnitude = np.abs(stft)
            
            # Apply temporal smoothing to reduce noise
            from scipy import ndimage
            magnitude_smooth = ndimage.gaussian_filter(magnitude, sigma=[0, 1])
            
            # Compute modulation spectrogram
            mod_spec = np.zeros((magnitude_smooth.shape[0], magnitude_smooth.shape[1]//2))
            
            for freq_bin in range(magnitude_smooth.shape[0]):
                if magnitude_smooth.shape[1] > 1:
                    # Take FFT along time axis for each frequency bin
                    time_series = magnitude_smooth[freq_bin, :]
                    
                    # Remove DC component
                    time_series = time_series - np.mean(time_series)
                    
                    # Apply window to reduce spectral leakage
                    window = signal.windows.hann(len(time_series))
                    time_series = time_series * window
                    
                    # Compute FFT
                    mod_fft = np.fft.fft(time_series)
                    mod_spec[freq_bin, :] = np.abs(mod_fft[:mod_spec.shape[1]])
            
            # Convert to dB scale
            mod_spec_db = librosa.amplitude_to_db(mod_spec + np.finfo(float).eps, ref=np.max)
            
            # Create plot
            fig, ax = plt.subplots(figsize=self.figsize)
            
            # Calculate frequency axes
            modulation_freqs = np.fft.fftfreq(magnitude_smooth.shape[1], d=512/sample_rate)[:mod_spec.shape[1]]
            acoustic_freqs = librosa.fft_frequencies(sr=sample_rate, n_fft=2048)
            
            # Limit to reasonable modulation frequency range (0-50 Hz)
            mod_freq_limit = 50
            mod_indices = modulation_freqs <= mod_freq_limit
            
            img = ax.imshow(
                mod_spec_db[:, mod_indices], 
                extent=[0, mod_freq_limit, acoustic_freqs[-1], acoustic_freqs[0]], 
                cmap='hot', 
                aspect='auto',
                origin='upper',
                interpolation='bilinear'
            )
            
            ax.set_title('Modulation Spectrogram\n(Sideband Modulation Analysis)', fontweight='bold')
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
