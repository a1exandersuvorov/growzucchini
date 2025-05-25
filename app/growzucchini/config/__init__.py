import os

# from .tomato import Tomato
from .zucchini import Zucchini

profile = os.environ.get("APP_PROFILE", "zucchini").lower()

if profile == "zucchini":
    config = Zucchini()
# elif profile == "tomato":
#     config = Tomato()
else:
    raise ValueError(f"Unknown profile: {profile}")
