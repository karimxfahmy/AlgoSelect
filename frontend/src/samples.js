// pre-baked sample inputs so the user has something to click on
// instead of typing a graph by hand. handy for demos.

export function knapsackSample(n) {
  // simple deterministic generator — same n always gives the same items.
  // makes the comparison table reproducible across reloads.
  const weights = []
  const values = []
  for (let i = 0; i < n; i++) {
    weights.push(1 + ((i * 7) % 9))   // weights in 1..9
    values.push(2 + ((i * 11) % 14))  // values in 2..15
  }
  // capacity scales with n, roughly half the total weight
  const capacity = Math.max(5, Math.floor(weights.reduce((a, b) => a + b, 0) / 2))
  return { weights, values, capacity }
}

export function routingSample(n) {
  // build a small connected graph. ring + a few cross edges so dijkstra
  // actually has choices to make.
  const nodes = []
  for (let i = 0; i < n; i++) nodes.push(String.fromCharCode(65 + i))  // A,B,C...
  const edges = []
  for (let i = 0; i < n; i++) {
    const a = nodes[i]
    const b = nodes[(i + 1) % n]
    edges.push({ u: a, v: b, w: 1 + ((i * 3) % 5) })
  }
  // a couple of chords to make shortest paths non-trivial
  if (n >= 4) edges.push({ u: nodes[0], v: nodes[Math.floor(n / 2)], w: 2 })
  if (n >= 6) edges.push({ u: nodes[1], v: nodes[Math.floor(n / 2) + 1], w: 3 })
  return { nodes, edges, source: nodes[0], directed: false }
}

export function sortingSample(n) {
  // pseudo-random but deterministic
  const arr = []
  let seed = 42
  for (let i = 0; i < n; i++) {
    seed = (seed * 1103515245 + 12345) & 0x7fffffff
    arr.push(seed % 100)
  }
  return arr
}

export function searchSample(n) {
  // sorted array of even numbers, target is somewhere in the middle
  const arr = []
  for (let i = 0; i < n; i++) arr.push(i * 2)
  const target = Math.floor(n / 2) * 2
  return { array: arr, target }
}

export function exponentSample(n) {
  // base 2 keeps the numbers easy to eyeball (powers of two are recognisable).
  // n drives the exponent — we just rename it so the API gets what it expects.
  return { base: 2, exp: n }
}
