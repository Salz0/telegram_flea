import os
import polib


def compile_all_languages(base_locales_path="locales"):
    for lang in os.listdir(base_locales_path):
        lang_path = os.path.join(base_locales_path, lang)
        if os.path.isdir(lang_path):
            lc_messages_path = os.path.join(lang_path, "LC_MESSAGES")
            for file_name in os.listdir(lc_messages_path):
                if file_name.endswith(".po"):
                    po_path = os.path.join(lc_messages_path, file_name)
                    mo_path = os.path.join(lc_messages_path, file_name.replace(".po", ".mo"))
                    compile_po_to_mo(po_path, mo_path)


def compile_po_to_mo(po_path, mo_path):
    po = polib.pofile(po_path)
    po.save_as_mofile(mo_path)
