# ODB – Object-Relational Edge Mapper

`ODB` is a lightweight Python class used to persist and load object trees using SQLAlchemy under the hood. It supports:

- Saving Pydantic models (`O` subclasses) to a SQL database.
- Linking objects with directional and bidirectional edges.
- Retrieving objects by `id` or globally unique `name`.
- Automatically cascading saves through object references.
- Minimal API: `save()`, `delete()`, `get_related()`, etc.

## Key Features

### 1. Object Identity
Each object is saved and loaded through SQLAlchemy with an internal `id`. You can also assign a global `name` to use symbolic references.

### 2. Edges as First-Class Links
Edges are stored in a separate table with support for:
- Directional and reverse relationships
- Optional keys (for list and dict indexing)
- Automatic edge deduplication

### 3. Recursion and Cycles
Saving an object recursively saves all its child objects and edges. Cycle-safe.

### 4. Usage Example

```python
class Book(O):
	title  : str
	author : 'Author' = O.Field(reverse='books')

class Author(O):
	name  : str
	books : List[Book] = O.Field(reverse='author')

a = Author(name='Leo Tolstoy')
b = Book(title='War and Peace')
a.books.append(b)

a.save(name='tolstoy')
```

### 5. Loading

```python
a = Author.load('tolstoy')
print(a.books[0].title)  # "War and Peace"
```

## Edge API

Internally used by `ODB`:

```python
edge.set(...)   # upsert
edge.unset(...) # delete relation
edge.get(...)   # list relations for given object and field
```

## Notes

- Only supports shallow inheritance.
- All models must be declared and registered before use.
- Uses a single global session (`ODB.session`) for simplicity.