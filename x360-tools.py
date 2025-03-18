import os
import tkinter as Tk
from tkinter import filedialog
import pathlib
import shutil
import subprocess

main = os.getcwd()
codename = None  # Definição inicial como None

def convert_xma(inputfile, codename, main):
    if not codename:
        print("error: codename not defined!")
        return

    print(f"file selected: {inputfile}")

    # Criar diretório temp se não existir
    xma_path = os.path.join(main, "temp")
    os.makedirs(xma_path, exist_ok=True)

    temp_xma = os.path.join(xma_path, "temp.xma")

    # Comando para converter o áudio
    subprocess.run(f'"{os.path.join("bin", "xma2encode.exe")}" "{inputfile}" /BlockSize 4 /Quality 92 /TargetFile "{temp_xma}"')

    if not os.path.exists(temp_xma):
        print(f"error: conversion failed for {temp_xma}.")
        return

    print(f"converting wav to {temp_xma}...")

    with open(temp_xma, "rb") as f:
        xma_data = f.read()
    
    # Substituir o cabeçalho do arquivo pelo cabeçalho personalizado
    custom_header = b"\x52\x41\x4B\x49\x00\x00\x00\x09\x58\x33\x36\x30\x78\x6D\x61\x32\x00\x00\x1D\x50\x00\x00\x20\x00\x00\x00\x00\x03\x00\x00\x00\x03\x66\x6D\x74\x20\x00\x00\x00\x44\x00\x00\x00\x34\x73\x65\x65\x6B\x00\x00\x00\x78\x00\x00\x1C\xD8\x64\x61\x74\x61\x00\x00\x20\x00"
    modified_xma_data = custom_header + xma_data[len(custom_header):]  # Substitui apenas o cabeçalho

    output_dir = os.path.join(main, "output", codename, "audio")
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, f"{codename.lower()}.wav.ckd")
    with open(output_path, "wb") as f:
        f.write(modified_xma_data)

    print(f"file {output_path} created.")
    shutil.rmtree(xma_path)

def convert_gesture(input_folder="input", output_folder="output"):
    # Define a estrutura de pastas dentro do output
    output_path = os.path.join(output_folder, codename)  # output/codename
    moves_path = os.path.join(output_path, "moves")  # output/codename/moves

    # Criar as pastas caso não existam
    os.makedirs(moves_path, exist_ok=True)

    # Verifica se a pasta de entrada existe
    if not os.path.exists(input_folder):
        print("you need to put some .gesture in the input")
        os.makedirs(input_folder)
        return

    # Lista todos os arquivos .gesture na pasta de entrada
    gesture_files = [f for f in os.listdir(input_folder) if f.endswith(".gesture")]

    if not gesture_files:
        print("without .gesture in input folder")
        return

    for gesture_file in gesture_files:
        input_path = os.path.join(input_folder, gesture_file)
        output_gesture_path = os.path.join(moves_path, gesture_file.lower())  # Salva em minúsculas e salva dentro de "moves"
        os.makedirs(moves_path, exist_ok=True)

        with open(input_path, "rb") as f:
            file_bytes = f.read()

        # Remove o cabeçalho do Xbox One e ajusta os dados
        gesture_data = file_bytes[22:]  # Remove os primeiros 22 bytes
        gesture_data = bytearray(gesture_data)

        # Inverte os bytes a cada 4 posições
        for i in range(0, len(gesture_data), 4):
            if i + 4 <= len(gesture_data):
                gesture_data[i:i+4] = reversed(gesture_data[i:i+4])

        # Escreve o novo arquivo dentro da pasta moves
        with open(output_gesture_path, "wb") as f:
            f.write(b"GestureDetectorX360")  # Escreve o cabeçalho do Xbox 360
            f.write(b"\x00")  # Byte extra
            f.write(gesture_data)

        print(f"converted: {output_gesture_path}")

    print("conversion complete!")

def set_codename():
    global codename
    codename = input("codename: ").strip()
    if not codename:
        print("error: codename cannot be empty!")
        exit(1)

