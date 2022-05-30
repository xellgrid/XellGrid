# version_info = (1, 3, 1, "final")

# _specifier_ = {"alpha": "a", "beta": "b", "candidate": "rc", "final": ""}

# __version__ = "%s.%s.%s%s" % (
#     version_info[0],
#     version_info[1],
#     version_info[2],
#     ""
#     if version_info[3] == "final"
#     else _specifier_[version_info[3]] + str(version_info[4]),
# )

import json
from pathlib import Path

__all__ = ["__version__"]

def _fetchVersion():
    HERE = Path(__file__).parent.resolve()

    for settings in HERE.rglob("package.json"): 
        try:
            with settings.open() as f:
                version = json.load(f)["version"]
                return (
                    version.replace("-alpha.", "a")
                    .replace("-beta.", "b")
                    .replace("-rc.", "rc")
                )
        except FileNotFoundError:
            pass

    raise FileNotFoundError(f"Could not find package.json under dir {HERE!s}")

__version__ = _fetchVersion()
