"""
Audio Processing Utilities for Flask Motor Audio Analyzer
Handles audio loading and comprehensive feature extraction
"""

"""
SciPy-free Audio Processing Utilities
Uses alternative libraries to avoid SciPy compilation issues on Windows
"""

import librosa
import numpy as np
import statistics
import logging
from typing import Tuple, Dict, Any
import soundfile as sf
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)

class AudioProcessor:
    """SciPy-free audio processing class"""
    
    def __init__(self):
        self.default_sr = 22050
    
    def load_audio(self, file_path: str) -> Tuple[np.ndarray, int]:
        """Load audio using SoundFile instead of scipy"""
        try:
            # Primary method: use soundfile
            audio_data, sample_rate = sf.read(file_path)
            
            # Convert to mono if stereo
            if len(audio_data.shape) > 1:
                audio_data = np.mean(audio_data, axis=1)
            
            # Resample if needed (using librosa which handles this well)
            if sample_rate != self.default_sr:
                audio_data = librosa.resample(audio_data, 
                                            orig_sr=sample_rate, 
                                            target_sr=self.default_sr)
                sample_rate = self.default_sr
            
            # Normalize
            if np.max(np.abs(audio_data)) > 0:
                audio_data = librosa.util.normalize(audio_data)
            
            logger.info(f"Loaded audio: {len(audio_data)} samples at {sample_rate} Hz")
            return audio_data, sample_rate
            
        except Exception as e:
            logger.error(f"Failed to load audio with SoundFile: {e}")
            # Fallback to librosa
            try:
                audio_data, sample_rate = librosa.load(file_path, sr=self.default_sr, mono=True)
                audio_data = librosa.util.normalize(audio_data)
                return audio_data, sample_rate
            except Exception as e2:
                raise ValueError(f"Could not load audio file: {e2}")
    
    def extract_features(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, Any]:
        """Extract features without scipy.stats"""
        features = {}
        
        try:
            features.update(self._extract_time_domain_features(audio_data, sample_rate))
            features.update(self._extract_frequency_domain_features(audio_data, sample_rate))
            features.update(self._extract_spectral_features(audio_data, sample_rate))
            features.update(self._extract_rhythm_features(audio_data, sample_rate))
            
            logger.info(f"Extracted {len(features)} audio features")
            return features
            
        except Exception as e:
            logger.error(f"Feature extraction failed: {e}")
            raise ValueError(f"Feature extraction failed: {e}")
    
    def _extract_time_domain_features(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, float]:
        """Time-domain features using NumPy instead of scipy.stats"""
        features = {}
        
        try:
            # RMS Energy
            rms_frames = librosa.feature.rms(y=audio_data, frame_length=2048, hop_length=512)
            features['rms_energy_mean'] = float(np.mean(rms_frames))
            features['rms_energy_std'] = float(np.std(rms_frames))
            
            # Zero Crossing Rate
            zcr = librosa.feature.zero_crossing_rate(audio_data, frame_length=2048, hop_length=512)
            features['zero_crossing_rate_mean'] = float(np.mean(zcr))
            features['zero_crossing_rate_std'] = float(np.std(zcr))
            
            # Basic amplitude features
            abs_audio = np.abs(audio_data)
            features['peak_amplitude'] = float(np.max(abs_audio))
            features['mean_amplitude'] = float(np.mean(abs_audio))
            features['std_amplitude'] = float(np.std(audio_data))
            
            # Crest factor
            rms_value = features['rms_energy_mean']
            features['crest_factor'] = features['peak_amplitude'] / rms_value if rms_value > 0 else 0
            
            # Statistical moments using NumPy
            features['skewness_amplitude'] = float(self._calculate_skewness(audio_data))
            features['kurtosis_amplitude'] = float(self._calculate_kurtosis(audio_data))
            
            # Dynamic range
            features['dynamic_range'] = features['peak_amplitude'] - np.min(abs_audio)
            
        except Exception as e:
            logger.warning(f"Time domain feature extraction failed: {e}")
            # Set defaults
            default_features = ['rms_energy_mean', 'rms_energy_std', 'zero_crossing_rate_mean', 
                              'zero_crossing_rate_std', 'peak_amplitude', 'crest_factor']
            for key in default_features:
                features[key] = 0.0
        
        return features
    
    def _calculate_skewness(self, data: np.ndarray) -> float:
        """Calculate skewness using NumPy (replaces scipy.stats.skew)"""
        try:
            data_mean = np.mean(data)
            data_std = np.std(data)
            if data_std == 0:
                return 0.0
            normalized = (data - data_mean) / data_std
            return float(np.mean(normalized**3))
        except:
            return 0.0
    
    def _calculate_kurtosis(self, data: np.ndarray) -> float:
        """Calculate kurtosis using NumPy (replaces scipy.stats.kurtosis)"""
        try:
            data_mean = np.mean(data)
            data_std = np.std(data)
            if data_std == 0:
                return 0.0
            normalized = (data - data_mean) / data_std
            return float(np.mean(normalized**4) - 3)  # Excess kurtosis
        except:
            return 0.0
    
    def _extract_frequency_domain_features(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, float]:
        """Frequency domain features (librosa handles most of this)"""
        features = {}
        
        try:
            # These use librosa which has its own implementations
            spectral_centroids = librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate)
            features['spectral_centroid_mean'] = float(np.mean(spectral_centroids))
            features['spectral_centroid_std'] = float(np.std(spectral_centroids))
            
            spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio_data, sr=sample_rate)
            features['spectral_bandwidth_mean'] = float(np.mean(spectral_bandwidth))
            features['spectral_bandwidth_std'] = float(np.std(spectral_bandwidth))
            
            spectral_contrast = librosa.feature.spectral_contrast(y=audio_data, sr=sample_rate)
            features['spectral_contrast_mean'] = float(np.mean(spectral_contrast))
            features['spectral_contrast_std'] = float(np.std(spectral_contrast))
            
            spectral_flatness = librosa.feature.spectral_flatness(y=audio_data)
            features['spectral_flatness_mean'] = float(np.mean(spectral_flatness))
            features['spectral_flatness_std'] = float(np.std(spectral_flatness))
            
            spectral_rolloff = librosa.feature.spectral_rolloff(y=audio_data, sr=sample_rate)
            features['spectral_rolloff_mean'] = float(np.mean(spectral_rolloff))
            features['spectral_rolloff_std'] = float(np.std(spectral_rolloff))
            
        except Exception as e:
            logger.warning(f"Frequency domain feature extraction failed: {e}")
        
        return features
    
    def _extract_spectral_features(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, float]:
        """Spectral features using librosa"""
        features = {}
        
        try:
            # MFCCs
            mfccs = librosa.feature.mfcc(y=audio_data, sr=sample_rate, n_mfcc=13)
            for i in range(mfccs.shape[0]):
                features[f'mfcc_{i+1}_mean'] = float(np.mean(mfccs[i]))
                features[f'mfcc_{i+1}_std'] = float(np.std(mfccs[i]))
            
            # Chroma features
            chroma = librosa.feature.chroma_stft(y=audio_data, sr=sample_rate)
            features['chroma_mean'] = float(np.mean(chroma))
            features['chroma_std'] = float(np.std(chroma))
            
            # Tonnetz
            tonnetz = librosa.feature.tonnetz(y=audio_data, sr=sample_rate)
            features['tonnetz_mean'] = float(np.mean(tonnetz))
            features['tonnetz_std'] = float(np.std(tonnetz))
            
        except Exception as e:
            logger.warning(f"Spectral feature extraction failed: {e}")
        
        return features
    
    def _extract_rhythm_features(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, float]:
        """Rhythm features using librosa"""
        features = {}
        
        try:
            tempo, beats = librosa.beat.beat_track(y=audio_data, sr=sample_rate)
            features['tempo'] = float(tempo)
            features['beat_count'] = len(beats)
            
            if len(beats) > 1:
                beat_times = librosa.frames_to_time(beats, sr=sample_rate)
                beat_intervals = np.diff(beat_times)
                features['beat_interval_mean'] = float(np.mean(beat_intervals))
                features['beat_interval_std'] = float(np.std(beat_intervals))
                features['beat_regularity'] = float(1.0 / (1.0 + np.std(beat_intervals)))
            else:
                features['beat_interval_mean'] = 0.0
                features['beat_interval_std'] = 0.0
                features['beat_regularity'] = 0.0
            
            # Onset detection
            onset_frames = librosa.onset.onset_detect(y=audio_data, sr=sample_rate)
            features['onset_count'] = len(onset_frames)
            
        except Exception as e:
            logger.warning(f"Rhythm feature extraction failed: {e}")
        
        return features
