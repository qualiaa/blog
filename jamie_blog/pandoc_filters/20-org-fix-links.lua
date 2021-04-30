function Image(elem)
  if elem.src:match("^./") then
      elem.src = "LOCAL/" .. elem.src:sub(3)
  end
  return elem
end
