import unittest


# accepts a string of the form 1-2,4,5-9 and returns a list of numbers
# or the lengths of each segment
# asserts if ranges are out of order or duplicated
def Parse(input, lengths=False):
  result = []
  rangeLength = []
  terms = input.split(',')
  assert (len(terms) >= 1)
  for term in terms:
    subterms = term.split('-')
    if (len(subterms) == 1):  # is a single number
      result.append(int(term.strip()))
      rangeLength.append(1)
    else:  # is a range
      assert (len(subterms) == 2)
      a = int(subterms[0])
      b = int(subterms[1])
      assert (a < b)
      for i in range(a, b + 1):
        result.append(i)
      rangeLength.append(b+1-a)
  for i in range(1,len(result)):
    assert (result[i-1]<result[i])
  return result if lengths == False else rangeLength


class TestRanges(unittest.TestCase):

  def test_single(self):
    self.assertEqual(Parse('1'), [1])
    self.assertEqual(Parse('1', lengths=True), [1])

  def test_two(self):
    self.assertEqual(Parse('1,4'), [1, 4])
    self.assertEqual(Parse('1,4', lengths=True), [1, 1])

  def test_sort(self):
    with self.assertRaises(AssertionError):
      Parse('4, 1')

  def test_range(self):
    self.assertEqual(Parse('1-3'), [1, 2, 3])
    self.assertEqual(Parse('1-3', lengths=True), [3])

  def test_all(self):
    self.assertEqual(Parse('1-3 , 5,7, 8 - 9, 11-12'),
                     [1, 2, 3, 5, 7, 8, 9, 11, 12])
    self.assertEqual(Parse('1-3 , 5,7, 8 - 9, 11-12', lengths=True),
                     [3,1,1,2,2])


if __name__ == '__main__':
  unittest.main()
