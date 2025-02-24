def create_circular_loader(canvas, x, y, radius, width=5, speed=10, color="blue"):
    """Creates a rotating circular loading animation in a CTkCanvas."""
    def animate():
        nonlocal angle
        if running:  # Only animate if running is True
            angle = (angle + speed) % 360
            canvas.itemconfig(arc, start=angle)
            canvas.after(50, animate)

    angle = 0
    running = True
    arc = canvas.create_arc(
        x - radius, y - radius, x + radius, y + radius,
        start=angle, extent=90, outline=color, width=width, style="arc"
    )
    animate()
    return lambda: canvas.delete(arc)