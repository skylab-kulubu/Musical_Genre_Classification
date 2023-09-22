import numpy as np 
import matplotlib.pyplot as plt  
from PIL import Image as im
from scipy.io import wavfile  
import os   
from scipy import signal 
import itertools 
import csv


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

def calculate_features(stft_matrix):
    num_windows = stft_matrix.shape[1]
    num_bins = stft_matrix.shape[0]
    freq_axis = np.arange(num_bins)
    features = []

    for window_idx in range(num_windows):
        stft_window = stft_matrix[:, window_idx]
        power = np.sum(np.abs(stft_window) ** 2) / stft_window.size
        freq_avg = np.average(freq_axis, weights=np.abs(stft_window))
        ampl_avg = np.average(np.abs(stft_window))
        features.append([power, freq_avg, ampl_avg])
    return features 

def genres_to_csv(genres_array,genre_name,window_type='hamming') : 
    features_genre = []
    for idx,genre in enumerate(genres_array): 
        stft_matrix = ShortFourierTransform(signal=genre,window_size=1024,overlap_ratio=0.2,window_type=window_type)
        if idx < 23 and genre_name == 'reggea': 
            stft_matrix = stft_matrix
        if idx == 54 and genre_name == 'classical': 
            continue
        print(idx,". işlem yapılıyor. ")
        stft_matrix = ShortFourierTransform(signal=genre,window_size=1024,overlap_ratio=0.2,window_type=window_type)
        features = calculate_features(stft_matrix=stft_matrix) 
        array = np.array(features)  
        mean_values = np.mean(array, axis=0)
        std_values = np.std(array, axis=0)
        median_values = np.median(array, axis=0) 

        
        features_dict = {
        'Power_mean': mean_values[0],
        'Amplitude_mean': mean_values[1],
        'Weighted_Mean_Frequency_mean': mean_values[2], 
        'Power_std': std_values[0],
        'Amplitude_std': std_values[1],
        'Weighted_Mean_Frequency_std': std_values[2],  
        'Power_median': median_values[0],
        'Amplitude_median': median_values[1],
        'Weighted_Mean_Frequency_median': median_values[2], 
        'Genre': genre
        } 
        features_genre.append(features_dict)
    
    csv_file = f'Data\FeaturesCsv\\{genre_name}_{window_type}.csv' 
    
    # Get the keys from the first entry in the features list
    keys = list(features_genre[0].keys())

    # Save the features to the CSV file
    with open(csv_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(features_genre) 

def process_genres(genre_array,genre_name,window_type='hamming') : 
    print(genre_name)
    for idx,genre in enumerate(genre_array): 

        if idx > 99 and genre_name !='jazz' : 
            genre = genre[:,0]  

        if genre_name =='jazz' and idx > 98: 
            genre = genre[:,0]

        stftMatrix = ShortFourierTransform(genre,1024,0.2,window_type=window_type)
        spectrogram_data_amplitude = np.angle(stftMatrix) 
        spectrogram_data_amplitude = spectrogram_data_amplitude[0:1024,0:720]

        plt.figure(figsize=(8, 6))  
        plt.imshow(spectrogram_data_amplitude, cmap='viridis')  
        plt.savefig(f'Spectograms\PhaseSpectograms\genres\{genre_name}\\{genre_name}_{idx}.jpg', bbox_inches='tight', dpi=300)  
        plt.close()
        print(f"{idx}. işlem sonlandı")
        

def Main():  
    
    blues= load_from_folder('Data\genres\\blues')  
    print('blues okey')
    
    classical = load_from_folder('Data\genres\\classical')  
    print('classic okey')

    disco= load_from_folder('Data\genres\\disco') 
    print('disco okey')

    #hiphop = load_from_folder('Data\genres\\hiphop')   
    #print('hiphop okey')

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
    

    #process_genres(blues,'blues')
    #process_genres(classical,'classical')
    #process_genres(disco,'disco') 
    #process_genres(rock,'rock') 
    #process_genres(metal,'metal') 
    #process_genres(pop,'pop') 
    #process_genres(reggae,'reggae') 
    process_genres(jazz,'jazz')
    process_genres(country,'country')
    #process_genres(hiphop,'hiphop')

    print("Resimler doğru bir şekilde dosyalara çıkıldı.")   
    
    """ 
    #genres_to_csv(blues,'blues')
    genres_to_csv(classical,'classical')
    #genres_to_csv(disco,'disco') 
    genres_to_csv(rock,'rock') 
    genres_to_csv(metal,'metal') 
    #genres_to_csv(pop,'pop') 
    #genres_to_csv(reggae,'reggae') 
    #genres_to_csv(jazz,'jazz')
    #genres_to_csv(country,'country')
    #genres_to_csv(hiphop,'hiphop') 
    print('Csv dosyaları başarılı oluştu')
    """ 

   

    

Main()