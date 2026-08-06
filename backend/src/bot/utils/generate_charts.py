import io
import logging

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)

plt.rcParams["font.family"] = "DejaVu Sans"


def generate_pie_chart(data: list[tuple[str, float]], title: str) -> bytes | None:
    if not data:
        return None

    labels: list[str] = []
    sizes: list[float] = []
    for name, amount in data:
        if amount is None or amount <= 0:
            continue
        labels.append(name)
        sizes.append(float(amount))

    if not labels or sum(sizes) <= 0:
        return None

    fig, ax = plt.subplots(figsize=(5, 5))
    try:
        cmap = plt.get_cmap("Pastel1")
        colors = [cmap(i % cmap.N) for i in range(len(labels))]

        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=labels,
            autopct="%1.1f%%",
            startangle=140,
            colors=colors,
            textprops={"color": "black"},
        )

        for autotext in autotexts:
            autotext.set_fontsize(10)
            autotext.set_weight("bold")

        ax.set_title(title, fontsize=14, pad=20, weight="bold")

        image_buffer = io.BytesIO()
        fig.savefig(
            image_buffer,
            format="png",
            bbox_inches="tight",
            dpi=100,
            pad_inches=0.1,
        )
        png_bytes = image_buffer.getvalue()
        if len(png_bytes) < 8 or png_bytes[:8] != b"\x89PNG\r\n\x1a\n":
            logger.warning("Pie chart save produced invalid PNG (%s bytes)", len(png_bytes))
            return None
        return png_bytes
    except Exception:
        logger.exception("Failed to generate pie chart")
        return None
    finally:
        plt.close(fig)
