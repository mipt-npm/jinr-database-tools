import pathlib
from unittest import TestCase

from sqlalchemy import delete

from sdp.database import Database
from sdp.description import Description
from sdp.file_status import LoadStatus


class DatabaseTest(TestCase):

    schema_path = None
    data_path = None

    def setUp(self) -> None:
        self.database = Database.connect_from_file("config.json")
        self.clear_data()

    def load_data(self):
        description = Description.load(self.schema_path)
        load_result = self.database.load_data(description, self.data_path)
        self.assert_(load_result.status == LoadStatus.SUCCESS,
                     msg= load_result.to_string(self.data_path))

    def clear_data(self):
        description = Description.load(self.schema_path)
        with self.database.engine.connect() as conn:
            metadata = self.database._metadata(conn)
            table = metadata.tables[description["table"]]
            self.delete_data(conn, table, description)


    def delete_data(self, conn, table, description):
        pass

    def tearDown(self) -> None:
        self.clear_data()


class DetectorCSVTest(DatabaseTest):
    schema_path = pathlib.Path("data/detector_.json")
    data_path = pathlib.Path("data/detector_.csv")

    def test_load(self):
        self.load_data()

    def delete_data(self, conn, table, description):
        for i in range(10):
            statement = delete(table).where(
                table.c.detector_name == "\'{}\'".format(str(i))
            )
            with conn.begin():
                conn.execute(statement)


class RunInfoTest(DatabaseTest):

    def test_xml(self):
        # FIXME(Нет подходящей таблицы)
        description = Description.load("data/run_info.json")
        load_result = self.database.load_data(description, "data/run_info.xml")