def convert_pictos():
    header = b"\x00\x00\x00\x09\x54\x45\x58\x00\x00\x00\x00\x2C\x00\x00\x20\x80\x01\x00\x01\x00\x00\x01\x18\x00\x00\x00\x20\x80\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\xCC\xCC"

    out_folder = f"{main}\\output\\{codename}\\pictos"  # Pasta de saída
    tempfolder = f"{main}\\temp"  # Pasta temporária para armazenar arquivos .png
    os.makedirs(tempfolder, exist_ok=True)  # Cria a pasta temp, se não existir

    # Iterando sobre todos os arquivos na pasta de entrada
    for filename in os.listdir(input_folder):
        if filename.lower().endswith(".dds"):  # Verifica se o arquivo é .dds
            img_path = os.path.join(input_folder, filename)  # Caminho do arquivo .dds
            png_filename = filename.split(".")[0] + ".png"  # Nome do arquivo .png
            png_path = os.path.join(tempfolder, png_filename)  # Caminho do .png na pasta temp

            print(f"Converting {filename} to {png_filename}...")

            # Converte o arquivo .dds para .png
            subprocess.run(
                f'bin\\magick.exe convert "{img_path}" "{png_path}"',
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE
            )

            # Lê o arquivo .png convertido
            with open(png_path, "rb") as png_file:
                png = png_file.read()

            # Garante que a pasta de saída exista
            os.makedirs(out_folder, exist_ok=True)

            # Cria o arquivo final com o cabeçalho e o conteúdo do .png
            output_ckd = os.path.join(out_folder, filename.replace('.dds', '.png.ckd'))
            with open(output_ckd, "wb") as ckd:
                ckd.write(header + png)

            os.remove(png_path)

    shutil.rmtree(tempfolder)

def convert_menuart():
    header = b"\x00\x00\x00\x09\x54\x45\x58\x00\x00\x00\x00\x2C\x00\x00\x20\x80\x01\x00\x01\x00\x00\x01\x18\x00\x00\x00\x20\x80\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\xCC\xCC"

    out_folder = f"{main}\\output\\{codename}\\menuart"  # Pasta de saída
    tempfolder = f"{main}\\temp"  # Pasta temporária para armazenar arquivos .png
    os.makedirs(tempfolder, exist_ok=True)  # Cria a pasta temp, se não existir

    # Iterando sobre todos os arquivos na pasta de entrada
    for filename in os.listdir(input_folder):
        if filename.lower().endswith(".dds"):  # Verifica se o arquivo é .dds
            img_path = os.path.join(input_folder, filename)  # Caminho do arquivo .dds
            png_filename = filename.split(".")[0] + ".png"  # Nome do arquivo .png
            png_path = os.path.join(tempfolder, png_filename)  # Caminho do .png na pasta temp

            print(f"Converting {filename} to {png_filename}...")

            # Converte o arquivo .dds para .png
            subprocess.run(
                f'bin\\magick.exe convert "{img_path}" "{png_path}"',
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE
            )

            # Lê o arquivo .png convertido
            with open(png_path, "rb") as png_file:
                png = png_file.read()

            # Garante que a pasta de saída exista
            os.makedirs(out_folder, exist_ok=True)

            # Cria o arquivo final com o cabeçalho e o conteúdo do .png
            output_ckd = os.path.join(out_folder, filename.replace('.dds', '.tga.ckd'))
            with open(output_ckd, "wb") as ckd:
                ckd.write(header + png)

            os.remove(png_path)

    shutil.rmtree(tempfolder)


def webm(codename, orig_name_video):
    output_dir = os.path.join(os.getcwd(), 'output')
    nohud_dir = os.path.join(output_dir, codename, 'videoscoach')
    ffmpeg_path = os.path.join(main, 'bin', 'ffmpeg.exe')  # Caminho do FFmpeg dentro da pasta bin
    
    if os.path.exists(nohud_dir):
        shutil.rmtree(nohud_dir)
    os.makedirs(nohud_dir, exist_ok=True)
    
    resolution = '1216:720'
    video_output_path = os.path.join(nohud_dir, f'{codename.lower()}.x360.webm')
    
    video_command = [
        ffmpeg_path, '-v', 'quiet', '-stats', '-loglevel', 'error', '-i', orig_name_video,
        '-threads:v', '4', '-qscale:v', '3', '-sws_flags', 'bilinear', '-codec:v', 'libvpx',
        '-r:v', '25', '-b:v', '4000k', '-bufsize', '4000k', '-keyint_min', '25', '-g', '25',
        '-rc_lookahead', '16', '-profile:v', '1', '-qmax', '28', '-qmin', '1', '-slices', '4',
        '-quality', 'realtime', '-an', '-af', 'volume=0', '-aspect', '16:9',
        '-vf', f'scale={resolution}', '-y', video_output_path
    ]
    
    print(f'converting {video_output_path} to {resolution}')
    subprocess.run(video_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f'converted successfully! check path {video_output_path}')

