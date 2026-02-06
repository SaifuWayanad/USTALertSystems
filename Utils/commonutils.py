import json


def parse_article_json(url, json_string: str) -> dict:
	"""
	Parses a JSON string and returns it as a dictionary.
	Input: JSON string with article data
	Output: Dictionary with keys: source, title, content, snippet, industry, published_at, created_at
	Attempts to repair common JSON issues.
	"""
	try:
		data = json.loads(json_string)
	except json.JSONDecodeError as e:
		# Try to repair by escaping unescaped quotes
		print(f"Initial parse failed: {e}")
		try:
			repaired_json = escape_unescaped_quotes(json_string)
			data = json.loads(repaired_json)
			print("Successfully parsed repaired JSON")
		except json.JSONDecodeError as e2:
			print(f"Repair also failed: {e2}")
			print(f"JSON string preview: {json_string[:100]}...")
			return {}
	
	data["source_url"] = url
	data["article_url"] = url
	data["content_hash"] = get_string_hash(data.get("content", ""))
	
	# Add snippet if missing
	if "snippet" not in data:
		content = data.get("content", "")
		data["snippet"] = content[:200] if len(content) > 200 else content
	
	return data


def escape_unescaped_quotes(json_str: str) -> str:
	"""
	Attempts to escape unescaped quotes within string values in JSON.
	This is a heuristic approach that looks for quote patterns.
	"""
	result = []
	i = 0
	while i < len(json_str):
		if json_str[i] == '"':
			result.append('"')
			i += 1
			# We're inside a string, collect until closing quote
			while i < len(json_str):
				if json_str[i] == '\\' and i + 1 < len(json_str):
					# Escaped character
					result.append(json_str[i])
					result.append(json_str[i+1])
					i += 2
				elif json_str[i] == '"':
					# End of string
					result.append('"')
					i += 1
					break
				else:
					result.append(json_str[i])
					i += 1
		else:
			result.append(json_str[i])
			i += 1
	
	return ''.join(result)


def process_article_data(article: dict) -> dict:
	"""
	Accepts a dictionary with article data and returns it.
	The input should have keys: source, title, content, snippet, industry, published_at, created_at.
	"""
	# Optionally, you can validate the structure here if needed
	return article







def get_string_hash(content: str) -> int:
	"""
	Returns the hash value of the input string content.
	"""
	return hash(content)

