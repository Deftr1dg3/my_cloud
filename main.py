#!/usr/bin/env python3


import time
import os
import json
from pywebio.input import *
from pywebio.output import *
from pywebio import start_server, config
from pywebio.session import *
from pywebio_battery import *
from subprocess import run
from style_css import CSS
from hashlib import sha256
from dotenv import load_dotenv
from modules import Log

load_dotenv('.env')

log = Log()

CLOUD_PASSWORD = os.getenv('cloud_password')
CLOUD_FOLDER = 'Data'
CLIENTS = json.load(open('client_history.json'))

def _validate_path(path: str) -> None:
    if not os.path.exists(path):
        os.makedirs(path)

img_path = CLOUD_FOLDER + os.sep + 'Images' + os.sep
vid_path = CLOUD_FOLDER + os.sep + 'Videos' + os.sep
mp3_path = CLOUD_FOLDER + os.sep + 'mp3' + os.sep
nmf_path = CLOUD_FOLDER + os.sep + 'NonMediaFiles' + os.sep

_validate_path(img_path)
_validate_path(vid_path)
_validate_path(mp3_path)
_validate_path(nmf_path)


config(title='MyCloud', css_style=CSS)


def uploadFiles():
    files = file_upload(multiple=True)
    if files:
        try:

            for file in files:
                file_name = file['filename']

                if file_name.endswith('.jpg') or file_name.endswith('.jpeg') or\
                    file_name.endswith('.png') or file_name.endswith('.gif'):

                    with open(img_path + file_name, 'wb') as f:
                        f.write(file['content'])

                elif file_name.endswith('.mp4') or file_name.endswith('.avi') or file_name.endswith('.wmv'):
                    with open(vid_path + file_name, 'wb') as f:
                        f.write(file['content'])

                elif file_name.endswith('.mp3'):
                    with open(mp3_path + file_name, 'wb') as f:
                        f.write(file['content'])

                else:
                    with open(nmf_path + file_name, 'wb') as f:
                        f.write(file['content'])
        except Exception as e:
            raise Exception(e)

        refresh_data()


def onDelete(tpl):
    path, file_name = tpl
    choice = confirm(f'Do you wish to delete - {file_name}')
    if choice:
        run_shell(f'rm -r {path + file_name}')
        toast(f'The file - {file_name} has been deleted', position='right', color='red')
    else:
        toast(f'The file - {file_name} kept', position='right')
    refresh_data()


def put_to_tab(dir):
    path = CLOUD_FOLDER + os.sep + dir + os.sep
    
    files_list = []
    for file in os.listdir(path):
        if not file.startswith(".") and not file.startswith("_"):
            files_list.append(file)
    
    timestamps = [os.path.getctime(path + file) for file in files_list]

    times_and_files = list(zip(timestamps, files_list))
    times_and_files.sort()
    
    tab = []
    count = 1
    for timestamp, file_name in times_and_files[::-1]:
        tab += [[
            count,
            put_file(file_name, content=open(path + file_name, 'rb').read()),
            put_text(time.ctime(timestamp)),
            put_buttons([{'label': 'Delete', 'value': (path, file_name), 'color': 'warning'}], onclick=onDelete)
        ]]
        count += 1
    with use_scope(dir, clear=True):
        put_table(tab, header=['N', 'File', 'Created on', 'Delete'])


def downloadFiles():
    dirs = ('Images', 'Videos', 'mp3', 'NonMediaFiles')
    for dir in dirs:
        put_to_tab(dir)


def refresh_data():
    downloadFiles()


def TopButtons():
    put_row([
        put_column([
            put_markdown('# MyCloud Storage')
        ]), None,
        put_column([
            put_column([put_buttons([{'label': 'logout', 'value': local.ip, 'color': 'info'}], onclick=Logout)])
        ])
    ])
    put_row([
        put_column([
            put_buttons([
                {'label': '__Upload__', 'value': 'upload', 'color': 'warning'},
                {'label': 'Refresh', 'value': 'refresh', 'color': 'success'}
            ], onclick=onTopButtons)
        ]),
        put_column([
            put_scope(name='theme_button')
        ])
    ])
    with use_scope('theme_button', clear=True):
        themeButton()


