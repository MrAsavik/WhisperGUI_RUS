def bind_copy(widget):
    """
    Позволяет копировать текст с помощью Ctrl+C и Ctrl+С (английская и русская раскладки).
    Работает для ScrolledText и других текстовых полей.
    """
    def on_ctrl_key(event):
        if event.state & 0x4 and event.keysym.lower() in ("c", "с"):
            widget.event_generate("<<Copy>>")

    widget.bind("<KeyPress>", on_ctrl_key)
