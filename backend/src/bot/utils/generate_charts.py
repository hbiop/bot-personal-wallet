import io
import matplotlib
import matplotlib.pyplot as plt

matplotlib.use('Agg')


def generate_pie_chart(data: list[tuple[str, float]], title: str) -> io.BytesIO | None:
    if not data:
        return None

    labels = [row[0] for row in data]
    sizes = [row[1] for row in data]

    fig, ax = plt.subplots(figsize=(6, 6))

    colors = plt.get_cmap('Pastel1').colors

    wedges, texts, autotexts = ax.pie(
        sizes,
        labels=labels,
        autopct='%1.1f%%',
        startangle=140,
        colors=colors,
        textprops=dict(color="black")
    )

    for autotext in autotexts:
        autotext.set_fontsize(10)
        autotext.set_weight('bold')

    ax.set_title(title, fontsize=14, pad=20, weight='bold')

    image_buffer = io.BytesIO()
    plt.savefig(image_buffer, format='png', bbox_inches='tight', dpi=150)
    image_buffer.seek(0)

    plt.close(fig)

    return image_buffer
