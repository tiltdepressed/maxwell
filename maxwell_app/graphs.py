import pygame


def draw_series_graph(surface, rect, times, series_list, colors):
    pygame.draw.rect(surface, (40, 40, 40), rect)
    pygame.draw.rect(surface, (100, 100, 100), rect, 1)

    if not times or len(times) < 2:
        return

    t_min = times[0]
    t_max = times[-1]
    if t_max <= t_min:
        t_max = t_min + 1e-6

    values = []
    for series in series_list:
        values.extend(series)
    if not values:
        return

    v_min = min(values)
    v_max = max(values)
    if v_max <= v_min:
        v_max = v_min + 1e-6

    def to_screen(t, v):
        x = rect.left + (t - t_min) / (t_max - t_min) * rect.width
        y = rect.bottom - (v - v_min) / (v_max - v_min) * rect.height
        return x, y

    for series, color in zip(series_list, colors):
        points = []
        for t, v in zip(times, series):
            sx, sy = to_screen(t, v)
            points.append((sx, sy))
        if len(points) >= 2:
            pygame.draw.lines(surface, color, False, points, 1)
