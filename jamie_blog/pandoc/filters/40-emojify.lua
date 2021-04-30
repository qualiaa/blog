package.path = (PANDOC_STATE.user_data_dir .. "/lua/json/json.lua;") .. package.path

data_dir = PANDOC_STATE.user_data_dir .. "/../data"
json = require ("json")

lookup_file = io.open(data_dir .. "/emoji.json")
emoji_lookup = json.decode(lookup_file:read())
short_names_file = io.open(data_dir .. "/short_names.json")
emoji_short_names = json.decode(short_names_file:read())

function match_emoji(short_name)
  if emoji_lookup[short_name] then
    return emoji_lookup[short_name]
  else
    for name, aliases in pairs(emoji_short_names) do
      if aliases[short_name] then
        return emoji_lookup[name]
      end
    end
  end
  return ":" .. short_name .. ":"
end

function Str(str)
  str.text = str.text:gsub(":([^:%s]+):", match_emoji)
  return str
end
