import math
import pygame

from .config import BUTTON_COLOR, BUTTON_HOVER_COLOR, TEXT_COLOR


class Button:
    def __init__(self, rect, text, font, callback, icon=None):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.callback = callback
        self.icon = icon
        self.hovered = False

    def _draw_icon(self, surface, kind, rect, color):
        cx, cy = rect.center
        size = min(rect.width, rect.height)
        pad = max(2, size // 8)
        stroke = max(2, size // 10)

        if kind == "play":
            pts = [
                (rect.left + pad, rect.top + pad),
                (rect.left + pad, rect.bottom - pad),
                (rect.right - pad, cy),
            ]
            pygame.draw.polygon(surface, color, pts)
            return

        if kind == "pause":
            bar_w = max(3, size // 5)
            gap = max(3, size // 6)
            h = rect.height - 2 * pad
            r1 = pygame.Rect(cx - gap // 2 - bar_w, rect.top + pad, bar_w, h)
            r2 = pygame.Rect(cx + gap // 2, rect.top + pad, bar_w, h)
            pygame.draw.rect(surface, color, r1)
            pygame.draw.rect(surface, color, r2)
            return

        if kind == "reset":
            radius = (size // 2) - pad - 1
            if radius <= 2:
                return
            arc_rect = pygame.Rect(0, 0, 2 * radius, 2 * radius)
            arc_rect.center = (cx, cy)
            start = math.radians(45)
            end = math.radians(315)
            pygame.draw.arc(surface, color, arc_rect, start, end, stroke)

            ex = cx + radius * math.cos(end)
            ey = cy + radius * math.sin(end)
            tx = -math.sin(end)
            ty = math.cos(end)
            tlen = max(1e-6, math.hypot(tx, ty))
            tx /= tlen
            ty /= tlen

            a = math.radians(-30)
            rtx = tx * math.cos(a) - ty * math.sin(a)
            rty = tx * math.sin(a) + ty * math.cos(a)
            tx, ty = rtx, rty

            nx = -ty
            ny = tx

            head_len = max(8.0, size * 0.26)
            head_w = max(6.0, size * 0.18)

            tip = (int(ex), int(ey))
            base_cx = ex - tx * head_len
            base_cy = ey - ty * head_len
            p1 = (int(base_cx + nx * head_w), int(base_cy + ny * head_w))
            p2 = (int(base_cx - nx * head_w), int(base_cy - ny * head_w))
            pygame.draw.polygon(surface, color, [tip, p1, p2])
            return

        if kind == "save":
            body = rect.inflate(-2 * pad, -2 * pad)
            pygame.draw.rect(surface, color, body, stroke, border_radius=3)
            notch = pygame.Rect(0, 0, int(body.width * 0.42), int(body.height * 0.28))
            notch.topleft = (body.left + 2, body.top + 2)
            pygame.draw.rect(surface, color, notch, stroke, border_radius=2)
            slot = pygame.Rect(0, 0, int(body.width * 0.6), max(3, int(body.height * 0.12)))
            slot.midbottom = (body.centerx, body.bottom - 3)
            pygame.draw.rect(surface, color, slot)
            return

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos) and self.callback:
                self.callback()

    def draw(self, surface):
        color = BUTTON_HOVER_COLOR if self.hovered else BUTTON_COLOR
        pygame.draw.rect(surface, color, self.rect, border_radius=6)
        pad_x = 16
        icon_gap = 10
        icon_size = int(self.rect.height * 0.42)
        icon_size = max(20, min(34, icon_size))
        text_surf = self.font.render(self.text, True, TEXT_COLOR)

        if self.icon:
            icon_rect = pygame.Rect(0, 0, icon_size, icon_size)
            icon_rect.midleft = (self.rect.left + pad_x, self.rect.centery)
            self._draw_icon(surface, self.icon, icon_rect, TEXT_COLOR)
            text_x = icon_rect.right + icon_gap
            text_rect = text_surf.get_rect(midleft=(text_x, self.rect.centery))
        else:
            text_rect = text_surf.get_rect(center=self.rect.center)

        if text_rect.right > self.rect.right - pad_x:
            text_rect.right = self.rect.right - pad_x

        surface.blit(text_surf, text_rect)


class Slider:
    def __init__(self, rect, value=0.0):
        self.rect = pygame.Rect(rect)
        self.value = max(0.0, min(1.0, value))
        self.dragging = False

    def handle_event(self, event):
        changed = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
                changed = True
                self._set_from_mouse(event.pos[0])
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            changed = True
            self._set_from_mouse(event.pos[0])
        return changed

    def _set_from_mouse(self, mx):
        if self.rect.width <= 0:
            return
        rel = (mx - self.rect.x) / float(self.rect.width)
        self.value = max(0.0, min(1.0, rel))

    def draw(self, surface):
        track_rect = pygame.Rect(self.rect.x, self.rect.centery - 2, self.rect.width, 4)
        pygame.draw.rect(surface, (80, 80, 80), track_rect, border_radius=2)
        knob_x = self.rect.x + int(self.value * self.rect.width)
        knob_rect = pygame.Rect(knob_x - 6, self.rect.centery - 8, 12, 16)
        pygame.draw.rect(surface, (180, 180, 180), knob_rect, border_radius=3)


class TextInput:
    def __init__(self, rect, text, font, on_enter=None):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.on_enter = on_enter
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.active = self.rect.collidepoint(event.pos)
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                if self.on_enter:
                    self.on_enter(self.text)
                self.active = False
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                if event.unicode and event.unicode in "0123456789.-eE":
                    self.text += event.unicode

    def draw(self, surface):
        border_color = BUTTON_HOVER_COLOR if self.active else (100, 100, 100)
        pygame.draw.rect(surface, (20, 20, 20), self.rect, border_radius=4)
        pygame.draw.rect(surface, border_color, self.rect, 1, border_radius=4)
        txt_surf = self.font.render(self.text, True, TEXT_COLOR)
        txt_rect = txt_surf.get_rect(midleft=(self.rect.x + 8, self.rect.centery))
        surface.blit(txt_surf, txt_rect)


class Checkbox:
    def __init__(self, rect, label, font, checked, callback):
        self.rect = pygame.Rect(rect)
        self.base_rect = pygame.Rect(rect)
        self.label = label
        self.font = font
        self.checked = checked
        self.callback = callback

    def set_position(self, x, y, w=None, h=None):
        if w is None:
            w = self.base_rect.width
        if h is None:
            h = self.base_rect.height
        self.rect = pygame.Rect(x, y, w, h)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.checked = not self.checked
                if self.callback:
                    self.callback(self.checked)

    def draw(self, surface):
        box_size = self.rect.height - 4
        box_rect = pygame.Rect(self.rect.x, self.rect.y + 2, box_size, box_size)
        pygame.draw.rect(surface, (20, 20, 20), box_rect)
        pygame.draw.rect(surface, (150, 150, 150), box_rect, 1)
        if self.checked:
            inner = box_rect.inflate(-6, -6)
            pygame.draw.rect(surface, BUTTON_HOVER_COLOR, inner)
        label_surf = self.font.render(self.label, True, TEXT_COLOR)
        label_rect = label_surf.get_rect(midleft=(box_rect.right + 10, self.rect.centery))
        surface.blit(label_surf, label_rect)


class ParameterControl:
    def __init__(
        self,
        name,
        unit,
        x,
        y,
        width,
        font_label,
        font_value,
        min_val,
        max_val,
        initial,
        on_change,
        has_slider=True,
        log_scale=False,
    ):
        self.name = name
        self.unit = unit
        self.base_x = x
        self.base_y = y
        self.width = width
        self.font_label = font_label
        self.font_value = font_value
        self.min_val = min_val
        self.max_val = max_val
        self.on_change = on_change
        self.has_slider = has_slider
        self.log_scale = log_scale
        self.value = initial

        self.input_width = 140
        self.input_height = 40

        self.label_surface = self.font_label.render(f"{self.name} ({self.unit})", True, TEXT_COLOR)
        self.label_rect = self.label_surface.get_rect(topleft=(x, y))

        if self.log_scale:
            self.log_min = math.log10(self.min_val)
            self.log_max = math.log10(self.max_val)
        else:
            self.log_min = None
            self.log_max = None

        slider_width = width - (self.input_width + 10) if has_slider else 0
        if has_slider:
            norm = self._value_to_norm(initial)
            self.slider = Slider((x, y, slider_width, 18), value=norm)
        else:
            self.slider = None

        self.text_input = TextInput((x, y, self.input_width, self.input_height), self._format_value(initial), font_value, on_enter=self._on_text_enter)
        self._apply_layout(x, y)

    def get_height(self):
        label_h = self.label_surface.get_height()
        if self.has_slider:
            return label_h + 10 + max(self.input_height, 18) + 12
        return max(label_h, self.input_height) + 12

    def set_position(self, x, y):
        self.base_x = x
        self.base_y = y
        self._apply_layout(x, y)

    def _apply_layout(self, x, y):
        label_h = self.label_surface.get_height()
        if self.has_slider:
            self.label_rect.topleft = (x, y)
            slider_y = y + label_h + 10
            self.slider.rect.topleft = (x, slider_y)
            input_x = x + self.slider.rect.width + 10
            input_y = slider_y - (self.input_height - self.slider.rect.height) // 2
            self.text_input.rect.topleft = (input_x, input_y)
            self.text_input.rect.size = (self.input_width, self.input_height)
        else:
            input_x = x + self.width - self.input_width
            self.text_input.rect.topleft = (input_x, y)
            self.text_input.rect.size = (self.input_width, self.input_height)
            self.label_rect.midleft = (x, y + self.input_height // 2)

    def _format_value(self, v):
        return f"{v:.5g}"

    def _value_to_norm(self, v):
        if self.log_scale:
            lv = math.log10(max(self.min_val, min(self.max_val, v)))
            return (lv - self.log_min) / (self.log_max - self.log_min)
        return (v - self.min_val) / (self.max_val - self.min_val)

    def _norm_to_value(self, norm):
        norm = max(0.0, min(1.0, norm))
        if self.log_scale:
            lv = self.log_min + norm * (self.log_max - self.log_min)
            return 10 ** lv
        return self.min_val + norm * (self.max_val - self.min_val)

    def _apply_value(self, v):
        v = max(self.min_val, min(self.max_val, v))
        self.value = v
        self.text_input.text = self._format_value(v)
        if self.slider:
            self.slider.value = self._value_to_norm(v)
        if self.on_change:
            self.on_change(v)

    def _on_text_enter(self, text):
        try:
            v = float(text.replace(",", "."))
        except ValueError:
            self.text_input.text = self._format_value(self.value)
            return
        self._apply_value(v)

    def handle_event(self, event):
        if self.slider:
            changed = self.slider.handle_event(event)
            if changed:
                v = self._norm_to_value(self.slider.value)
                self._apply_value(v)
        self.text_input.handle_event(event)

    def draw(self, surface):
        surface.blit(self.label_surface, self.label_rect)
        if self.slider:
            self.slider.draw(surface)
        self.text_input.draw(surface)
