function resolve_local_link(link)
  if link:match("^#") then
    return "LOCAL" .. link
  elseif link:match("^./") then
    return "LOCAL/" .. link:sub(3)
  elseif link[1] ~= "/" and not link:match("://") then
    return "LOCAL/" .. link
  end
  return link
end

function Image(elem)
  elem.src = resolve_local_link(elem.src)
  return elem
end

function Link(elem)
  elem.target = resolve_local_link(elem.target)
  return elem
end
