#!/usr/bin/env python3

#from logging import StreamHandler
import argparse
import logging
import os
import sys
import threading

import simulation

from PIL import Image, ImageDraw, ImageFont
from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.ImageHelpers import PILHelper

# Folder location of images
BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.pardir))
IMAGE_PATH = os.path.join(BASE_PATH, "images")
FONT = "/usr/share/fonts/truetype/msttcorefonts/Times_New_Roman.ttf"

# Tests Section BEGIN

def test_pil_helpers(deck):
    if not deck.is_visual():
        return

    test_key_image_pil = PILHelper.create_key_image(deck)
    test_scaled_key_image_pil = PILHelper.create_scaled_key_image(deck, test_key_image_pil)     # noqa: F841
    test_key_image_native = PILHelper.to_native_key_format(deck, test_scaled_key_image_pil)     # noqa: F841

    if deck.is_touch():
        test_touchscreen_image_pil = PILHelper.create_touchscreen_image(deck)
        test_scaled_touchscreen_image_pil = PILHelper.create_scaled_touchscreen_image(deck, test_touchscreen_image_pil)     # noqa: F841
        test_touchscreen_image_native = PILHelper.to_native_touchscreen_format(deck, test_scaled_touchscreen_image_pil)     # noqa: F841


def test_basic_apis(deck):
    with deck:
        deck.open()

        connected = deck.connected()     # noqa: F841
        deck_id = deck.id()     # noqa: F841
        key_count = deck.key_count()     # noqa: F841
        vendor_id = deck.vendor_id()     # noqa: F841
        product_id = deck.product_id()     # noqa: F841
        deck_type = deck.deck_type()     # noqa: F841
        key_layout = deck.key_layout()     # noqa: F841
        key_image_format = deck.key_image_format() if deck.is_visual() else None     # noqa: F841
        key_states = deck.key_states()     # noqa: F841
        dial_states = deck.dial_states()     # noqa: F841
        touchscreen_image_format = deck.touchscreen_image_format() if deck.is_touch() else None     # noqa: F841

        deck.set_key_callback(None)
        deck.reset()

        if deck.is_visual():
            deck.set_brightness(30)

            test_key_image_pil = PILHelper.create_key_image(deck)
            test_key_image_native = PILHelper.to_native_key_format(deck, test_key_image_pil)
            deck.set_key_image(0, None)
            deck.set_key_image(0, test_key_image_native)

            if deck.is_touch():
                test_touchscreen_image_pil = PILHelper.create_touchscreen_image(deck)
                test_touchscreen_image_native = PILHelper.to_native_touchscreen_format(deck, test_touchscreen_image_pil)
                deck.set_touchscreen_image(None)
                deck.set_touchscreen_image(test_touchscreen_image_native, 0, 0, test_touchscreen_image_pil.width, test_touchscreen_image_pil.height)

        deck.close()


def test_key_pattern(deck):
    if not deck.is_visual():
        return

    test_key_image = PILHelper.create_key_image(deck)

    draw = ImageDraw.Draw(test_key_image)
    draw.rectangle((0, 0) + test_key_image.size, fill=(0x11, 0x22, 0x33), outline=(0x44, 0x55, 0x66))

    test_key_image = PILHelper.to_native_key_format(deck, test_key_image)

    with deck:
        deck.open()
        deck.set_key_image(0, test_key_image)
        deck.close()

def run_test(deck, test):
    log.info("Running Test: {}".format(name))
    test(deck)
    log.info("Finished Test: {}".format(name))


tests = {
    "PIL Helpers": test_pil_helpers,
    "Basic APIs": test_basic_apis,
    "Key Pattern": test_key_pattern,
}

# Tests Section END

class mercury_ui:
    def __init__(self) -> None:
        self.simulation = simulation.simulation()
        self.keys = {
            0: {
                "text": "Estonia",
                "icon": "russian-flag.png",
                "callback": self.simulation.estonia_scenario,
                "oneshot": True
            },
            1: {
                "text": "Somalia",
                "icon": "somalian-flag.png",
                "callback": self.simulation.somalian_scenario,
                "oneshot": True
            },
            2: {
                "text": "Jersey",
                "icon": "jersey-flag.png",
                "callback": self.simulation.jersey_scenario,
                "oneshot": False
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

    def display_simulation(self, oneshot=False):
        self.deck.reset()
        with self.deck:
            if oneshot:
                self.deck.set_key_image(
                    1, self._render_key_image(None, FONT, "SINGLE\nINJECTED\nMESSAGE\nSENT")
                )
                self.deck.set_key_image(
                    4, self._render_key_image(os.path.join(IMAGE_PATH, "Return.png"), FONT, "RETURN")
                )
            else:
                self.deck.set_key_image(
                    1, self._render_key_image(None, FONT, "FLOODING\nBUS")
                )
                self.deck.set_key_image(
                    4, self._render_key_image(os.path.join(IMAGE_PATH, "Exit.png"), FONT, "STOP ATTACK")
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
            icon = Image.open(os.path.join(ASSETS_PATH,"blank.png"))
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

    # Prints key state change information, updates rhe key image and performs any
    # associated actions when a key is pressed.
    def key_change_callback(self, deck, key, state):
        if self.under_simulation and key == 4 and state:
            # Stop the simulation
            self.simulation.stop_simulation_threads()
            self.under_simulation = False
            self.setup_keys()
        elif not self.under_simulation and state and key in self.keys:
             # Launch the simulation
            if not key == 5:
                self.display_simulation(oneshot=self.keys[key]["oneshot"])
                self.under_simulation = True
            self.keys[key]["callback"]()



if __name__ == "__main__":
    # Setup Logging
    log = logging.getLogger('logger')
    formatter = logging.Formatter('%(message)s')
    sh = logging.StreamHandler()
    sh.setLevel(logging.INFO)
    sh.setFormatter(formatter)
    log.addHandler(sh)

    # Setup Parser
    parser = argparse.ArgumentParser(description="StreamDeck Library test.")
    parser.add_argument("--run", action="store_true", help="Stream Deck run mode")
    parser.add_argument("--test-all", action='store_true', help="Stream Deck run all tests mode")
    parser.add_argument("--test", type=str, help="Stream Deck run all tests mode")
    args = parser.parse_args()

    # Deal with Streamdeck
    manager = DeviceManager(transport="libusb")
    streamdecks = manager.enumerate()
    print("Found {} Stream Deck(s).\n".format(len(streamdecks)))

    # Basic Checks
    if len(streamdecks) < 1:
        print("Error: Connect Stream Deck!")
        sys.exit()

    for index, deck in enumerate(streamdecks):
        if not deck.is_visual():
            continue

        deck.open()
        deck.reset()

        print("Opened '{}' device (serial number: '{}', fw: '{}')".format(
            deck.deck_type(), deck.get_serial_number(), deck.get_firmware_version()
        ))

        # Set initial screen brightness to 30%.
        deck.set_brightness(100)
        deck.close()


    # Test Logic BEGIN

    if args.test_all:
        for name, test in tests.items():
            run_test(deck, test)

    if args.test:
        test_to_run = {name: test for (name, test) in tests.items() if name == args.test}
        for name, test in test_to_run.items():
            run_test(deck, test)

    # Test Logic END

    # Run Logic
    if args.run:
        ui = mercury_ui()

    # Wait until all application threads have terminated (for this example,
    # this is when all deck handles are closed).
    for t in threading.enumerate():
        try:
            t.join()
        except RuntimeError:
            pass
