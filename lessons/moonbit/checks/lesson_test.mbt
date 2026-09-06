fn add(a : Int, b : Int) -> Int { a + b }
fn or_zero(x : Int?) -> Int {
  match x { Some(n) => n; None => 0 }
}
fn[T : Eq] same(a : T, b : T) -> Bool { a == b }
enum LoadState { Idle; Loading; Ready(String) }
fn message(state : LoadState) -> String {
  match state {
    Idle => "waiting"
    Loading => "loading"
    Ready(text) => text
  }
}
suberror Negative
fn checked(n : Int) -> Int raise Negative {
  if n < 0 { raise Negative }
  n
}
test "addition and fallback" {
  assert_eq(add(6, 7), 13)
  assert_eq(or_zero(None), 0)
  assert_eq(or_zero(Some(9)), 9)
}
test "if and range" {
  let n = 5
  let answer = if n > 3 { n * 2 } else { n + 2 }
  assert_eq(answer, 10)
  let mut total = 0
  for i in 0..<4 { total = total + i }
  assert_eq(total, 6)
}
test "binding versus array mutation" {
  let values : Array[Int] = [1, 2, 3]
  values[0] = 9
  values.push(4)
  assert_eq(values[0], 9)
  assert_eq(values.length(), 4)
}
test "map preserves source" {
  let source = [4, 5, 6]
  let doubled = source.map(x => x * 2)
  assert_eq(doubled[1], 10)
  assert_eq(source[1], 5)
}
test "all states" {
  assert_eq(message(Idle), "waiting")
  assert_eq(message(Loading), "loading")
  assert_eq(message(Ready("done")), "done")
}
test "generic equality" {
  assert_true(same(3, 3))
  assert_false(same("a", "b"))
}
test "raise and catch" {
  assert_eq(checked(4), 4)
  let value = try checked(-2) catch { Negative => 0 }
  assert_eq(value, 0)
}
