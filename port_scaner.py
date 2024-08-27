import PySimpleGUI as sg
from contextlib import redirect_stdout
import socket
import platform
import ctypes
import os
import pyperclip
import subprocess
import platform
from pathlib import Path
import tarfile

# Funciones
            
def is_host_reachable(host):
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, '1', host]
    try:
        output = subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        if output.returncode == 0:
            return True
        else:
            return False
    except Exception as e:
        print(f"ERROR: Fallo en chequeo de ping")
        return False
        
def targz_compress(_arch_carpeta_entrada, _arch_salida):
    with tarfile.open(_arch_salida, mode="w:gz") as tar:
        tar.add(_arch_carpeta_entrada, arcname=os.path.basename(_arch_carpeta_entrada))
        tar.close()

def stdpublishr_upload(_nexusurl, _file_folder):
    #command = ['std-publishr.exe --url ', _nexusurl, '-f', _file_folder]
    if _file_folder.exists():
        targz_compress(_file_folder + '.tar.gz', _file_folder)
        
def ports_to_list(_ports):
    _port_list = []
    for port in _ports.split(','):
        if "-" in port:
            _vport = port.split('-')
            for _v in range(int(_vport[0]),int(_vport[1])+1):
                _port_list.append(_v)
        else:
            _port_list.append(int(port))
    return _port_list
    
def check_pts(_host, _port_list):
    open_ports = []
    for port in _port_list:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket.setdefaulttimeout(1)
        result = sock.connect_ex((_host, port))
        if result == 0:
            open_ports.append(port)
        sock.close()
    return open_ports
    
def make_dpi_aware():
    if platform.system() == "Windows" and int(platform.release()) >= 8:
        ctypes.windll.shcore.SetProcessDpiAwareness(True)
        
# Ventana

tab1_layout = [
               [sg.Text("Host/Ip "), sg.InputText(socket.gethostbyname(socket.gethostname()), key='IN1', expand_x=True)],
               [sg.Text("Puertos"), sg.InputText("20-22,80,443",key='IN2', expand_x=True)],
               [sg.Button('Escanear', key='ESCANPORT')]
              ]

tab2_layout = [
               [sg.Text("Nexus URL"), sg.InputText('https://nexus.cloudint.afip.gob.ar/nexus/repository/papiro-raw/papiro/papiro-data-input/1.7.3/papiro-data-input-1.7.3.tar.gz', key='_IN100_', expand_x=True)],
               [sg.Frame('Subir archivo ó carpeta',[
                   [sg.Radio('Upload de archivo', key='_RADIO1_', group_id=1, default=True), sg.Radio('Upload de directorio', key='_RADIO2_', group_id=1), sg.Radio('Upload de comprimido', key='_RADIO3_', group_id=1)],
                   [sg.InputText(key='_INT4_',expand_x=True), sg.FileBrowse('Archivo ', key='_FBROWSE1_'), sg.Button('Upload', key='_BUTTON2_')],
                   [sg.HorizontalSeparator(color='red')],
                   [sg.InputText(key='_INT5_',expand_x=True), sg.FolderBrowse('Directorio', key='_FBROWSE2_'), sg.Button('Upload',  key='_BUTTON3_')],
                   [sg.HorizontalSeparator(color='red')],
                   [sg.InputText(key='_INT6_',expand_x=True), sg.FileBrowse('Comprimido', key='_FBROWSE3_',file_types=(("Comprimidos TAR GZ", "*.tar.gz"),("Comprimidos GZ", "*.gz"),("Comprimidos ZIP", "*.zip"),)), sg.Button('Upload',  key='_BUTTON4_')]], expand_x=True)],
              ]
              
