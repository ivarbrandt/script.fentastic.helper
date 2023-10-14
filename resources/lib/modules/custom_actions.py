import xbmc, xbmcgui, xbmcvfs
import xml.etree.ElementTree as ET
from xml.dom import minidom

KEYMAP_LOCATION = "special://userdata/keymaps/"
POSSIBLE_KEYMAP_NAMES = ["gen.xml", "keyboard.xml"]


def set_image():
    image_file = xbmcgui.Dialog().browse(
        2, "Choose Custom Background Image", "network", ".jpg|.png|.bmp", False, False
    )
    if image_file:
        xbmc.executebuiltin("Skin.SetString(CustomBackground,%s)" % image_file)


def get_current_keymap_path():
    for keymap_name in POSSIBLE_KEYMAP_NAMES:
        keymap_path = xbmcvfs.translatePath(KEYMAP_LOCATION + keymap_name)
        if xbmcvfs.exists(keymap_path):
            return keymap_path
    return None


def get_parent_map(tree):
    return {c: p for p in tree.iter() for c in p}


def modify_keymap():
    xbmc.log("Modify Keymap Function Called", 2)

    keymap_path = get_current_keymap_path()

    # Return if the keymap doesn't exist
    if not keymap_path:
        return

    tree = ET.parse(keymap_path)
    root = tree.getroot()

    parent_map = get_parent_map(tree)

    def has_play_trailer_tag(tag):
        return tag.text == "RunScript(script.fentastic.helper, mode=play_trailer)"

    play_pause_tags = [
        tag
        for tag in root.findall(".//play_pause[@mod='longpress']")
        if has_play_trailer_tag(tag)
    ]

    # If the specific skin setting is enabled
    setting_value = xbmc.getCondVisibility("Skin.HasSetting(Enable.OneClickTrailers)")
    xbmc.log(f"Skin setting Enable.OneClickTrailers: {setting_value}", 2)

    if xbmc.getCondVisibility("Skin.HasSetting(Enable.OneClickTrailers)"):
        # If the tag doesn't exist, create and inject it
        if not play_pause_tags:
            keymap_tag = root
            global_tag = keymap_tag.find("global")
            if global_tag is None:
                global_tag = ET.SubElement(keymap_tag, "global")

            keyboard_tag = global_tag.find("keyboard")
            if keyboard_tag is None:
                keyboard_tag = ET.SubElement(global_tag, "keyboard")

            play_pause_tag = ET.SubElement(keyboard_tag, "play_pause", mod="longpress")
            play_pause_tag.text = (
                "RunScript(script.fentastic.helper, mode=play_trailer)"
            )
    else:
        # If the skin setting is disabled and the tag exists, remove it
        xbmc.log(f"Number of play_pause tags found: {len(play_pause_tags)}", 2)

        for tag in play_pause_tags:
            keyboard_tag = parent_map[tag]
            keyboard_tag.remove(tag)

            # If the parent tags are empty, remove them as well
            if not list(keyboard_tag):
                global_tag = parent_map[keyboard_tag]
                global_tag.remove(keyboard_tag)
                if not list(global_tag):
                    keymap_tag = parent_map[global_tag]
                    keymap_tag.remove(global_tag)
                    if not list(keymap_tag):
                        root.remove(keymap_tag)

    # Write back the modified XML
    xml_string = ET.tostring(root, encoding="utf-8").decode("utf-8")
    pretty_xml = minidom.parseString(xml_string).toprettyxml(
        indent="  "
    )  # 2 spaces for indentation
    pretty_xml = "\n".join(
        [line for line in pretty_xml.split("\n") if line.strip()]
    )  # Remove lines that contain only whitespace
    with xbmcvfs.File(keymap_path, "w") as xml_file:
        xml_file.write(pretty_xml)

    # Notify Kodi to reload its keymaps
    xbmc.executebuiltin("Action(reloadkeymaps)")

    # Notify Kodi to reload its keymaps
    xbmc.executebuiltin("Action(reloadkeymaps)")