def Logout(client):
    CLIENTS[local.client_ip]['authorized'] = False
    log.warning(local.client_ip + ' - logout')
    run_js('window.location.reload()')


def onTopButtons(arg):
    if arg == 'upload':
        uploadFiles()
    else:
        refresh_data()


def putTabs():
    put_tabs([
        {'title': 'Images',
         'content': put_scrollable(put_scope(name='Images'), height=500, border=False, keep_bottom=False)},
        {'title': 'Videos',
         'content': put_scrollable(put_scope(name='Videos'), height=500, border=False, keep_bottom=False)},
        {'title': 'MP3', 'content': put_scrollable(put_scope(name='mp3'), height=500, border=False, keep_bottom=False)},
        {'title': 'NonMediaFiles',
         'content': put_scrollable(put_scope(name='NonMediaFiles'), height=500, border=False, keep_bottom=False)}
    ])


def themeButton():

    if CLIENTS[local.client_ip]['theme'] == 'dark':
        with use_scope('theme_button', clear=True):
            put_buttons([{'label': 'Light', 'value': '', 'color': 'light'}],
                        onclick=on_themeButton)
    else:
        with use_scope('theme_button', clear=True):
            put_buttons([{'label': 'Dark', 'value': 'dark', 'color': 'dark'}],
                        onclick=on_themeButton)


def on_themeButton(arg):
    CLIENTS[local.client_ip]['theme'] = arg
    run_js('window.location.reload()')


def authorization():
    if CLIENTS[local.client_ip]['authorized']:
        return

    passwd = str(input(placeholder='Password', type=PASSWORD))
    if str(sha256(passwd.encode()).hexdigest()) == CLOUD_PASSWORD:
        CLIENTS[local.client_ip]['authorized'] = True
        CLIENTS[local.client_ip]['current_theme'] = ''
        log.warning(local.client_ip + ' - login')
        return

    put_error('The password is incorrect !', closable=True)
    return authorization()


def setTheme(new_theme=''):
    global refresh_ind

    current_theme = CLIENTS[local.client_ip]['current_theme']
    CLIENTS[local.client_ip]['theme'] = new_theme

    if new_theme != current_theme:
        CLIENTS[local.client_ip]['current_theme'] = new_theme
        config(title='MyCloud', theme=new_theme, css_style=CSS)
        run_js('window.location.reload()')


def main():
    local.client_ip = info.user_ip

    if not CLIENTS.get(local.client_ip):
        CLIENTS[local.client_ip] = {'authorized': False, 'theme': '', 'current_theme': '',
                                    'last_session': time.strftime('%H:%M:%S_%d/%m/%Y')}

    CLIENTS[local.client_ip]['last_session'] = time.strftime('%H:%M:%S_%d/%m/%Y')
    CLIENTS[local.client_ip]['is_mobile'] = info.user_agent.is_mobile
    CLIENTS[local.client_ip]['is_tablet'] = info.user_agent.is_tablet
    CLIENTS[local.client_ip]['is_pc'] = info.user_agent.is_pc
    CLIENTS[local.client_ip]['device_family'] = info.user_agent.device.family
    CLIENTS[local.client_ip]['os_family'] = info.user_agent.os.family
    CLIENTS[local.client_ip]['origin'] = info.origin

    setTheme(CLIENTS[local.client_ip]['theme'])

    authorization()
    TopButtons()
    putTabs()
    downloadFiles()

    @defer_call
    def onEndSession():

        with open('client_history.json', 'w') as f:
            json.dump(CLIENTS, f, indent=4)


start_server(main, port=8080, debug=True)

# # Make server visible in WAN:
# start_server(main, port=8080, remote_access=True)
