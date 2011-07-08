from sharded_counter import ShardedCounter

class UserCounter(db.Model):
    '''Keeps a global count of registered users, used to create `UserLog`s.'''
    @staticmethod
    def get_count():
        '''Get the number of registered users'''
        return ShardedCounter.get_count('user_counter')

    @staticmethod
    def add_to_counter(n):
        '''Add n to the counter (n < 0 is valid)'''
        ShardedCounter.add_to_counter('user_counter', n)

    @staticmethod
    def change_number_of_shards(num):
        '''Change the number of shards to num'''
        ShardedCounter.change_number_of_shards('user_counter', num)
