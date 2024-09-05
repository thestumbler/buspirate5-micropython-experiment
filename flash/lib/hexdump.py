
def is_printable_ascii( ch ):
  code = ord(ch)
  if code < 0x20: return False
  if code > 0x7e: return False
  return True

def hexdump( vals, wrap=16, offset=None, ascii=True, prefix='' ):
  """Formats long list of bytes to a standard hex dump format."""
  if vals is None: return
  # output=[]
  line=[]
  text = []
  newline = True
  line.append( prefix )
  if offset is not None: line.append( f'{offset:04x}   ' )
  for i,h in enumerate(vals):
    line.append( f'{h:02x} ' )
    if ascii: 
      if is_printable_ascii(chr(h)):
        text.append( chr(h) )
      else:
        text.append( '.' )
      if i%(wrap/2) == ((wrap/2)-1): # insert blank for clarity
        line.append(' ')
        text.append(' ')
    newline = False
    if i%wrap == (wrap-1): # new line
      # output.extend( [ ' '.join( [ ''.join( line ), ''.join(text) ]  ) ] )
      print( ' '.join( [ ''.join( line ), ''.join(text) ]  ) )
      if offset is not None: offset += wrap
      line=[]
      text=[]
      newline = True
      line.append( prefix )
      if offset is not None: line.extend( [ f'{offset:04x}', '   ' ] )

  if not newline: 
    # output.extend( [ ' '.join( [ ''.join( line ), ''.join(text) ]  ) ] )
    print( ' '.join( [ ''.join( line ), ''.join(text) ]  ) )



