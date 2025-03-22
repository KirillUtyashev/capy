class Queue:
    def __init__(self) -> None:
        """Initialize a new empty queue."""
        self._items = []

    def is_empty(self) -> bool:
        """Return whether this queue contains no items.

        >>> q = Queue()
        >>> q.is_empty()
        True
        >>> q.enqueue('hello')
        >>> q.is_empty()
        False
        """
        return self._items == []

    def enqueue(self, item) -> None:
        """Add <item> to the back of this queue.
        """
        self._items.append(item)

    def _dequeue_item(self) -> None:
        """Add <item> to the back of this queue.
        """
        del self._items[0]

    def dequeue(self):
        """Remove and return the item at the front of this queue.

        Return None if this Queue is empty.
        (We illustrate a different mechanism for handling an erroneous case.)

        >>> q = Queue()
        >>> q.enqueue('hello')
        >>> q.enqueue('goodbye')
        >>> q.dequeue()
        'hello'
        """
        a = self._items[::-1].pop()
        self._dequeue_item()
        return a

    def __len__(self):
        return len(self._items)
