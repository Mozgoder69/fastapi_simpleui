// frontend/src/core/types/data.ts

export type Value = object | string | number | boolean | null | undefined;
export type Dict<T = Value> = Record<string, T>;
export type Records<T> = { records: T[] };
export type DataOnly<T = Value> = { data: Dict<T> };
export type DataOnlyList<T = Value> = Records<DataOnly<T>>;
export type KeysOnly<T = Value> = { keys: Dict<T> };
export type KeysOnlyList<T = Value> = Records<KeysOnly<T>>;
export type KeyedData<K = Value, D = Value> = { keys: Dict<K>; data: Dict<D> };
export type KeyedDataList<K = Value, D = Value> = Records<KeyedData<K, D>>;
