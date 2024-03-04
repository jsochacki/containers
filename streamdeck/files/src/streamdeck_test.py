#!/usr/bin/env python3

import argparse
import logging
import os
import sys

from PIL import Image, ImageDraw, ImageFont
from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.ImageHelpers import PILHelper

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

def run_test(deck, test, name, log):
    log.info("Running Test: {}".format(name))
    test(deck)
    log.info("Finished Test: {}".format(name))

def setup_parser():
    # Setup Parser
    parser = argparse.ArgumentParser(description="StreamDeck Library test.")
    parser.add_argument("--run", action="store_true", help="Stream Deck run mode")
    parser.add_argument("--test-all", action='store_true', help="Stream Deck run all tests mode")
    parser.add_argument("--test", type=str, help="Stream Deck run all tests mode")
    args = parser.parse_args()
    return args

def setup_logger():
    # Setup Logging
    log = logging.getLogger('logger')
    formatter = logging.Formatter('%(message)s')
    sh = logging.StreamHandler()
    sh.setLevel(logging.INFO)
    sh.setFormatter(formatter)
    log.addHandler(sh)
    return log

def basic_checks(streamdecks):
    # Deal with Streamdeck
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

def test_main():
    test_was_run = False
    args = setup_parser()
    log = setup_logger()

    manager = DeviceManager(transport="libusb")
    streamdecks = manager.enumerate()

    basic_checks(streamdecks)

    deck = streamdecks[0]

    if args.test_all:
        test_was_run = True
        for name, test in tests.items():
            run_test(deck, test, name, log)

    if args.test:
        test_was_run = True
        test_to_run = {name: test for (name, test) in tests.items() if name == args.test}
        for name, test in test_to_run.items():
            run_test(deck, test, name, log)

    return test_was_run

tests = {
    "PIL Helpers": test_pil_helpers,
    "Basic APIs": test_basic_apis,
    "Key Pattern": test_key_pattern,
}


if __name__ == "__main__":
    test_main()

