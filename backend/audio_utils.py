"""
Audio Processing Utilities for Flask Motor Audio Analyzer
Handles audio loading and comprehensive feature extraction
"""

import librosa
import numpy as np
from scipy import stats
import logging
from typing import Tuple, Dict, Any

logger = logging.getLogger(__name__)

class AudioProcessor:
    """Main audio processing class for motor audio analysis"""
    
    def __init__(self):
        self.default_sr = 22050  # Default sample rate for consistency
    
    def load_audio(self, file_path: str) -> Tuple[np.ndarray, int]:
        """
        Load audio file and return audio data and sample rate
        
        Args:
            file_path: Path to audio file
            
        Returns:
            Tuple of (audio_data, sample_rate)
        """
        try:
            # Load audio with librosa
            audio_data, sample_rate = librosa.load(
                file_path, 
                sr=self.default_sr,  # Resample to consistent rate
                mono=True  # Convert to mono
            )
            
            # Normalize audio to prevent clipping
            if np.max(np.abs(audio_data)) > 0:
                audio_data = librosa.util.normalize(audio_data)
            
            logger.info(f"Loaded audio: {len(audio_data)} samples at {sample_rate} Hz")
            return audio_data, sample_rate
            
        except Exception as e:
            logger.error(f"Failed to load audio: {e}")
            raise ValueError(f"Could not load audio file: {e}")
    
    def extract_features(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, Any]:
        """
        Extract comprehensive audio features for motor analysis
        
        Args:
            audio_data: Audio time series
            sample_rate: Sample rate of audio
            
        Returns:
            Dictionary of extracted features
        """
        features = {}
        
        try:
            # Time-domain features
            features.update(self._extract_time_domain_features(audio_data, sample_rate))
            
            # Frequency-domain features
            features.update(self._extract_frequency_domain_features(audio_data, sample_rate))
            
            # Spectral features
            features.update(self._extract_spectral_features(audio_data, sample_rate))
            
            # Rhythm and tempo features
            features.update(self._extract_rhythm_features(audio_data, sample_rate))
            
            logger.info(f"Extracted {len(features)} audio features")
            return features
            
        except Exception as e:
            logger.error(f"Feature extraction failed: {e}")
            raise ValueError(f"Feature extraction failed: {e}")
    
    def _extract_time_domain_features(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, float]:
        """Extract time-domain features crucial for motor analysis"""
        features = {}
        
        try:
            # RMS Energy - indicates overall energy level
            rms_frames = librosa.feature.rms(y=audio_data, frame_length=2048, hop_length=512)
            features['rms_energy_mean'] = float(np.mean(rms_frames))
            features['rms_energy_std'] = float(np.std(rms_frames))
            
            # Zero Crossing Rate - indicates frequency content
            zcr = librosa.feature.zero_crossing_rate(audio_data, frame_length=2048, hop_length=512)
            features['zero_crossing_rate_mean'] = float(np.mean(zcr))
            features['zero_crossing_rate_std'] = float(np.std(zcr))
            
            # Peak amplitude and crest factor
            features['peak_amplitude'] = float(np.max(np.abs(audio_data)))
            rms_value = features['rms_energy_mean']
            features['crest_factor'] = features['peak_amplitude'] / rms_value if rms_value > 0 else 0
            
            # Statistical moments of amplitude
            abs_audio = np.abs(audio_data)
            features['mean_amplitude'] = float(np.mean(abs_audio))
            features['std_amplitude'] = float(np.std(audio_data))
            features['skewness_amplitude'] = float(stats.skew(audio_data))
            features['kurtosis_amplitude'] = float(stats.kurtosis(audio_data))
            
            # Dynamic range
            features['dynamic_range'] = features['peak_amplitude'] - np.min(abs_audio)
            
        except Exception as e:
            logger.warning(f"Time domain feature extraction failed: {e}")
            # Set default values
            for key in ['rms_energy_mean', 'rms_energy_std', 'zero_crossing_rate_mean', 
                       'zero_crossing_rate_std', 'peak_amplitude', 'crest_factor']:
                features[key] = 0.0
        
        return features
    
    def _extract_frequency_domain_features(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, float]:
        """Extract frequency-domain features for spectral analysis"""
        features = {}
        
        try:
            # Spectral centroid - "brightness" of sound
            spectral_centroids = librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate)
            features['spectral_centroid_mean'] = float(np.mean(spectral_centroids))
            features['spectral_centroid_std'] = float(np.std(spectral_centroids))
            
            # Spectral bandwidth - spread of frequencies
            spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio_data, sr=sample_rate)
            features['spectral_bandwidth_mean'] = float(np.mean(spectral_bandwidth))
            features['spectral_bandwidth_std'] = float(np.std(spectral_bandwidth))
            
            # Spectral contrast - difference between peaks and valleys
            spectral_contrast = librosa.feature.spectral_contrast(y=audio_data, sr=sample_rate)
            features['spectral_contrast_mean'] = float(np.mean(spectral_contrast))
            features['spectral_contrast_std'] = float(np.std(spectral_contrast))
            
            # Spectral flatness - measure of noisiness
            spectral_flatness = librosa.feature.spectral_flatness(y=audio_data)
            features['spectral_flatness_mean'] = float(np.mean(spectral_flatness))
            features['spectral_flatness_std'] = float(np.std(spectral_flatness))
            
            # Spectral rolloff - frequency below which specified percentage of energy is contained
            spectral_rolloff = librosa.feature.spectral_rolloff(y=audio_data, sr=sample_rate)
            features['spectral_rolloff_mean'] = float(np.mean(spectral_rolloff))
            features['spectral_rolloff_std'] = float(np.std(spectral_rolloff))
            
        except Exception as e:
            logger.warning(f"Frequency domain feature extraction failed: {e}")
            # Set default values
            for key in ['spectral_centroid_mean', 'spectral_centroid_std', 'spectral_bandwidth_mean',
                       'spectral_bandwidth_std', 'spectral_contrast_mean', 'spectral_contrast_std']:
                features[key] = 0.0
        
        return features
    
    def _extract_spectral_features(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, float]:
        """Extract advanced spectral features including MFCCs"""
        features = {}
        
        try:
            # MFCCs (Mel-frequency cepstral coefficients) - most important for audio analysis
            mfccs = librosa.feature.mfcc(y=audio_data, sr=sample_rate, n_mfcc=13)
            for i in range(mfccs.shape[0]):
                features[f'mfcc_{i+1}_mean'] = float(np.mean(mfccs[i]))
                features[f'mfcc_{i+1}_std'] = float(np.std(mfccs[i]))
            
            # Chroma features - harmonic content
            chroma = librosa.feature.chroma_stft(y=audio_data, sr=sample_rate)
            features['chroma_mean'] = float(np.mean(chroma))
            features['chroma_std'] = float(np.std(chroma))
            for i in range(chroma.shape[0]):
                features[f'chroma_{i+1}_mean'] = float(np.mean(chroma[i]))
            
            # Tonnetz (Tonal centroid features) - harmonic relationships
            tonnetz = librosa.feature.tonnetz(y=audio_data, sr=sample_rate)
            features['tonnetz_mean'] = float(np.mean(tonnetz))
            features['tonnetz_std'] = float(np.std(tonnetz))
            
        except Exception as e:
            logger.warning(f"Spectral feature extraction failed: {e}")
            # Set default MFCC values
            for i in range(13):
                features[f'mfcc_{i+1}_mean'] = 0.0
                features[f'mfcc_{i+1}_std'] = 0.0
            features['chroma_mean'] = 0.0
            features['tonnetz_mean'] = 0.0
        
        return features
    
    def _extract_rhythm_features(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, float]:
        """Extract rhythm and tempo features for motor pattern analysis"""
        features = {}
        
        try:
            # Tempo estimation and beat tracking
            tempo, beats = librosa.beat.beat_track(y=audio_data, sr=sample_rate)
            features['tempo'] = float(tempo)
            features['beat_count'] = len(beats)
            
            # Beat interval analysis
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
            
            # Onset detection for transient analysis
            onset_frames = librosa.onset.onset_detect(y=audio_data, sr=sample_rate)
            features['onset_count'] = len(onset_frames)
            
            if len(onset_frames) > 1:
                onset_times = librosa.frames_to_time(onset_frames, sr=sample_rate)
                onset_intervals = np.diff(onset_times)
                features['onset_interval_mean'] = float(np.mean(onset_intervals))
                features['onset_interval_std'] = float(np.std(onset_intervals))
            else:
                features['onset_interval_mean'] = 0.0
                features['onset_interval_std'] = 0.0
                
        except Exception as e:
            logger.warning(f"Rhythm feature extraction failed: {e}")
            # Set default values
            default_rhythm_features = {
                'tempo': 0.0,
                'beat_count': 0,
                'beat_interval_mean': 0.0,
                'beat_interval_std': 0.0,
                'beat_regularity': 0.0,
                'onset_count': 0,
                'onset_interval_mean': 0.0,
                'onset_interval_std': 0.0
            }
            features.update(default_rhythm_features)
        
        return features
