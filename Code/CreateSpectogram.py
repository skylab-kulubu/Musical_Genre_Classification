import numpy as np 
import matplotlib.pyplot as plt  
from PIL import Image as im
from scipy.io import wavfile  
import os   
from scipy import signal 
import itertools


def load_from_folder(folder_path):  
    songs = [] 
    for filename in os.listdir(folder_path): 
                sample_rate , song = wavfile.read(os.path.join(folder_path,filename)) 
                if song is not None:
                    songs.append(song) 
    
    return songs 

def FFT(x):
    """
    A recursive implementation of 
    the 1D Cooley-Tukey FFT, the 
    input should have a length of 
    power of 2. 
    """
    # It slow therefore it weren't used.
    N = len(x)
    
    if N == 1:
        return x
    else:
        X_even = FFT(x[::2])
        X_odd = FFT(x[1::2])
        factor = \
          np.exp(-2j*np.pi*np.arange(N)/ N)
        
        X = np.concatenate(\
            [X_even+factor[:int(N/2)]*X_odd,
             X_even+factor[int(N/2):]*X_odd])
        return X 


def ShortFourierTransform(signal, window_size, overlap_ratio=0.2,window_type='hamming'):
    hop_length = int(window_size * (1 - overlap_ratio))

    # Compute the number of frames
    num_frames = 1 + (len(signal) - window_size) // hop_length

    # Create an empty matrix to store the STFT coefficients
    stft_matrix = np.zeros((window_size, num_frames), dtype=np.complex128)

    for frame_idx in range(num_frames):
        # Calculate the start and end indices for the current frame
        start = frame_idx * hop_length
        end = start + window_size

        # Extract the current frame from the signal
        frame = signal[start:end]

        # Apply the window function to the frame 
        if(window_type == 'hanning') : 
            windowed_frame = frame * np.hanning(window_size) 
        elif(window_type == 'bartlett') : 
            windowed_frame = frame * np.bartlett(window_size) 
        else : 
            windowed_frame = frame * np.hamming(window_size) 

        # Perform the FFT on the windowed frame
        fft_frame = np.fft.fft(windowed_frame)

        # Store the FFT coefficients in the STFT matrix
        stft_matrix[:, frame_idx] = fft_frame

    return stft_matrix


def plot_spectrogram(magnitude_spectrogram, hop_size, sample_rate):
    """
    Plot the magnitude spectrogram.

    Args:
        magnitude_spectrogram (numpy.ndarray): The magnitude spectrogram.
        hop_size (int): The hop size used in the STFT.
        sample_rate (int): The sample rate of the original signal.
    """
    # Calculate the time and frequency axes for the spectrogram
    num_frames, window_size = magnitude_spectrogram.shape
    duration = num_frames * hop_size / sample_rate
    frequencies = np.arange(window_size) * sample_rate / window_size
    times = np.arange(num_frames) * hop_size / sample_rate

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.imshow(magnitude_spectrogram.T, aspect='auto', origin='lower', cmap='jet')
    plt.colorbar(format='%+2.0f dB')
    plt.title('Magnitude Spectrogram')
    plt.xlabel('Time (s)')
    plt.ylabel('Frequency (Hz)')
    plt.show() 

def process_genres(genre_array,genre_name,window_type='hamming') : 
    
    for idx,genre in enumerate(genre_array):  
        stftMatrix = ShortFourierTransform(genre,1024,0.2,window_type=window_type) 
        spectrogram_data_amplitude = np.abs(stftMatrix)
        plt.figure(figsize=(8, 6))  # İsteğe bağlı olarak figür boyutunu ayarlayabilirsiniz
        plt.imshow(spectrogram_data_amplitude, cmap='viridis')  # 'viridis' renk haritasını kullanabilirsiniz, başka haritalar da mevcuttur
    
        # Spektrogramu bir dosyaya kaydetmek için:
        plt.savefig(f'Spectograms\genres\{genre_name}\\{genre_name}_{idx}.jpg', bbox_inches='tight', dpi=300)  # 'spectrogram.png' adlı bir dosyaya kaydedin
        plt.close()
        print(f"{idx}. işlem sonlandı")
        

def Main():  
    
    blues= load_from_folder('Data\genres\\blues')  
    print('blues okey')
    
    classical = load_from_folder('Data\genres\\classical')  
    print('classic okey')

    disco= load_from_folder('Data\genres\\disco') 
    print('disco okey')

    hiphop = load_from_folder('Data\genres\\hiphop')   
    print('hiphop okey')

    metal = load_from_folder('Data\genres\\metal')   
    print('metal okey')

    country = load_from_folder('Data\genres\\country') 
    print('country okey')
    
    jazz = load_from_folder('Data\genres\\jazz')  
    print('jazz okey')

    pop= load_from_folder('Data\genres\\pop')  
    print('pop okey')
   
    reggae = load_from_folder('Data\genres\\reggae')  
    print('reggea okey')
   
    rock = load_from_folder('Data\genres\\rock')   
    print('rock okey')
    
    process_genres(blues,'blues')
    process_genres(classical,'classical')
    process_genres(disco,'disco') 
    process_genres(rock,'rock') 
    process_genres(metal,'metal') 
    process_genres(pop,'pop') 
    process_genres(reggae,'reggae') 
    process_genres(jazz,'jazz')
    process_genres(country,'country')
    process_genres(hiphop,'hiphop')

    print("Resimler doğru bir şekilde dosyalara çıkıldı.") 

Main()