def convert_xma_amb(inputfile, codename, main):
    if not codename:
        print("error: codename not defined!")
        return

    print(f"file selected: {inputfile}")

    # Criar diretório temp se não existir
    xma_path = os.path.join(main, "temp")
    os.makedirs(xma_path, exist_ok=True)

    temp_xma = os.path.join(xma_path, "temp.xma")

    # Comando para converter o áudio
    subprocess.run(f'"{os.path.join("bin", "xma2encode.exe")}" "{inputfile}" /BlockSize 4 /Quality 92 /TargetFile "{temp_xma}"')

    if not os.path.exists(temp_xma):
        print(f"error: conversion failed for {temp_xma}.")
        return

    print(f"converting wav to {temp_xma}...")

    with open(temp_xma, "rb") as f:
        xma_data = f.read()
    
    # Substituir o cabeçalho do arquivo pelo cabeçalho personalizado
    custom_header = b"\x52\x41\x4B\x49\x00\x00\x00\x09\x58\x33\x36\x30\x78\x6D\x61\x32\x00\x00\x01\xC4\x00\x00\x08\x00\x00\x00\x00\x03\x00\x00\x00\x00\x66\x6D\x74\x20\x00\x00\x00\x44\x00\x00\x00\x34\x73\x65\x65\x6B\x00\x00\x00\x78\x00\x00\x01\x4C\x64\x61\x74\x61\x00\x00\x08\x00"
    modified_xma_data = custom_header + xma_data[len(custom_header):]  # Substitui apenas o cabeçalho

    output_dir = os.path.join(main, "output", codename, "audio", "amb")
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, f"amb_{codename.lower()}_{ambType}.wav.ckd")
    with open(output_path, "wb") as f:
        f.write(modified_xma_data)

    print(f"file {output_path} created.")
    shutil.rmtree(xma_path)

if __name__ == '__main__':
    os.system('cls' if os.name == 'nt' else 'clear')
    print("Xbox 360 tools made by lunn!")
    print("                             ")
    while True:
        print("-----------------------------")
        print("                             ")
        print("-----------------------------")
        print("                             ")
        print("[1] convert audio file to xbox 360 .wav.ckd")
        print(" ")
        print("[2] convert durango (xbox one) .gesture to x360")
        print(" ")
        print("[3] convert .dds to x360 textures/pictos")
        print(" ")
        print("[4] convert video for x360.webm")
        print(" ")
        print("[0] exit")
        print("                             ")
        option = input("enter your choice: ")

        if option == "1":
            set_codename()

            print("select an audio file...")
            openFile = Tk.Tk()
            openFile.withdraw()  # Oculta a janela do Tkinter
            inputfile = filedialog.askopenfilename(
            initialdir=str(pathlib.Path().absolute()),
            title="select your audio file",
            filetypes=[("Audio/Video files", "*.mp4 *.bik *.webm *.avi *.mkv *.mov *.wav *.ogg *.mp3 *.m4a *.opus *.flac")]
        )
            
            audioType = input('do you want convert a normal audio or amb? (audio / amb): ')
            if (audioType == "audio"):
                convert_xma(inputfile, codename, main)
            elif (audioType == "amb"):
                ambType = input('is intro or outro?: ')
                convert_xma_amb(inputfile, codename, main)

        elif option == "2":
            set_codename()
            input_folder = f"{main}\\input"
            convert_gesture(input_folder="input", output_folder="output")

        elif option == "3":
            codename = input('codename: ')
            input_folder = filedialog.askdirectory(initialdir=str(pathlib.Path().absolute()), title="select your texture/picto folder")
            textureType = input('you want to convert pictos or menuart (p / m): ')
            if (textureType == "p"):
                convert_pictos()
            elif (textureType == "m"):
                convert_menuart()

        elif option == "4":
            codename = input('codename: ')
            print("select an video file...")
            openFile = Tk.Tk()
            openFile.withdraw()  # Oculta a janela do Tkinter
            video_path = filedialog.askopenfilename(
                initialdir=str(pathlib.Path().absolute()),
                title="select your video file",
                filetypes=[("Video (.mp4 / .bik / .webm / .avi / .mkv / .mov)", "*.mp4 *.bik *.webm *.avi *.mkv *.mov")]
            )

            webm(codename, video_path)

        elif option == "0":
            print("closing python, have a good day !")
            break