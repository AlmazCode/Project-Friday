"""
The main file to start assistant.

by: AlmazCode
discord: almazcode
github: https://github.com/AlmazCode
"""

import threading

from core.assistant import Assistant
from core.equalizer.equalizer_visualizer import EqualizerVisualizer
from core.config import VERSION

equalizer = EqualizerVisualizer(
    caption=f"Project Friday {VERSION}",
    width=1280,
    height=720
)

assistant = Assistant(
    equalizer=equalizer
)
assistant_thread = threading.Thread(target=assistant.listen, daemon=True)
assistant_thread.start()
equalizer.run()