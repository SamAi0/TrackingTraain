import codecs

print("Converting encoding...")
with codecs.open("trackease_export.json", "r", "utf-16") as f_in:
    with codecs.open("trackease_export_utf8.json", "w", "utf-8") as f_out:
        for line in f_in:
            f_out.write(line)
print("Conversion complete.")