layout = [ [sg.TabGroup([
           [sg.Tab('Escaneo puertos', tab1_layout, expand_x=True, expand_y=False)],
           [sg.Tab('Nexus_upload', tab2_layout, expand_x=True)]], tooltip='TIP2', expand_x=True,  expand_y=False)],
           [#sg.Button('Copiar a clipboard', key='CPTOCLIP'), 
            sg.Button('Salir', expand_y=False), 
            sg.Button('Limpiar salida',  expand_y=False, key='CLEARSCR')],
           [sg.Output(key='OUTPUT1', expand_x=True, expand_y=True)],
           [sg.VPush()],
           [sg.Push(), sg.Sizegrip()]
         ]

# Create the Window
window = sg.Window('Data Tool Implementaciones', layout, finalize=True, resizable=True)

# Event Loop to process "events" and get the "values" of the inputs
stop = False
while True:
    make_dpi_aware()
    event, values = window.read(timeout=100)
    
    window.Refresh()

    # TAB 1
    # if user closes window or clicks cancel
    if event == sg.WIN_CLOSED or event == 'Salir':
        break
        
    if event == 'CLEARSCR':
            window['OUTPUT1'].Update('')
    
    if event == 'ESCANPORT':          
        tag_selection = ['ESCANPORT','CLEARSCR']
        [window[i].update(disabled=True) for i in tag_selection]
               
        if is_host_reachable(values['IN1']) == False:
            print('El host {} no es accesible por lo que no se pueden escanear sus puertos'.format(values['IN1']))
        elif any(puerto > 65536 for puerto in ports_to_list(values['IN2'])) == True:
            print('Error: No existe un puerto mayor a 65.535, verifique el parametro **Puertos**')
        else:
            print('Escaneando puertos {} para host {}'.format(values['IN2'],values['IN1']))
            salida = check_pts(values['IN1'], ports_to_list(values['IN2']))
            print('Los puertos abiertos son: {}\n'.format(salida))
            
        [window[i].update(disabled=False) for i in tag_selection]
        
    #if event == 'CPTOCLIP':
    #    pyperclip.copy(values['OUTPUT1'])
    
    # TAB 2
    
    if values['_RADIO1_']:
       window['_INT4_'].update(disabled=False, background_color='white')
       window['_BUTTON2_'].update(disabled=False)
       window['_FBROWSE1_'].update(disabled=False)
       window['_INT5_'].update(disabled=True, background_color='grey')
       window['_BUTTON3_'].update(disabled=True)
       window['_FBROWSE2_'].update(disabled=True)
       window['_INT6_'].update(disabled=True, background_color='white')
       window['_BUTTON4_'].update(disabled=True)
       window['_FBROWSE3_'].update(disabled=True)

    if values['_RADIO2_']:
       window['_INT4_'].update(disabled=True, background_color='grey')
       window['_BUTTON2_'].update(disabled=True)
       window['_FBROWSE1_'].update(disabled=True)
       window['_INT5_'].update(disabled=False, background_color='white')
       window['_BUTTON3_'].update(disabled=False)
       window['_FBROWSE2_'].update(disabled=False)
       window['_INT6_'].update(disabled=True, background_color='white')
       window['_BUTTON4_'].update(disabled=True)
       window['_FBROWSE3_'].update(disabled=True)

    if values['_RADIO3_']:
       window['_INT4_'].update(disabled=True, background_color='grey')
       window['_BUTTON2_'].update(disabled=True)
       window['_FBROWSE1_'].update(disabled=True)
       window['_INT5_'].update(disabled=True, background_color='white')
       window['_BUTTON3_'].update(disabled=True)
       window['_FBROWSE2_'].update(disabled=True)
       window['_INT6_'].update(disabled=False, background_color='white')
       window['_BUTTON4_'].update(disabled=False)
       window['_FBROWSE3_'].update(disabled=False)
       
    if event == '_BUTTON2_':
        path, filename = os.path.split(os.path.abspath(values['_INT4_']))
        _output_targz=os.path.join(path, filename + str('.tar.gz'))
        targz_compress(os.path.join(path, filename), _output_targz)
    
    if event == '_BUTTON3_':
        _output_targz=os.path.join(values['_INT5_'] + str('.tar.gz'))
        targz_compress(values['_INT5_'], _output_targz)

window.close()
