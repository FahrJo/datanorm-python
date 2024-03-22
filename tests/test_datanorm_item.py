from datanorm import DatanormItem
from importlib import import_module
from importlib.resources import files
import unittest

GOOD_EAN_13 = "3250614315336"
GOOD_EAN_8 = "90311017"
BAD_EAN1 = "12323"
BAD_EAN2 = "1234567890123"


class TestDatanormItem(unittest.TestCase):

    def setUp(self):
        this_package = import_module(".", package="tests")
        self.DATANORM_PATH = str(files(this_package).joinpath("datanorm_test.001"))
        self.DATANORM_WRG_PATH = str(files(this_package).joinpath("datanorm_test.WRG"))
        return super().setUp()

    def test_manufacturer_name(self):
        dut = DatanormItem()
        result = {
            "ACME some product": "ACME",
            "AC'ME some product": "AC'ME",
            "AC-ME some product": "AC-ME",
            "ACMEsome product": None,
            "AC some product": "AC",
            "A product": None,
            "123 product": "123",
            "AC-ME'9 product": "AC-ME'9",
        }
        for input, expectation in result.items():
            dut.short_text_1 = input
            self.assertEqual(dut.manufacturer_name, expectation)

    def test_item_name(self):
        dut = DatanormItem()
        result = {
            "ACME some product": "some product",
            "AC'ME some product": "some product",
            "AC-ME some product": "some product",
            "ACMEsome product": "ACMEsome product",
            "AC some product": "some product",
            "A product": "A product",
            "123 product": "product",
        }
        for input, expectation in result.items():
            dut.short_text_1 = input
            self.assertEqual(dut.item_name, expectation)

    def test_description(self):
        dut = DatanormItem()
        dut.short_text_1 = "KT1"
        dut.short_text_2 = "KT2"
        dut.longtext = "LT"
        dut.dimensions_text = "DT"
        result = {
            "00": "KT1\nKT2",
            "01": "KT1",
            "10": "LT\nKT2",
            "20": "KT1\nDT",
            "30": "LT\nDT",
            "40": "KT1\nKT2\nLT",
            "41": "KT1\nLT",
            "50": "KT1\nKT2\nDT",
            "51": "KT1\nDT",
            "60": "KT1\nKT2\nLT\nDT",
            "61": "KT1\nLT\nDT",
            "99": "KT1\nKT2",
        }
        for input, expectation in result.items():
            dut.text_indicator = input
            self.assertEqual(dut.description, expectation)

    def test_price_unit_getter(self):
        dut = DatanormItem()
        dut.price_unit_raw = "0"
        self.assertEqual(dut.price_unit, 1)
        dut.price_unit_raw = "1"
        self.assertEqual(dut.price_unit, 10)
        dut.price_unit_raw = "2"
        self.assertEqual(dut.price_unit, 100)
        dut.price_unit_raw = "3"
        self.assertEqual(dut.price_unit, 1000)
        dut.price_unit_raw = "4"
        self.assertIsNone(dut.price_unit)

    def test_price_unit_setter(self):
        dut = DatanormItem()
        dut.price_unit = 1
        self.assertEqual(dut.price_unit_raw, "0")
        dut.price_unit = 10
        self.assertEqual(dut.price_unit_raw, "1")
        dut.price_unit = 100
        self.assertEqual(dut.price_unit_raw, "2")
        dut.price_unit = 1000
        self.assertEqual(dut.price_unit_raw, "3")
        dut.price_unit = 2
        self.assertIsNone(dut.price_unit_raw)
