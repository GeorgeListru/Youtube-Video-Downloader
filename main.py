import tkinter as tk
from tkinter import ttk
from urllib.request import urlopen
from pytube import YouTube
import urllib.parse as parse
from io import BytesIO
from PIL import Image, ImageTk
from pathlib import Path
from os import path,startfile

###Creare ferestrei aplicatiei
window = tk.Tk()
window.config(background="#1A1C1D")
window.minsize(width=800, height=400)
window.maxsize(width=800, height=400)
window.title("Video Downloader")
###

##Preluarea imaginii din folder folosind libraria PIL, redimensionarea
# acesteia conform dimensiunilor ferestrei si plasarea in aplicatie
image = Image.open("default_yt_img.png")
width, height = image.size
image = image.resize((round(250 / height * width), round(250)))
photo = ImageTk.PhotoImage(image)
label = tk.Label(image=photo, border=0, width=800, background="#1A1C1D")
label.grid(column=0, row=0, sticky="", columnspan=2, pady=15)
##

##Crearea input-ului pentru introducerea link-ului
Link_Entry = tk.Entry(window, font=("Arial", 10), width=80, fg="#DBD8D3", background="#303030", border=0,
                      highlightcolor="white")
Link_Entry.grid(column=0, row=1, ipady=6, ipadx=10, pady=10, sticky="e")
##

##Subprogram ce verifica daca adresa introdusa este cea de la youtube,
# iar in caz ca da, va extrage id-ul videoclipului pentru a putea fi preluata de pytube
def video_id(value):
    query = parse.urlparse(value)
    if query.hostname == 'youtu.be':
        return query.path[1:]
    if query.hostname in ('www.youtube.com', 'youtube.com'):
        if query.path == '/watch':
            p = parse.parse_qs(query.query)
            return p['v'][0]
        if query.path[:7] == '/embed/':
            return query.path.split('/')[2]
        if query.path[:3] == '/v/':
            return query.path.split('/')[2]
    return None
##

##Subprogram pentru cautarea videoclipului pe youtube si afisarea tuturor rezultatelor primite
#in aplicatie, precum si afisarea butoanelor de optiuni ale calitatii si butonul de descarcare
def Search():
    ##extragerea thumbnail-ului videoclipului si afisarea in fereastra
    try:
        link = str(Link_Entry.get())
        URL = f"https://img.youtube.com/vi/{video_id(link)}/hqdefault.jpg"
        u = urlopen(URL)
        raw_data = u.read()
        u.close()
        im = Image.open(BytesIO(raw_data))
    except:
        #in caz ca nu functioneaza, vom sterge continutul din entry si il vom colora diferit pentru
        #o secuda, dupa care va veni la culoarea normala
        Link_Entry.config(background="#660900")

        def normal():
            Link_Entry.config(background="#303030")
            Link_Entry.delete(0, "end")

        window.after(1000, normal)
        ##
    ##
    else:
        ##in caz ca functioneaza, imaginea va fi plasata in aplicatie
        width, height = im.size
        im = ImageTk.PhotoImage(im.resize((round(250 / height * width), round(250))))
        label.configure(image=im)
        label.image = im

        n = tk.StringVar(window)
        ##extragerea rezolutiilor videoclipului si afisarea acestora intr-un widget numit options
        resolutions = []
        for i in YouTube(link).streams.filter(mime_type="video/mp4"):
            if i.resolution:
                resolutions.append(int(str(i.resolution).replace("p", "")))
        max_resolution = max(resolutions)
        values = ["2160p", "1440p", "1080p", "720p", "480p", "360p", "240p", "144p"]
        #extragerea doar rezolutiilor posibile din intreaga lista de rezolutii
        values = tuple(values[values.index(f"{max_resolution}p"):])
        value_inside = tk.StringVar(window)
        value_inside.set("Select an Option")
        #afisarea lista de optiuni
        options = ttk.Combobox(window, width=16, font=("Calibri", "10"), textvariable=value_inside, values=values)
        options.grid(column=0, row=2, ipady=2, sticky="e", pady=4)
        ##
        ##Crearea unui progress bar pentru a afisa progresul descarcarii videoclipului
        s = ttk.Style()
        s.theme_use("default")
        s.configure("TProgressbar", thickness=20)
        progess_bar = ttk.Progressbar(window, length=521, orient=tk.HORIZONTAL, mode='determinate',
                                      style="TProgressbar")
        progess_bar.grid(column=0, row=2, sticky="w", padx=31, pady=4)
        ##
        ##Crearea unei metode ce descarca videoclipul, actualizeaza bara de progres si deschides
        #ferestrea de descarcari in momentul finalizarii descarcarii
        def downloadVideo():
            #deciderea numelui fisierului. In caz ca exista un nume similar, il va schimba pe cel
            #ce se descarca
            downloads_path = str(Path.home() / "Downloads")
            file_name = str(YouTube(link).title)
            file_name_temp=file_name
            i = 1
            while path.exists(path.join(downloads_path, file_name_temp) + ".mp4"):
                file_name_temp = file_name
                file_name_temp += str(i)
                i += 1
            file_name=file_name_temp
            progess_bar["value"]=0
            #functie ce actualizeaza bara de progres
            def on_progress(chunk, file_handler, remaining):
                #calcularea procentajului pe baza marimii fisierului si cat a mai ramas de descarcat
                percent = (100 * (file_size - remaining)) / file_size
                progess_bar["value"] = percent
                window.update()
            videos = YouTube(link, on_progress_callback=on_progress)
            video = videos.streams.filter(res=value_inside.get(),mime_type="video/mp4").first()
            #Descarcarea fisierului si deschiderea folderului de descarcari
            global file_size
            file_size = video.filesize
            video.download(downloads_path, filename=file_name+".mp4")
            startfile(Path.home() / "Downloads")
        #plasarea butonului de descarcare
        download_btn = tk.Button(text="DOWNLOAD", command=downloadVideo, width=10, font=("Arial", "8","bold"),
                                 background="#ffffff",foreground="#660900",relief="ridge")
        download_btn.grid(column=1, row=2, sticky="w", padx=2, ipadx=2, pady=4)

#Plasarea butonului de cautare
Search_btn = tk.Button(width=10, height=1, background="#660900", text="SEARCH", border=0, fg="#DBD8D3",
                       font=("Arial", 10),activebackground="#7a0b00", relief="ridge", command=Search)
Search_btn.grid(column=1, row=1, ipady=2.5, sticky="w")

file_size = 0
window.mainloop()
