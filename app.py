from textual.app import App, ComposeResult
from textual.widgets import Label, Header, Footer, Static, Button, Input, TextArea
# 1. Import Container
from textual.containers import Horizontal, Vertical, Container
from textual.color import Color
from textual.reactive import reactive
from textual import events
import random
import colorsys

# 2. Change parent class from Static to Container
class ColorBlock(Container):
    """
    Container is better than Static for color blocks because it 
    doesn't try to shrink-wrap text content. It strictly obeys CSS height.
    """
    current_color = reactive(Color(0, 0, 0))

    def watch_current_color(self, old_color: Color, new_color: Color) -> None:
        self.styles.background = new_color

class PalleteItem(Static, can_focus=True):
    
    DEFAULT_CSS = """
    PalleteItem {
        width: 1fr;
        height: auto;
        layout: vertical;
        margin: 1;
        padding: 5;
    }
    
    PalleteItem:focus {
        border: solid yellow;
    }
    
    PalleteItem.locked {
        border: solid red;
    }
    
    #color-block {
        width: 100%;
        height: 20;
        background: black;
        /* No overflow hidden needed for Container */
        border: none;
    }
    
    #lock-status {
        width: 100%;
        height: 2;
        background: $surface-darken-1;
        color: $text;
        text-align: center;
        content-align: center middle;
        text-style: bold;
        border: none;
    }
    
    #info-label {
        width: 100%;
        height: 3;
        background: $surface;
        color: $text;
        text-align: center;
        content-align: center middle;
        padding: 0 1;
        border: none;
    }
    """
    
    def __init__(self, color_name="primary", color_range=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.color_name = color_name
        self.hex_value = "#000000"
        self.locked = False
        self.color_range = color_range or {}
    
    def compose(self) -> ComposeResult:
        # This will now use the Container-based class
        yield ColorBlock(id="color-block")
        yield Label("🔓 UNLOCKED", id="lock-status")
        yield Label(f"{self.hex_value} - {self.color_name}", id="info-label")
    
    def on_mount(self) -> None:
        self.set_color()
    
    def on_click(self, event: events.Click) -> None:
        self.toggle_lock()
    
    def toggle_lock(self):
        self.locked = not self.locked
        lock_label = self.query_one("#lock-status", Label)
        
        if self.locked:
            self.add_class("locked")
            lock_label.update("🔒 LOCKED")
        else:
            self.remove_class("locked")
            lock_label.update("🔓 UNLOCKED")
    
    def set_color(self, color_input=None):
        if self.locked:
            return
        
        if color_input:
            try:
                hex_color = color_input.strip().lstrip('#')
                if len(hex_color) == 3:
                    hex_color = ''.join([c*2 for c in hex_color])
                if len(hex_color) == 6:
                    r = int(hex_color[0:2], 16)
                    g = int(hex_color[2:4], 16)
                    b = int(hex_color[4:6], 16)
                else:
                    return 
            except:
                return 
        else:
            if self.color_range:
                hue_range = self.color_range.get("hue", (0, 360))
                sat_range = self.color_range.get("sat", (0, 100))
                val_range = self.color_range.get("val", (0, 100))
                h = random.randint(hue_range[0], hue_range[1]) / 360.0
                s = random.randint(sat_range[0], sat_range[1]) / 100.0
                v = random.randint(val_range[0], val_range[1]) / 100.0
                r, g, b = [int(x * 255) for x in colorsys.hsv_to_rgb(h, s, v)]
            else:
                r = random.randint(0, 255)
                g = random.randint(0, 255)
                b = random.randint(0, 255)
        
        self.hex_value = f"#{r:02X}{g:02X}{b:02X}"
        
        # Update the reactive variable
        color_block = self.query_one("#color-block", ColorBlock)
        color_block.current_color = Color(r, g, b)
        
        info_label = self.query_one("#info-label", Label)
        info_label.update(f"{self.hex_value} - {self.color_name}")

class PalleteGenerator(App):
    
    BINDINGS = [
        ("p", "randomize_primary", "Primary"),
        ("s", "randomize_secondary", "Secondary"),
        ("t", "randomize_tertiary", "Tertiary"),
        ("a", "randomize_accent", "Accent"),
        ("space", "randomize_all", "Randomize All"),
        ("c", "copy_palette", "Copy CSS"),
    ]
    
    CSS = """
    Screen {
        align: center top;
        overflow-y: auto;
    }
    #palette-container {
        width: 100%;
        height: auto;
        padding: 1;
        layout: horizontal;
    }
    #controls {
        width: 100%;
        height: auto;
        align: center middle;
        padding: 1;
    }
    #input-container {
        width: 100%;
        height: auto;
        align: center middle;
        padding: 1;
        layout: horizontal;
    }
    #input-label {
        width: auto;
        margin: 0 1;
        content-align: center middle;
    }
    #color-input {
        width: 20;
        margin: 0 1;
    }
    #export-container {
        width: 100%;
        height: auto;
        padding: 1;
        layout: horizontal;
        align: center middle;
    }
    #css-output {
        width: 80%;
        height: 10;
        margin: 1;
    }
    Button {
        margin: 1;
        min-width: 16;
    }
    PalleteItem {
        min-width: 15;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="controls"):
            yield Button("Randomize All (Space)", id="randomize", variant="primary")
        with Horizontal(id="input-container"):
            yield Label("Color:", id="input-label")
            yield Input(placeholder="#RRGGBB", id="color-input")
            yield Button("Apply", id="apply-color", variant="success")
        with Horizontal(id="palette-container"):
            yield PalleteItem(color_name="Primary", color_range={"hue": (0, 60), "sat": (60, 100), "val": (40, 90)}, id="primary")
            yield PalleteItem(color_name="Secondary", color_range={"hue": (180, 260), "sat": (40, 80), "val": (50, 90)}, id="secondary")
            yield PalleteItem(color_name="Tertiary", color_range={"hue": (30, 90), "sat": (30, 70), "val": (60, 95)}, id="tertiary")
            yield PalleteItem(color_name="Accent", color_range={"hue": (0, 360), "sat": (70, 100), "val": (50, 100)}, id="accent")
        with Vertical(id="export-container"):
            yield TextArea("/* CSS will appear here */", id="css-output", read_only=True)
            yield Button("Copy CSS to Clipboard (C)", id="copy-css", variant="warning")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "randomize":
            self.action_randomize_all()
        elif event.button.id == "apply-color":
            self.apply_color_input()
        elif event.button.id == "copy-css":
            self.action_copy_palette()

    def action_randomize_primary(self): self.query_one("#primary", PalleteItem).set_color(); self.update_css_output()
    def action_randomize_secondary(self): self.query_one("#secondary", PalleteItem).set_color(); self.update_css_output()
    def action_randomize_tertiary(self): self.query_one("#tertiary", PalleteItem).set_color(); self.update_css_output()
    def action_randomize_accent(self): self.query_one("#accent", PalleteItem).set_color(); self.update_css_output()
    def action_randomize_all(self): self.randomize_all()
    
    def randomize_all(self):
        for item in self.query(PalleteItem): item.set_color()
        self.update_css_output()
    
    def update_css_output(self):
        items = list(self.query(PalleteItem))
        css_lines = [":root {"]
        for item in items:
            var_name = f"--color-{item.color_name.lower()}"
            css_lines.append(f"  {var_name}: {item.hex_value};")
        css_lines.append("}")
        try: self.query_one("#css-output", TextArea).text = "\n".join(css_lines)
        except: pass
    
    def action_copy_palette(self):
        try:
            css_output = self.query_one("#css-output", TextArea)
            original_text = css_output.text
            css_output.text = "CSS copied!\n" + original_text
        except: pass
    
    def apply_color_input(self):
        color_input = self.query_one("#color-input", Input)
        if not color_input.value: return
        try:
            focused = self.focused
            if isinstance(focused, PalleteItem): focused.set_color(color_input.value)
            else:
                for item in self.query(PalleteItem):
                    if not item.locked:
                        item.set_color(color_input.value)
                        break
        except: pass
        color_input.value = ""
        self.update_css_output()

if __name__ == "__main__":
    app = PalleteGenerator()
    app.run()