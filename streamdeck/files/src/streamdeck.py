#!/usr/bin/env python3

#from logging import StreamHandler
import argparse
import logging
import os
import sys
import threading
import signal

import streamdeck_test
import simulation

from PIL import Image, ImageDraw, ImageFont
from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.ImageHelpers import PILHelper

# Folder location of images
BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.pardir))
IMAGE_PATH = os.path.join(BASE_PATH, "images")
FONT = "/usr/share/fonts/truetype/msttcorefonts/Times_New_Roman.ttf"

class streamdeck:
    def __init__(self) -> None:
        signal.signal(signal.SIGINT, self.ctrl_c_handler)
        self.under_simulation = False
        self.simulation = simulation.simulation()
        self.keys = {
            0: {
                "text": "Estonia",
                "icon": "russian-flag.png",
                "callback": self.simulation.estonia_scenario,
            },
            1: {
                "text": "Somalia",
                "icon": "somalian-flag.png",
                "callback": self.simulation.somalian_scenario,
            },
            2: {
                "text": "Jersey",
                "icon": "jersey-flag.png",
                "callback": self.simulation.jersey_scenario,
            },
        }

        try:
            self.deck = DeviceManager().enumerate()[0]
            self.deck.open()
            self.deck.reset()
        except IndexError:
            raise Exception("Stream Deck Not Found!")

        self.deck.set_key_callback(self.key_change_callback)
        self.setup_keys()

    def ctrl_c_handler(self, sig, frame):
        print('Caught SIGINT signal, exiting streamdeck application!')
        self.deck.close()
        sys.exit(0)

    def setup_keys(self):
        self.deck.reset()
        for k in self.keys:
            self.setup_key(k, self.keys[k]["icon"], self.keys[k]["text"])

    def setup_key(self, key, image, text):
        with self.deck:
            self.deck.set_key_image(
                key,
                self._render_key_image(os.path.join(IMAGE_PATH, image), FONT, text),
            )

    def display_simulation(self):
        self.deck.reset()
        with self.deck:
            self.deck.set_key_image(
                1, self._render_key_image(None, FONT, "SIMULATION\nSTARTED")
            )
            self.deck.set_key_image(
                4, self._render_key_image(os.path.join(IMAGE_PATH, "right-arrow.png"), FONT, "RESET")
            )

    def _render_key_image(self, icon_filename, font_filename, label_text):
        # Resize the source image asset to best-fit the dimensions of a single key,
        # leaving a margin at the bottom so that we can draw the key title
        # afterwards.
        if icon_filename is not None:
            icon = Image.open(icon_filename)
            image = PILHelper.create_scaled_image(self.deck, icon, margins=[0, 0, 20, 0])

            # Load a custom TrueType font and use it to overlay the key index, draw key
            # label onto the image a few pixels from the bottom of the key.
            draw = ImageDraw.Draw(image)
            font = ImageFont.truetype(font_filename, 12)
            draw.text(
                (image.width / 2, image.height - 10),
                text=label_text,
                font=font,
                anchor="mm",
                fill="white",
            )

        else:
            icon = Image.open(os.path.join(IMAGE_PATH,"blank.png"))
            image = PILHelper.create_scaled_image(self.deck, icon)

            # Load a custom TrueType font and use it to overlay the key index, draw key
            # label onto the image a few pixels from the bottom of the key.
            draw = ImageDraw.Draw(image)
            font = ImageFont.truetype(font_filename, 12)
            draw.multiline_text(
                (image.width/2, image.height/2),
                text=label_text,
                font=font,
                anchor="mm",
                align="center",
                fill="white",
            )

        return PILHelper.to_native_format(self.deck, image)

    # Prints key state change information, updates the key image and performs any
    # associated actions when a key is pressed.
    def key_change_callback(self, deck, key, state):
        if self.under_simulation and key == 4 and state:
            self.under_simulation = False
            self.setup_keys()
            self.simulation.kill_simulation()
        elif not self.under_simulation and state and key in self.keys:
            self.display_simulation()
            self.under_simulation = True
            self.keys[key]["callback"]()

    def run(self):
        while True:
            pass


if __name__ == "__main__":
    result = streamdeck_test.test_main()
    if result:
        sys.exit()

    control = streamdeck()
    control.run()

    # Wait until all application threads have terminated (for this example,
    # this is when all deck handles are closed).
    for t in threading.enumerate():
        try:
            t.join()
        except RuntimeError:
            pass
