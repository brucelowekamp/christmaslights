def DmxSent(state):
  if not state.Succeeded():
    print ("Error: ", state.message)
    raise
