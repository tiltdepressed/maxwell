import threading
import pygame

from .config import (
    WIDTH,
    HEIGHT,
    FPS,
    LEFT_PANEL_WIDTH,
    RIGHT_PANEL_WIDTH,
    CENTER_PANEL_WIDTH,
    BACKGROUND_COLOR,
    TEXT_COLOR,
    PANEL_BG_COLOR,
    ROPE_COLOR,
    BAR_COLOR,
    COLOR_HEIGHT,
    COLOR_VELOCITY,
    COLOR_EP,
    COLOR_EK_TRANS,
    COLOR_EK_ROT,
    PENDULUM_RADIUS_PIXELS,
    PENDULUM_BAR_Y,
    PENDULUM_START_Y,
    PIXELS_PER_METER,
    SIM_DT,
)
from .ui import Button, ParameterControl
from .simulation import MaxwellWheelSimulation
from .graphs import draw_series_graph
from .plots import snapshot_history, save_plots


def run():
    pygame.init()
    pygame.display.set_caption("Маятник (Колесо Максвелла)")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    font_small = pygame.font.SysFont("arial", 28)
    font_medium = pygame.font.SysFont("arial", 32)
    font_large = pygame.font.SysFont("arial", 40)

    sim = MaxwellWheelSimulation()

    left_rect = pygame.Rect(0, 0, LEFT_PANEL_WIDTH, HEIGHT)
    center_rect = pygame.Rect(LEFT_PANEL_WIDTH, 0, CENTER_PANEL_WIDTH, HEIGHT)
    right_rect = pygame.Rect(LEFT_PANEL_WIDTH + CENTER_PANEL_WIDTH, 0, RIGHT_PANEL_WIDTH, HEIGHT)

    top_title_h = font_large.get_height()
    top_margin = 16

    buttons = []
    btn_width, btn_height = 280, 70
    btn_x = left_rect.x + (left_rect.width - btn_width) // 2
    btn_y = top_margin + top_title_h + 14
    btn_gap = 10

    def start_sim():
        sim.running = True

    def pause_sim():
        sim.running = False

    def reset_sim():
        sim.reset_state(clear_history=True)

    buttons.append(Button((btn_x, btn_y, btn_width, btn_height), "Запустить", font_small, start_sim, icon="play"))
    buttons.append(
        Button(
            (btn_x, btn_y + (btn_height + btn_gap), btn_width, btn_height),
            "Остановить",
            font_small,
            pause_sim,
            icon="pause",
        )
    )
    buttons.append(Button((btn_x, btn_y + 2 * (btn_height + btn_gap), btn_width, btn_height), "Сбросить", font_small, reset_sim, icon="reset"))

    graph_width = 280
    graph_height = 130
    graph_x = left_rect.x + (left_rect.width - graph_width) // 2
    save_btn_width, save_btn_height = 280, 55
    bottom_pad = 20
    graph2_y = left_rect.bottom - bottom_pad - save_btn_height - 12 - graph_height
    graph1_y = graph2_y - 48 - graph_height
    graph_rect_hv = pygame.Rect(graph_x, graph1_y, graph_width, graph_height)
    graph_rect_energy = pygame.Rect(graph_x, graph2_y, graph_width, graph_height)

    save_btn_x = left_rect.x + (left_rect.width - save_btn_width) // 2
    save_btn_y = graph_rect_energy.bottom + 10

    def save_graphs_cb():
        data = snapshot_history(sim)

        def worker():
            try:
                save_plots(data)
            except Exception as e:
                print(f"Plot save failed: {e}")

        threading.Thread(target=worker, daemon=True).start()

    buttons.append(Button((save_btn_x, save_btn_y, save_btn_width, save_btn_height), "Скачать график", font_small, save_graphs_cb, icon="save"))

    param_controls = []
    param_x = right_rect.x + 20
    param_y = top_margin + top_title_h + 14
    param_width = right_rect.width - 40
    param_gap = 18
    right_scroll_offset = 0
    right_scroll_min = 0

    def on_param_change(_):
        sim.reset_state(clear_history=True)

    def set_m(v):
        sim.m = v
        on_param_change(v)

    param_controls.append(
        ParameterControl(
            "Масса m",
            "кг",
            param_x,
            0,
            param_width,
            font_small,
            font_small,
            0.01,
            1.0,
            sim.m,
            on_change=set_m,
            has_slider=True,
            log_scale=False,
        )
    )

    def set_R_mm(v_mm):
        sim.R_m = v_mm / 1000.0
        on_param_change(v_mm)

    param_controls.append(
        ParameterControl(
            "Радиус оси R",
            "мм",
            param_x,
            0,
            param_width,
            font_small,
            font_small,
            2.0,
            20.0,
            sim.R_m * 1000.0,
            on_change=set_R_mm,
            has_slider=True,
            log_scale=False,
        )
    )

    def set_J(v):
        sim.J = v
        on_param_change(v)

    param_controls.append(
        ParameterControl(
            "Момент инерции J",
            "кг·м²",
            param_x,
            0,
            param_width,
            font_small,
            font_small,
            1e-5,
            1e-3,
            sim.J,
            on_change=set_J,
            has_slider=True,
            log_scale=True,
        )
    )


    def set_h0(v):
        sim.h0 = v
        on_param_change(v)

    param_controls.append(
        ParameterControl(
            "Начальная высота h₀",
            "м",
            param_x,
            0,
            param_width,
            font_small,
            font_small,
            0.0,
            1.0,
            sim.h0,
            on_change=set_h0,
            has_slider=True,
            log_scale=False,
        )
    )

    def set_g(v):
        sim.g = v
        on_param_change(v)

    g_control = ParameterControl(
        "Ускорение свободного падения g",
        "м/с²",
        param_x,
        0,
        param_width,
        font_small,
        font_small,
        9.0,
        10.0,
        sim.g,
        on_change=set_g,
        has_slider=True,
        log_scale=False,
    )
    param_controls.append(g_control)

    def layout_right_panel(scroll_offset):
        nonlocal right_scroll_min
        y = param_y + scroll_offset
        # no friction checkbox insertion (ideal model)
        content_bottom = y
        for ctrl in param_controls:
            if ctrl is g_control:
                y += 24
            ctrl.set_position(param_x, y)
            y += ctrl.get_height() + param_gap
            content_bottom = max(content_bottom, y)
            

        available_h = right_rect.height - (param_y + 20)
        content_h = content_bottom - param_y
        if content_h <= available_h:
            right_scroll_min = 0
        else:
            right_scroll_min = available_h - content_h

    layout_right_panel(right_scroll_offset)

    time_accumulator = 0.0

    running = True
    while running:
        dt_real = clock.tick(FPS) / 1000.0
        time_accumulator += dt_real

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEWHEEL:
                mx, my = pygame.mouse.get_pos()
                if right_rect.collidepoint((mx, my)):
                    right_scroll_offset += int(event.y * 40)
                    right_scroll_offset = max(right_scroll_min, min(0, right_scroll_offset))
                    layout_right_panel(right_scroll_offset)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button in (4, 5):
                mx, my = event.pos
                if right_rect.collidepoint((mx, my)):
                    right_scroll_offset += 40 if event.button == 4 else -40
                    right_scroll_offset = max(right_scroll_min, min(0, right_scroll_offset))
                    layout_right_panel(right_scroll_offset)

            for btn in buttons:
                btn.handle_event(event)
            for ctrl in param_controls:
                ctrl.handle_event(event)
            

        while time_accumulator >= SIM_DT:
            sim.step(SIM_DT)
            time_accumulator -= SIM_DT

        screen.fill(BACKGROUND_COLOR)

        pygame.draw.rect(screen, PANEL_BG_COLOR, left_rect)
        pygame.draw.rect(screen, PANEL_BG_COLOR, center_rect)
        pygame.draw.rect(screen, PANEL_BG_COLOR, right_rect)

        for btn in buttons:
            btn.draw(screen)

        if sim.time_history:
            draw_series_graph(
                screen,
                graph_rect_hv,
                sim.time_history,
                [sim.h_history, sim.v_history],
                [COLOR_HEIGHT, COLOR_VELOCITY],
            )
            draw_series_graph(
                screen,
                graph_rect_energy,
                sim.time_history,
                [sim.ep_history, sim.ek_trans_history, sim.ek_rot_history],
                [COLOR_EP, COLOR_EK_TRANS, COLOR_EK_ROT],
            )

            legend_pad = 8
            legend_line_h = font_small.get_height() + 4

            legend_items_hv = [
                (COLOR_HEIGHT, "h(t)"),
                (COLOR_VELOCITY, "v(t)"),
            ]
            for idx, (color, text) in enumerate(legend_items_hv):
                lx = graph_rect_hv.x + legend_pad
                ly = graph_rect_hv.y + legend_pad + idx * legend_line_h
                text_w, text_h = font_small.size(text)
                bg_rect = pygame.Rect(lx - 4, ly - 2, 26 + text_w + 8, text_h + 4)
                pygame.draw.rect(screen, PANEL_BG_COLOR, bg_rect)
                pygame.draw.rect(screen, color, (lx, ly + (text_h // 2) - 4, 20, 8))
                txt = font_small.render(text, True, TEXT_COLOR)
                screen.blit(txt, (lx + 26, ly))

            legend_items_energy = [
                (COLOR_EP, "Ep"),
                (COLOR_EK_TRANS, "Ek пост."),
                (COLOR_EK_ROT, "Ek вр."),
            ]
            for idx, (color, text) in enumerate(legend_items_energy):
                lx = graph_rect_energy.x + legend_pad
                ly = graph_rect_energy.y + legend_pad + idx * legend_line_h
                text_w, text_h = font_small.size(text)
                bg_rect = pygame.Rect(lx - 4, ly - 2, 26 + text_w + 8, text_h + 4)
                pygame.draw.rect(screen, PANEL_BG_COLOR, bg_rect)
                pygame.draw.rect(screen, color, (lx, ly + (text_h // 2) - 4, 20, 8))
                txt = font_small.render(text, True, TEXT_COLOR)
                screen.blit(txt, (lx + 26, ly))

        cx = center_rect.centerx
        bar_half = 200
        bar_y = PENDULUM_BAR_Y
        pygame.draw.line(screen, BAR_COLOR, (cx - bar_half, bar_y), (cx + bar_half, bar_y), 8)

        rope_offset = 40
        rope_top_left = (cx - rope_offset, bar_y)
        rope_top_right = (cx + rope_offset, bar_y)

        pendulum_y = PENDULUM_START_Y + sim.h * PIXELS_PER_METER
        pendulum_y = min(pendulum_y, PENDULUM_START_Y + sim.h0 * PIXELS_PER_METER)

        rope_bottom_left = (cx - rope_offset, pendulum_y - PENDULUM_RADIUS_PIXELS)
        rope_bottom_right = (cx + rope_offset, pendulum_y - PENDULUM_RADIUS_PIXELS)

        pygame.draw.line(screen, ROPE_COLOR, rope_top_left, rope_bottom_left, 2)
        pygame.draw.line(screen, ROPE_COLOR, rope_top_right, rope_bottom_right, 2)

        for i in range(PENDULUM_RADIUS_PIXELS, 0, -4):
            f = i / PENDULUM_RADIUS_PIXELS
            r = int(0xC0 * f + 0x80 * (1 - f))
            g = int(0xC0 * f + 0x80 * (1 - f))
            b = int(0xC0 * f + 0x80 * (1 - f))
            pygame.draw.circle(screen, (r, g, b), (cx, int(pendulum_y)), i)

        pygame.draw.circle(screen, (50, 50, 50), (cx, int(pendulum_y)), PENDULUM_RADIUS_PIXELS, 2)

        info_y = PENDULUM_START_Y + int(sim.h0 * PIXELS_PER_METER) + 80
        text_lines = [
            f"h = {sim.h:.2f} м",
            f"v = {sim.v:.2f} м/с",
            f"ω = {sim.omega:.2f} рад/с",
            f"t = {sim.t:.2f} с",
            f"T = {(sim.time_to_bottom if sim.time_to_bottom is not None else float('nan')):.3f} с" if sim.time_to_bottom is not None else "T = —",
        ]
        line_step = font_medium.get_height() + 8
        for i, line in enumerate(text_lines):
            txt = font_medium.render(line, True, TEXT_COLOR)
            txt_rect = txt.get_rect(center=(center_rect.centerx, info_y + i * line_step))
            screen.blit(txt, txt_rect)

        for ctrl in param_controls:
            ctrl.draw(screen)
        

        title_left = font_large.render("Управление", True, TEXT_COLOR)
        screen.blit(title_left, (left_rect.x + 20, top_margin))
        title_center = font_large.render("Симуляция колеса Максвелла", True, TEXT_COLOR)
        tc_rect = title_center.get_rect(center=(center_rect.centerx, top_margin + title_center.get_height() // 2))
        screen.blit(title_center, tc_rect)
        title_right = font_large.render("Параметры", True, TEXT_COLOR)
        screen.blit(title_right, (right_rect.x + 20, top_margin))

        pygame.display.flip()

    pygame.quit()
