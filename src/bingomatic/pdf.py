"""PDF generation for Bingomatic bingo cards."""

from pathlib import Path

from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen.canvas import Canvas


# Constants for grid dimensions (in points, 72 points = 1 inch)
SQUARE_SIZE = 72  # 1 inch
GRID_SIZE = 5  # 5x5 grid
GAP = 36  # 0.5 inch gap between grids
GRID_TOTAL = SQUARE_SIZE * GRID_SIZE  # 5 inches total


def calculate_grid_positions(
    page_width: float, page_height: float
) -> tuple[float, float, float, float]:
    """Calculate x,y positions for two centered grids with a gap between them.

    Args:
        page_width: Width of the page in points
        page_height: Height of the page in points

    Returns:
        Tuple of (left_x, left_y, right_x, right_y) for grid positions
    """
    # Total width of both grids plus gap
    total_width = (GRID_TOTAL * 2) + GAP

    # Center horizontally
    left_x = (page_width - total_width) / 2
    right_x = left_x + GRID_TOTAL + GAP

    # Center vertically (leaving space for header)
    header_space = 36  # 0.5 inch for event name
    available_height = page_height - header_space
    y = (available_height - GRID_TOTAL) / 2

    return left_x, y, right_x, y


def draw_grid(canvas: Canvas, x: float, y: float) -> None:
    """Draw a 5x5 grid of 1-inch squares at the specified position.

    Args:
        canvas: ReportLab canvas to draw on
        x: X coordinate of bottom-left corner of grid
        y: Y coordinate of bottom-left corner of grid
    """
    canvas.setStrokeColorRGB(0, 0, 0)  # Black lines
    canvas.setLineWidth(1)

    # Draw horizontal lines
    for row in range(GRID_SIZE + 1):
        y_pos = y + (row * SQUARE_SIZE)
        canvas.line(x, y_pos, x + GRID_TOTAL, y_pos)

    # Draw vertical lines
    for col in range(GRID_SIZE + 1):
        x_pos = x + (col * SQUARE_SIZE)
        canvas.line(x_pos, y, x_pos, y + GRID_TOTAL)


def generate_pdf(
    output_path: Path | str,
    card_count: int,
    event_name: str | None = None,
    logo_path: Path | str | None = None,
) -> Path:
    """Generate a PDF with bingo card grids.

    Args:
        output_path: Path where the PDF will be saved
        card_count: Number of bingo cards to generate
        event_name: Optional event name to display above each grid
        logo_path: Optional path to logo image for center square

    Returns:
        Path to the generated PDF file
    """
    output_path = Path(output_path)
    page_width, page_height = landscape(letter)

    canvas = Canvas(str(output_path), pagesize=landscape(letter))

    # Calculate how many pages we need (2 cards per page)
    pages_needed = (card_count + 1) // 2

    for page_num in range(pages_needed):
        # Calculate grid positions
        left_x, left_y, right_x, right_y = calculate_grid_positions(
            page_width, page_height
        )

        # Draw left grid (always present)
        draw_grid(canvas, left_x, left_y)

        # Draw event name above left grid if provided
        if event_name:
            _draw_event_name(canvas, event_name, left_x, left_y)

        # Draw logo in center square of left grid if provided
        if logo_path:
            _draw_logo(canvas, logo_path, left_x, left_y)

        # Draw right grid only if we have another card to show
        cards_on_this_page = 2 if (page_num * 2 + 2) <= card_count else 1
        if cards_on_this_page == 2:
            draw_grid(canvas, right_x, right_y)

            # Draw event name above right grid if provided
            if event_name:
                _draw_event_name(canvas, event_name, right_x, right_y)

            # Draw logo in center square of right grid if provided
            if logo_path:
                _draw_logo(canvas, logo_path, right_x, right_y)

        # Add new page if not the last one
        if page_num < pages_needed - 1:
            canvas.showPage()

    canvas.save()
    return output_path


def _draw_event_name(canvas: Canvas, event_name: str, grid_x: float, grid_y: float) -> None:
    """Draw event name centered above the grid.

    Args:
        canvas: ReportLab canvas to draw on
        event_name: Text to display
        grid_x: X coordinate of grid's bottom-left corner
        grid_y: Y coordinate of grid's bottom-left corner
    """
    # Position text above grid
    text_x = grid_x + (GRID_TOTAL / 2)
    text_y = grid_y + GRID_TOTAL + 10  # 10 points above grid

    canvas.setFont("Helvetica-Bold", 14)
    canvas.drawCentredString(text_x, text_y, event_name)


def _draw_logo(canvas: Canvas, logo_path: Path | str, grid_x: float, grid_y: float) -> None:
    """Draw logo in the center square of the grid.

    Args:
        canvas: ReportLab canvas to draw on
        logo_path: Path to the logo image file
        grid_x: X coordinate of grid's bottom-left corner
        grid_y: Y coordinate of grid's bottom-left corner
    """
    logo_path = Path(logo_path)

    if not logo_path.exists():
        raise FileNotFoundError(f"Logo file not found: {logo_path}")

    # Center square is at row 2, col 2 (0-indexed), which is row 3, col 3 (1-indexed)
    center_row = 2
    center_col = 2

    # Calculate center square position
    square_x = grid_x + (center_col * SQUARE_SIZE)
    square_y = grid_y + (center_row * SQUARE_SIZE)

    # Add small padding inside the square
    padding = 4
    logo_x = square_x + padding
    logo_y = square_y + padding
    logo_size = SQUARE_SIZE - (padding * 2)

    # Draw the logo, maintaining aspect ratio
    canvas.drawImage(
        str(logo_path),
        logo_x,
        logo_y,
        width=logo_size,
        height=logo_size,
        preserveAspectRatio=True,
        anchor="c",
    )
