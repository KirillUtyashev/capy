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

    def read_from_json(self, json_data):
        self._items.clear()

        def validate_and_enqueue(question_obj):
            required_keys = ("question", "correct", "incorrect", "hint")
            if not all(key in question_obj for key in required_keys):
                raise ValueError("A question object is missing required keys.")
            self.enqueue(question_obj)

        # Check if the json_data is a list of questions or a single question object.
        if isinstance(json_data, list):
            for question_obj in json_data:
                validate_and_enqueue(question_obj)
        elif isinstance(json_data, dict):
            validate_and_enqueue(json_data)
        else:
            raise ValueError("Invalid JSON data: expected a dict or a list of dicts.")
