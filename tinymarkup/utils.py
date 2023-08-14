import html

def html_start_tag(tag, **params):
    def fixkey(key):
        if key.endswith("_"):
            return key[:-1]
        else:
            return key

    if params:
        params = [ f'{fixkey(key)}="{html.escape(value)}"'
                   for (key, value) in params.items() ]
        params = " " + " ".join(params)
    else:
        params = ""

    return f"<{tag}{params}>"
