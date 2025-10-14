export class LRU<K,V> {
  private max: number;
  private map = new Map<K,V>();
  constructor(capacity = 512) { this.max = capacity; }
  get(k: K): V | undefined {
    const v = this.map.get(k);
    if (v !== undefined) { this.map.delete(k); this.map.set(k, v); }
    return v;
  }
  set(k: K, v: V) {
    if (this.map.has(k)) this.map.delete(k);
    this.map.set(k, v);
    if (this.map.size > this.max) {
      const fk = this.map.keys().next().value; // oldest
      this.map.delete(fk);
    }
  }
  has(k: K) { return this.map.has(k); }
}
