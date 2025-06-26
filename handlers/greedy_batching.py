def greedy_batching(bookings, max_group_size=3):
    """
    Divide bookings into batches of at most max_group_size.
    Simple greedy batching.
    """
    bookings.sort(key=lambda x: x['departure_dt'])
    batches = []

    while bookings:
        batch = bookings[:max_group_size]
        batches.append(batch)
        bookings = bookings[max_group_size:]

    return batches