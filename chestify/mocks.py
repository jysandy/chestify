class ObjectMock:
    def __init__(self, key='sandy/work/quux.psd', bucket_name='chestify'):
        self.key = key
        self.size = 0
        self.last_modified = 'Dec 21 2012'
        self.bucket_name = bucket_name

    def put(self, *args, **kwargs):
        return {
            'ResponseMetadata': {
                'HTTPStatusCode': 200
            }
        }


