from __future__ import print_function

from cloudmesh.common.console import Console
from cloudmesh.common.debug import VERBOSE
from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command


class BurnCommand(PluginCommand):

    # noinspection PyUnusedLocal
    @command
    def do_burn(self, args, arguments):
        """
        ::

          Usage:
                burn --file=FILE
                burn list

          This command does some useful things.

          Arguments:
              FILE   a file name

          Options:
              -f      specify the file

        """
        arguments.FILE = arguments['--file'] or None

        VERBOSE(arguments)

        if arguments.FILE:
            print("option a")

        elif arguments.list:
            print("option b")

        Console.error("This is just a sample")
        return ""
