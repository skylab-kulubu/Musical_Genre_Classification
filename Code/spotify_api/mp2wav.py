import os
import subprocess
import argparse

def convert_to_wav(filename, output_filename):
    subprocess.call(['ffmpeg', '-i', filename, output_filename + '.wav'])

def load_mp3_from_dir(directory_name):
    out = {"directory_name": directory_name}
    files = []
    for file in os.listdir(directory_name):
        files.append(file)
    out["filenames"] = files
    return out

def convert_mp3_to_wav(mp3ler, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    input_dir = mp3ler["directory_name"]
    for mp3 in mp3ler["filenames"]:
        print("Converting {} to wav".format(mp3))
        convert_to_wav(input_dir + "/" + mp3, output_dir + "/" + mp3[:-4])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert mp3 files to wav')
    parser.add_argument('input_dir', type=str, help='Input directory')    
    parser.add_argument('-o', '--output_dir', type=str, help='Output directory')
    args = parser.parse_args()
    mp3 = load_mp3_from_dir(args.input_dir)
    convert_mp3_to_wav(mp3, args.output_dir)
