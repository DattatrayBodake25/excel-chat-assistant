def getting_chart_information(response: str):
    lines = response.strip().splitlines()
    chart_information = {"type": None, "x": None, "y": None}

    for i, line in enumerate(lines):
        if line.startswith("CHART:"):
            chart_information["type"] = line.split(":", 1)[1].strip().lower()
            chart_information["x"] = lines[i + 1].split(":", 1)[1].strip() if i + 1 < len(lines) else None
            chart_information["y"] = lines[i + 2].split(":", 1)[1].strip() if i + 2 < len(lines) else None
            return "\n".join(lines[:i]), chart_information

    return response, chart_information