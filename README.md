# MyCloud App

Very simple and not maintainable script. Main purpose to be a private Cloude storage,
that works from home PC via PyWebIO server to WAN.

Script creates "Data" folder with four folders inside - "Images", "mp3", "Videos", "NonMediaFiles
in the directory the script is launched in.
In those folders script will store uplodaed files depending on its extension, sorted by creation time.

To make the server to be visible from WAN uncomment and use:

    - start_server(main, port=8080, remote_access=True)

    in mian.py

    remote_access=True starts the WAN server and displayes its address in the shell.
    For example:
    Remote access address: https://3xzepr3um5fw.app.pywebio.online
    The address every time is different.


P.S.
The script is written in a very bad way. Without using design patterns and clean code rules.
I worte it for myself in one file, once I needed it to be ready withing several hours.
But it still works:)
Once I will find enough time, I will refactor the code to convert it from the script to a normal application. 