from library.dbmodules.cmds import get_cmd_enabled

class cmd:
    def __init__(self, cmd_name:str):
        self.cmd_name = cmd_name

    def is_enabled(self):
        return get_cmd_enabled(self.cmd_name)