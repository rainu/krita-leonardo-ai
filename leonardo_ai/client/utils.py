def multipleOf(number: int, multiple : int = 8) -> int:
  return ((number + multiple - 1) // multiple) * multiple