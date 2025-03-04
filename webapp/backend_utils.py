from lib.custom_logger import get_custom_logger

logger = get_custom_logger(
    __file__,
    __name__,
)


def map_config(contents: str):
    lines = contents.split("\n")
    cfg = {}
    for line in lines:
        logger.debug(line)
        components = line.split("=")
        if len(components) == 2:
            cfg[components[0].strip()] = components[1].strip()
        if len(components) == 3:
            cmd, target, file = components
            if cmd == "setfile":
                if "files" not in cfg:
                    cfg["files"] = {}
                cfg["files"][target.strip()] = file.strip()
    return cfg
