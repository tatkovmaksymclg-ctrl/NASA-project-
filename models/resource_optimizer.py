"""Евристичний розподіл обмежених медичних комплектів."""

def allocate_medical_kits(astronaut_risks: dict, available_kits: int) -> dict:
    """
    Розподіляє комплекти за спаданням бала ризику.
    Комплект отримують особи з найбільшим ненульовим балом.
    Це навчальна евристика, не медичний протокол.
    """
    if available_kits < 0:
        raise ValueError("Кількість комплектів не може бути від'ємною.")

    ranked = sorted(
        astronaut_risks.items(),
        key=lambda item: item[1],
        reverse=True
    )
    selected = [
        name for name, score in ranked
        if score > 0
    ][:available_kits]

    return {
        "assigned": selected,
        "not_assigned": [
            name for name, score in ranked
            if score > 0 and name not in selected
        ],
        "ranking": ranked,
        "kits_used": len(selected),
        "kits_available": available_kits,
    }
