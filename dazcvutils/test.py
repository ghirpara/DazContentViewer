import argparse
from common import cleanify

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

argmap=vars(args)
kvarglist=["script_args", "cli_args"]
print (argmap)
print ("+++++++++++++++++++++++++++++++++")
print (cleanify(argmap, kvarglist))
