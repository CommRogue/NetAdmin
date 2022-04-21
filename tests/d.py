import typing

def installer_dialog() -> typing.Tuple:
    import PySimpleGUI as sg
    import textwrap

    sg.theme('DarkAmber')   # Add a touch of color

    column_to_be_centered = [  [sg.Text('NetAdmin Manual Configurator', font=("Arial", 24))],
                    [sg.Text(' '.join(textwrap.wrap("Welcome to the NetAdmin manual installation. This window is shown because the manual installation option was chosen in the client executable creation process.", 60)), size=(60, None), font=("Arial", 10))],
                    [sg.Text("Address Type: ", font=("Arial", 12))],
                    [sg.Radio("IP", 1, key='-TYPE-', default=True, font=("Arial", 11)), sg.Radio("Hostname (DNS-Resolvable)", 1, key='-TYPE-', font=("Arial", 11))],
                    [sg.Text("Address:", font=("Arial", 12))],
                    [sg.InputText(key="-ADDRESS_IN-")],
                    [sg.Text("Port (default 49152):", font=("Arial", 12))],
                    [sg.InputText(key="-PORT_IN-", size=(10, 10))],
                    [sg.Button('OK')]]

    layout = [[sg.VPush()],
                  [sg.Push(), sg.Column(column_to_be_centered,element_justification='c'), sg.Push()],
                  [sg.VPush()]]

    window = sg.Window('Window Title', layout, size=(500,300), finalize=True)

    window.TKroot.title("NetAdmin Manual Configurator")


    # Event Loop to process "events" and get the "values" of the inputs
    while True:
        event, values = window.read()
        if event == 'OK': # if user closes window or clicks cancel
            if values['-PORT_IN-'] != "" and values['-ADDRESS_IN-'] != "":
                try:
                    int(values['-PORT_IN-'])
                except:pass
                else:
                    window.close()
                    return values['-ADDRESS_IN-'], values["-PORT_IN-"], "ip" if values['-TYPE-'] else "hostname"
        elif event == sg.WIN_CLOSED:
            return -1, -1, -1

print (installer_dialog())