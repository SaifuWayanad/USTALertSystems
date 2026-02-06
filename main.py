from DB.db import get_all_raw_links
from Utils.commonutils import parse_article_json
from DB.db import insert_article_from_dict
from CrawlingAgent import  AgentCaller
import json
import re


def repair_json(json_str: str) -> str:
	"""
	Attempts to repair common JSON issues like unescaped quotes in strings.
	"""
	# Try to fix unescaped quotes within string values
	# This is a simple approach - find quotes that are not properly escaped
	result = []
	i = 0
	while i < len(json_str):
		if json_str[i] == '"':
			# Found a quote - collect the string content
			result.append('"')
			i += 1
			while i < len(json_str):
				if json_str[i] == '\\':
					result.append(json_str[i])
					if i + 1 < len(json_str):
						result.append(json_str[i + 1])
						i += 2
					else:
						i += 1
				elif json_str[i] == '"':
					result.append('"')
					i += 1
					break
				else:
					# If we encounter an unescaped quote-like character inside a string, escape it
					if json_str[i] == '"':
						result.append('\\"')
					else:
						result.append(json_str[i])
					i += 1
		else:
			result.append(json_str[i])
			i += 1
	
	return ''.join(result)


def extract_json_from_markdown(response_text: str) -> str:
	"""
	Extracts JSON from markdown code blocks or raw JSON.
	Returns the JSON string without markdown wrapper.
	Handles proper brace matching with string escaping.
	"""
	# Try to extract from markdown code block (```json ... ```)
	json_match = re.search(r'```(?:json)?\s*\n(.*?)\n```', response_text, re.DOTALL)
	if json_match:
		json_str = json_match.group(1).strip()
		# Validate and fix if needed
		return extract_valid_json(json_str)
	
	# If no markdown wrapper, try to find JSON directly
	start_idx = response_text.find('{')
	if start_idx != -1:
		json_str = response_text[start_idx:].strip()
		return extract_valid_json(json_str)
	
	return response_text.strip()


def extract_valid_json(text: str) -> str:
	"""
	Extracts a valid JSON object from text by matching braces properly,
	accounting for escaped quotes and strings.
	"""
	start_idx = text.find('{')
	if start_idx == -1:
		return text
	
	brace_count = 0
	in_string = False
	escape_next = False
	last_close_brace = -1
	
	for i in range(start_idx, len(text)):
		char = text[i]
		
		if escape_next:
			escape_next = False
			continue
		
		if char == '\\':
			escape_next = True
			continue
		
		if char == '"':
			in_string = not in_string
			continue
		
		if not in_string:
			if char == '{':
				brace_count += 1
			elif char == '}':
				brace_count -= 1
				if brace_count == 0:
					last_close_brace = i
					return text[start_idx:i+1]
	
	# If we reach here and found a close brace, return up to the last one
	if last_close_brace != -1:
		return text[start_idx:last_close_brace+1]
	
	# Otherwise return what we have
	return text[start_idx:]


def main():
	raw_links = get_all_raw_links()
	print(f"Found {len(raw_links)} raw links to process.")
	for raw in raw_links:
		# print(raw)
		print(f"Processing link: {raw[2]}")
		url = raw[2]
		response_text = AgentCaller(url)
		print(f"Agent response length: {len(response_text)} chars")
		print(f"Agent response preview: {response_text[:200]}...")
		
		# Extract JSON from markdown or raw response
		json_str = extract_json_from_markdown(response_text)
		print(f"Extracted JSON length: {len(json_str)} chars")
		print(f"Extracted JSON preview: {json_str[:200]}...")
		
		# Try to validate JSON
		try:
			test_parse = json.loads(json_str)
			print(f"JSON validation passed. Keys: {list(test_parse.keys())}")
		except json.JSONDecodeError as e:
			print(f"JSON validation failed: {e}")
			print(f"JSON string around error: {json_str[max(0, e.pos-50):e.pos+50]}")
		
		# Parse the JSON
		fin = parse_article_json(url, json_str)
		
		if fin:
			insert_article_from_dict(fin)
			print(f"Successfully inserted article: {fin.get('title', 'Unknown')}")
		else:
			print(f"Failed to extract JSON from response")
		break

if __name__ == "__main__":
    main()
