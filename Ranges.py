import unittest

# accepts a string of the form 1-2,4,5-9,3 and returns a list of numbers
# including duplicates 
def Parse(input): 
  result = []
  terms = input.split(',')
  assert (len(terms)>=1)
  for term in terms:
    subterms = term.split('-')
    if (len(subterms) == 1): # is a single number
      result.append(int(term.strip()))
    else: # is a range
      assert (len(subterms) == 2)
      a = int(subterms[0])
      b = int(subterms[1])
      assert (a < b)
      for i in range(a,b+1):
        result.append(i)
  result.sort()
  return result

  
class TestRanges(unittest.TestCase):
  def test_single(self):
    self.assertEqual(Parse('1'), [1])
  def test_two(self):
    self.assertEqual(Parse('1,4'), [1,4])
  def test_sort(self):
    self.assertEqual(Parse('4, 1'), [1,4])
  def test_range(self):
    self.assertEqual(Parse('1-3'), [1,2,3])
  def test_all(self):
    self.assertEqual(Parse('1-3 ,0, 5,8 - 9,6,7, 10-12,1'), [0,1,1,2,3,5,6,7,8,9,10,11,12])



if __name__ == '__main__':
  unittest.main()
