# Tkinter DSL mapping template
TKINTER_MAPPING = """
component Window:
    property title = $title
    property width = $width or 400
    property height = $height or 300

    template:
        window = tk.Tk()
        window.title("{$title}")
        window.geometry("{$width}x{$height}")
        {children}
        window.mainloop()

component Button:
    property text = $text or "Button"
    property x = $x or 0
    property y = $y or 0
    property width = compute_width($text, 10)
    property height = 30
    property command = $command

    template:
        button_{$id} = tk.Button(window, text="{$text}", width={$width // 10})
        button_{$id}.place(x={$x}, y={$y})
        {if $command then "button_{$id}.config(command=" + $command + ")" else ""}

component Label:
    property text = $text or ""
    property x = $x or 0
    property y = $y or 0

    template:
        label_{$id} = tk.Label(window, text="{$text}")
        label_{$id}.place(x={$x}, y={$y})
"""

# Textual DSL mapping template
TEXTUAL_MAPPING = """
component Window:
    property title = $title

    template:
        class {capitalize($title)}App(App):
            CSS = \"\"\"
            Screen {
                align: center middle;
            }
            \"\"\"

            def compose(self) -> ComposeResult:
                {children}

        if __name__ == "__main__":
            app = {capitalize($title)}App()
            app.run()

component Button:
    property text = $text or "Button"

    template:
        yield Button("{$text}", id="{lowercase($text)}_button")

component Label:
    property text = $text or ""

    template:
        yield Label("{$text}")
"""
