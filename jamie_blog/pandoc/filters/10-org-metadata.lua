-- Adapted from https://pandoc.org/org.html
-- intermediate store for variables and their values
local variables = {}

--- Convert keyword value to boolean, string, or list [ boolean | string ]
function parse_value(value_string)
  lower = value_string:lower()
  if lower == "t" or lower == "true" then
    return true
  elseif lower == "f" or lower == "false" then
    return false
  elseif value_string:match("^%b[]$") then
    -- Simplistic heterogenous list parsing (string | bool)
    results = {}
    for s in value_string:gmatch("%s*([%w-_]+)%s*[%],]") do
      table.insert(results, parse_value(s))
    end
    return results
  end
  return value_string
end

--- Function called for each raw block element.
function RawBlock (raw)
  -- Don't do anything unless the block contains *org* markup.
  if raw.format ~= 'org' then return nil end

  -- Extract variable name and value
  -- Allow key comprising alphanumeric + "-_".
  -- Allow value with at least 1 non-space character
  -- Trim whitespace around value
  local name, value = raw.text:match '#%+(%w[%w_-]*):%s*(%g.-)%s*$'
  if name and value then
    -- Org keys are typically UPPER_CASE, but pandoc metadata keys are
    -- lowercase, so convert keys to lowercase
    variables[name:lower()] = parse_value(value)
  end
end

-- Add the extracted variables to the document's metadata.
function Meta (meta)
  for name, value in pairs(variables) do
    meta[name] = value
  end
  return meta
end
