class RunSummary:
    def __init__(self, league):
        self.league = league
        self.processed = 0
        self.rejected = 0

    def add_processed(self, amount):
        self.processed += amount

    def add_rejected(self, amount):
        self.rejected += amount

    def total_records(self):
        return self.processed + self.rejected
