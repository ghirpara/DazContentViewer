import sys
import argparse
import subprocess
import common
import tempfile
from common import logger

class StudioBridge:

    def __init__(self, args):
        print(f"+++++Begin args = {args}")


        ignore_keys = ["daz_path"]

        valid_keys = ["resetDefaults",
                      "noDefaultScene",
                      "logSize",
                      "instanceName",
                      "cleanOnLaunch",
                      "cleanOnExit",
                      "copyAppSettings",
                      "copySessionUI",
                      "allowRemote",
                      "autoInstallMissing",
                      "logMissingProduct",
                      "logModifiedAssets",
                      "noEmitLogMessages",
                      "noPrompt",
                      "headless"]

        xargs=[]

        cli_args=args['cli_args']
        for key in cli_args:
            if key in valid_keys:
                xargs.append(f"-{key}")
                if cli_args[key] != '':
                    xargs.append(cli_args[key])
            elif key not in ignore_keys:
                logger.warning(f"Unknown cli key {key} ignored.")

        self.exe = cli_args.get('daz_path', "c:/Program Files/DAZ 3D/DAZStudio4/DAZStudio.exe")
        self.script = cli_args['scriptfile']

        script_args=args['script_args']
        for arg in script_args:
            xargs.append("-scriptArg")
            xargs.append(f"{arg}={script_args[arg]}")


        xargs.insert(0, self.exe)
        xargs.append(self.script)

        self.xargs = xargs

        logger.info (f"StudioBridge: Init: XARGS={self.xargs}")

    def execute(self, args=None):

        fullargs = self.xargs.copy()

        if args is not None:
            fullargs += args

        logger.info (f"StudioBridge: Execute: Call with XARGS={fullargs}")

        subprocess.run(fullargs, shell=True, check=False)

        logger.info (f"Call completed. Checking for data file.")

        
if __name__ == '__main__':        

    parser = argparse.ArgumentParser(
        prog="StudioBridge",
        description="Manager class for executing a specified DAZ script through the command line interface.")

    parser.add_argument('scriptfile')    

    parser.add_argument('-d', '--daz-path', default="C:/Program Files/DAZ 3D/DAZStudio4/DAZStudio.exe",
                        help="Path to the DAZStudio.exe file")

    parser.add_argument('-c', '--cli-args', 
                        metavar="KEY=VALUE", 
                        action="append",
                        default=[],
                        help="""
                        Command line arguments to DAZ CLI interface. 
                        See http://docs.daz3d.com/doku.php/public/software/dazstudio/4/referenceguide/tech_articles/command_line_options/start for a list of values.
                        """
                        )
    
    parser.add_argument('-s', '--script-args', 
                        action="append",
                        default=[],
                        help="scriptArgs to pass to the script. Each argument corresponds to an element in the App.scriptArg array")
    
    parser.add_argument('-n', '--no-command',
                        action="store_true",
                        help="If specified print out the command line to be executed, but don't actually run it.")
    args = parser.parse_args()

 

    bridge = StudioBridge(common.cleanify(vars(args), ["script_args", "cli_args"]))

    if not args.no_command:
        bridge.execute()
    else:
        logger.info("Did not send command to DAZ Studio since -n was specified.")
    
