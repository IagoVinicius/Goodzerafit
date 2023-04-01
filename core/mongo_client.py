from dataclasses import dataclass
import pymongo
from decouple import config
from bson import ObjectId


@dataclass
class DBConfig:
    host: str
    port: int
    username: str
    password: str
    database_name: str


class DocumentDBException(Exception):
    def __init__(self, message: str):
        Exception.__init__(self, message)


class DocDBConnection:
    """
    Document DB Connection
    """

    def __init__(self, config: DBConfig):
        self.host = config.host
        self.port = config.port
        self.username = config.username
        self.password = config.password
        self.database_name = config.database_name
        self.connected = False
        self._client = None

    @property
    def client(self) -> pymongo.MongoClient:
        return self._client

    def connect(self):
        """Connects to DocumentDB database

        Raises:
            DocumentDBException: connection error
        """

        try:
            self._client = pymongo.MongoClient(host=self.host,
                                               port=self.port,
                                               username=self.username,
                                               password=self.password)

            self.db = self.client.get_database(self.database_name)
            self.connected = True
        except Exception as e:
            raise DocumentDBException(f'Error trying to connect to DocumentDB database='
                                      f'{self.database_name}: {e}') from e

    def close(self):
        """Close Document DB connection

        Raises:
            DocumentDBException: connection error
        """

        try:
            if self.connected:
                self.client.close()
                self.connected = False
        except Exception as e:
            raise DocumentDBException(f'Error trying to close connection with DocumentDB database='
                                      f'{self.database_name}: {e}') from e


class DocumentDBClient:
    def __init__(self, connection: DocDBConnection, collection_name: str,
                 max_pagination_size: int = None):

        self.max_pagination_size = max_pagination_size or 2
        self.connection = connection

        if not self.connection.connected:
            self.connection.connect()

        self.collection_name = collection_name
        self.collection = self.connection.db.get_collection(collection_name)

    def insert(self, item: dict) -> str:
        """Insert a new item in a DocumentDB collection

        Args:
            item (dict): item to insert

        Raises:
            DocumentDBException: insert error

        Returns:
            dict: inserted id
        """

        try:
            result = self.collection.insert_one(item)

            return result.inserted_id
        except Exception as e:
            raise DocumentDBException(f'Error inserting record in DocumentDB collection '
                                      f'{self.collection_name}: {e}') from e

    def update(self, query_filter: dict, item: dict) -> str:
        """Update a new item in a DocumentDB collection

        Args:
            query_filter (dict): query filter
            item (dict): item to be updated

        Raises:
            DocumentDBException: update error

        Returns:
            str: upserted id
        """

        try:
            result = self.collection.update_one(query_filter, item)

            if result.matched_count == 0:
                raise DocumentDBException('No record found')
            if result.modified_count == 0:
                raise DocumentDBException('No record modified')
            if result.modified_count > 1:
                raise DocumentDBException('More than one record modified')

            return result.upserted_id
        except Exception as e:
            raise DocumentDBException(f'Error updating record in DocumentDB collection '
                                      f'{self.collection_name}: {e}') from e

    def find_one(self, query):
        try:
            data = self.collection.find_one(query)
            return data if data else {}

        except Exception as e:
            raise DocumentDBException(f'Error finding records in DocumentDB collection '
                                      f'{self.collection_name}: {e}') from e

    def find(self, **kwargs):
        # sort = [("data_vencimento", pymongo.ASCENDING)]
        # offset = page * (self.max_pagination_size if not limit else limit)
        #
        # limit = self.max_pagination_size if not limit else limit

        query = kwargs.get('query', {})

        try:
            content = self.collection.find(query)
            data = [x for x in content]

            return data if data else {}

        except Exception as e:
            raise DocumentDBException(f'Error finding records in DocumentDB collection '
                                      f'{self.collection_name}: {e}') from e

    def aggregate_groups(self, query):
        try:
            cursor = self.collection.aggregate(query)
            data = [x for x in cursor]

            return data[0] if data else {}

        except Exception as e:
            raise DocumentDBException(f'Error finding records in DocumentDB collection '
                                      f'{self.collection_name}: {e}') from e


def get_connection() -> DocDBConnection:
    cfg = DBConfig(
        host=config('MONGO_HOST'),
        port=config('MONGO_PORT', cast=int),
        username=config('MONGO_USER'),
        password=config('MONGO_PASS'),
        database_name=config('MONGO_DATABASE')
    )

    _connection = DocDBConnection(cfg)
    _connection.connect()

    print('Connection to DocumentDB estabilished...')

    return _connection
