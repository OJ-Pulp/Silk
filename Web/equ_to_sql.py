import re

def equ_to_sql(expr_list):
    result = {}

    for expr in expr_list:
        expr = expr.strip()
        expr = re.sub(r'\s+', ' ', expr)

        # Normalize operators
        expr = expr.replace("==", "=")
        expr = re.sub(r'\bnot like\b', 'NOT LIKE', expr, flags=re.IGNORECASE)
        expr = re.sub(r'\blike\b', 'LIKE', expr, flags=re.IGNORECASE)
        expr = re.sub(r'\bnot in\b', 'NOT IN', expr, flags=re.IGNORECASE)
        expr = re.sub(r'\bin\b', 'IN', expr, flags=re.IGNORECASE)

        # Patterns and processing
        patterns = [
            r'^(\w+)\s*=\s*(.+)$',
            r'^(\w+)\s*!=\s*(.+)$',
            r'^(\w+)\s*>=\s*(.+)$',
            r'^(\w+)\s*<=\s*(.+)$',
            r'^(\w+)\s*>\s*(.+)$',
            r'^(\w+)\s*<\s*(.+)$',
            r'^(\w+)\s+LIKE\s+(.+)$',
            r'^(\w+)\s+NOT LIKE\s+(.+)$',
            r'^(\w+)\s+IN\s+(\[.*\])$',
            r'^(\w+)\s+NOT IN\s+(\[.*\])$',
        ]

        matched = False
        for pattern in patterns:
            match = re.match(pattern, expr, re.IGNORECASE)
            if match:
                var, val = match.groups()
                var = var.strip()
                val = val.strip()

                # Handle IN / NOT IN list expressions
                if pattern.endswith(r'\[.*\])$'):
                    val = val[1:-1].strip()  # remove brackets
                    if val:
                        items = re.split(r',\s*', val)
                        formatted_items = []
                        for item in items:
                            item = item.strip()
                            if (item.startswith('"') and item.endswith('"')) or (item.startswith("'") and item.endswith("'")):
                                item = "'" + item[1:-1].replace("'", "''") + "'"
                            formatted_items.append(item)
                        list_sql = ", ".join(formatted_items)
                    else:
                        list_sql = ""
                    op = "NOT IN" if "NOT IN" in pattern else "IN"
                    result[var] = f"{var} {op} ({list_sql})"
                    matched = True
                    break

                # Handle single value expressions
                if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                    val = "'" + val[1:-1].replace("'", "''") + "'"

                op = re.search(r'(=|!=|>=|<=|>|<|LIKE|NOT LIKE)', pattern, re.IGNORECASE).group(1).upper()
                result[var] = f"{var} {op} {val}"
                matched = True
                break

        if not matched:
            raise ValueError(f"Invalid or unsupported expression: {expr}")

    return result

# --- test code ---
if __name__ == "__main__":
    inputs = [
        'x == 5',
        'y != "foo"',
        '  score > 90',
        'age <= 65',
        'tag IN [ "a" , "b" , "c" ]',
        "id NOT IN [1 , 2, 3]",
        "name LIKE 'foo%'",
        'email not like "admin_%"',
        'column_1 = "val"'
    ]

    result = equ_to_sql(inputs)
    for k, v in result.items():
        print(f"{k:12} => {v}")
