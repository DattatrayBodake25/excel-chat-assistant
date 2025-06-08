#Data visualization script

#writing function for accurate lable for chart visual or convert raw column name
def prettify_label(label: str) -> str:
    """
    Converts raw column names like 'product_id' to 'Product Id'.
    """
    if not label:
        return ""
    return label.replace("_", " ").title()


#writing function for chart information or insight here 
def getting_chart_information(response: str):
    """
    Reads model response to get chart info and returns:
    """
    lines = response.strip().splitlines()
    chart_information = {"type": None, "x": None, "y": None}

    for i, line in enumerate(lines):
        if line.startswith("CHART:"):
            chart_information["type"] = line.split(":", 1)[1].strip().lower()

            # Safe reads for X and Y lines
            try:
                chart_information["x"] = lines[i + 1].split(":", 1)[1].strip()
            except IndexError:
                chart_information["x"] = None

            try:
                chart_information["y"] = lines[i + 2].split(":", 1)[1].strip()
            except IndexError:
                chart_information["y"] = None

            # Return everything before CHART section as natural language response
            return "\n".join(lines[:i]).strip(), chart_information

    # If no CHART section found, return full response and empty chart info
    return response.strip(), chart_information