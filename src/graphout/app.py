import os
import pathlib

from graphout import default

_DEFAULT_MKDIR = False


class App:

    @classmethod
    def get_path_to_root(cls, *args, mkdir: bool = _DEFAULT_MKDIR) -> str:
        path = pathlib.Path(os.path.dirname(__file__))
        rootPath = os.path.join(path.parent.parent)
        assert rootPath.endswith(f'\\{default.APP_NAME}')

        if not mkdir:
            return os.path.join(rootPath, *args)
        else:
            path = rootPath
            for arg in args:
                path = os.path.join(path, arg)
                if not os.path.exists(path):
                    os.mkdir(path)
            return path

    @classmethod
    def get_path_to_dump(cls, *args, mkdir: bool = _DEFAULT_MKDIR) -> str:
        path = cls.get_path_to_root('_dump', *args, mkdir=mkdir)
        return path

    @classmethod
    def get_path_to_src(cls, *args, mkdir: bool = _DEFAULT_MKDIR) -> str:
        path = cls.get_path_to_root('src', *args, mkdir=mkdir)
        return path

    @classmethod
    def get_path_to_measurement_result(cls, folder_name: str, file_name: str) -> str:
        path = os.getcwd()
        if folder_name != "":
            path = os.path.join(path, folder_name)
            if not os.path.exists(path):
                os.mkdir(path)

        return os.path.join(path, file_name)
