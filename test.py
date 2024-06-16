import requests

max_brightness = 255
response = requests.get(
    'https://github-contributions-api.deno.dev/jriggles.text'
)
status = response.status_code
data = response.content
# split response content into rows, removing the contribution count at the
# beginning and the empty cell at the end
rows = data.decode().split('\n')[1:-1]
# split the rows into maps of str, keeping the 'display.width' (15) elements
string_maps = [map(str.strip, row.split(',')[-15:]) for row in rows]
# convert string values to ints, replacing the empty strings with 0
values = [int(n) if n.isdigit() else 0 for row in string_maps for n in row]
# normalize the integer values to a range of 0 to max_brigtness
peak = max(values)
normalized_values = [int((n / peak) * max_brightness) for n in values]
print(normalized_values)

for i, v in enumerate(normalized_values):
    x, y = divmod(i, 15)
    print(x, y, v)
