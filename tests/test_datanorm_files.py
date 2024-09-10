from datetime import datetime
from decimal import Decimal
from datanorm import (
    DatanormBaseFile,
    DatanormDiscountFile,
    DatanormPriceFile,
    DatanormItem,
    DatanormProductGroupFile,
    file_name_is_valid,
)
from importlib import import_module
from importlib.resources import files
import unittest

GOOD_EAN_13 = "3250614315336"
GOOD_EAN_8 = "90311017"
BAD_EAN1 = "12323"
BAD_EAN2 = "1234567890123"


class TestDatanorm(unittest.TestCase):

    def test_file_name_is_valid_DatanormBaseFile(self):
        self.assertTrue(file_name_is_valid(DatanormBaseFile, "Datanorm.001"))
        self.assertTrue(file_name_is_valid(DatanormBaseFile, "datanorm.001"))
        self.assertTrue(file_name_is_valid(DatanormBaseFile, "DATANORM.001"))
        self.assertTrue(file_name_is_valid(DatanormBaseFile, "DATANORM_123.999"))

        self.assertFalse(file_name_is_valid(DatanormBaseFile, "DATPREIS.001"))
        self.assertFalse(file_name_is_valid(DatanormBaseFile, "datanor.001"))
        self.assertFalse(file_name_is_valid(DatanormBaseFile, "DATANORM.A01"))
        self.assertFalse(file_name_is_valid(DatanormBaseFile, "DATANORM.0001"))

    def test_file_name_is_valid_DatanormProductGroupFile(self):
        self.assertTrue(file_name_is_valid(DatanormProductGroupFile, "Datanorm.WRG"))
        self.assertTrue(file_name_is_valid(DatanormProductGroupFile, "Anything.WRG"))
        self.assertTrue(file_name_is_valid(DatanormProductGroupFile, "DATANORM.wrg"))
        self.assertTrue(file_name_is_valid(DatanormProductGroupFile, "x.wrg"))

        self.assertFalse(file_name_is_valid(DatanormProductGroupFile, "DATANORM.001"))
        self.assertFalse(file_name_is_valid(DatanormProductGroupFile, "datanor.AWRG"))
        self.assertFalse(file_name_is_valid(DatanormProductGroupFile, ".wrg"))

    def test_file_name_is_valid_DatanormPriceFile(self):
        self.assertTrue(file_name_is_valid(DatanormPriceFile, "Datpreis.001"))
        self.assertTrue(file_name_is_valid(DatanormPriceFile, "datpreis.001"))
        self.assertTrue(file_name_is_valid(DatanormPriceFile, "DATPREIS.001"))
        self.assertTrue(file_name_is_valid(DatanormPriceFile, "DATPREIS_123.999"))

        self.assertFalse(file_name_is_valid(DatanormPriceFile, "DATANORM.001"))
        self.assertFalse(file_name_is_valid(DatanormPriceFile, "datprei.001"))
        self.assertFalse(file_name_is_valid(DatanormPriceFile, "DATPREIS.A01"))
        self.assertFalse(file_name_is_valid(DatanormPriceFile, "DATPREIS.0001"))

    def test_file_name_is_valid_DatanormDiscountFile(self):
        self.assertTrue(file_name_is_valid(DatanormDiscountFile, "Datanorm.RAB"))
        self.assertTrue(file_name_is_valid(DatanormDiscountFile, "datanorm_134.RAB"))
        self.assertTrue(file_name_is_valid(DatanormDiscountFile, "DATANORM.rab"))

        self.assertFalse(file_name_is_valid(DatanormDiscountFile, "DATANORM.001"))
        self.assertFalse(file_name_is_valid(DatanormDiscountFile, "datanor.ARAB"))
        self.assertFalse(file_name_is_valid(DatanormDiscountFile, "x.rab"))
        self.assertFalse(file_name_is_valid(DatanormDiscountFile, ".rab"))


class TestDatanormBaseFile(unittest.TestCase):

    def setUp(self):
        this_package = import_module(".", package="tests")
        self.DATANORM_PATH = str(files(this_package).joinpath("datanorm_test.001"))
        return super().setUp()

    def test_file_name_is_valid_abs_path(self):
        dut = DatanormBaseFile(self.DATANORM_PATH)
        self.assertTrue(dut.file_name_is_valid())

    def test_file_name_is_valid_rel_path(self):
        dut = DatanormBaseFile('./data/Datanorm/DATANORM.001')
        self.assertTrue(dut.file_name_is_valid())

    def test_search_file_for_id(self):
        dut = DatanormBaseFile(self.DATANORM_PATH)

        expected_result = {
            "V": "V 010199Firmenname                              E-Business                              Ansprechpartner, Tel.-Nr.          04EUR",  # noqa: E501
            "A": "A;N;899977;00;HAGER Leitungsschutzschalter AC C 16A 3p;MCS316 415V 3TE 50Hz Zusatzeinr.mögl;1;0;Stk;10000;HB86;01;;",  # noqa: E501
            "B": "B;N;899977;MCS316;MCS316;;0;0;0;3250614315336;;12;0;1;;;",
        }
        self.assertEqual(dut._search_file_for_id(GOOD_EAN_13), expected_result)

        self.assertIsNone(dut._search_file_for_id(BAD_EAN1))

    def test_search_file_for_id_nonexisting_file(self):
        dut = DatanormBaseFile("Datanorm.123")
        self.assertIsNone(dut._search_file_for_id(GOOD_EAN_13))

    def test_parse_line(self):
        di = DatanormItem()
        self.assertFalse(di.is_valid)

        dut = DatanormBaseFile(self.DATANORM_PATH)

        lines = {
            "V": "V 010199Firmenname                              E-Business                              Ansprechpartner, Tel.-Nr.          04EUR",  # noqa: E501
            "A": "A;N;899977;00;HAGER Leitungsschutzschalter AC C 16A 3p;MCS316 415V 3TE 50Hz Zusatzeinr.mögl;1;0;Stk;10000;HB86;01;;",  # noqa: E501
            "B": "B;N;899977;MCS316;MCS316;;0;0;0;3250614315336;;12;0;1;;;",
        }

        for line in lines.items():
            dut._parse_line(line, di)

        self.assertFalse(di.is_valid)
        self.assertEqual(di.date, datetime(1999, 1, 1))
        self.assertEqual(di.header_1, "Firmenname")
        self.assertEqual(di.header_2, "E-Business")
        self.assertEqual(di.header_3, "Ansprechpartner, Tel.-Nr.")
        self.assertEqual(di.version, 4)
        self.assertEqual(di.currency, "EUR")
        self.assertEqual(di.type, "N")
        self.assertEqual(di.article_id, "899977")
        self.assertEqual(di.text_indicator, "00")
        self.assertEqual(di.short_text_1, "HAGER Leitungsschutzschalter AC C 16A 3p")
        self.assertEqual(di.short_text_2, "MCS316 415V 3TE 50Hz Zusatzeinr.mögl")
        self.assertEqual(di.price_indicator, "1")
        self.assertEqual(di.price_unit_raw, "0")
        self.assertEqual(di.price_unit, 1)
        self.assertEqual(di.unit_of_measure, "Stk")
        self.assertEqual(di.price_retail, Decimal("100.00"))
        self.assertEqual(di.discount_group, "HB86")
        self.assertEqual(di.main_product_group_id, "01")
        self.assertIsNone(di.main_product_group_name)
        self.assertEqual(di.product_group_id, "12")
        self.assertIsNone(di.product_group_name)
        self.assertEqual(di.longtext_key, "")
        self.assertEqual(di.matchcode, "MCS316")
        self.assertEqual(di.alt_article_id, "MCS316")
        self.assertEqual(di.catalogue_page, "")
        self.assertEqual(di.raw_material_key, "0")
        self.assertEqual(di.raw_material_weight, "0")
        self.assertEqual(di.ean, GOOD_EAN_13)
        self.assertEqual(di.type_of_cost, "0")
        self.assertEqual(di.minimum_packaging_quantity, "1")
        self.assertEqual(di.reference_number, "")

    def test_parse(self):
        di = DatanormItem()
        dut = DatanormBaseFile(self.DATANORM_PATH)
        dut.parse(di, GOOD_EAN_13)

        self.assertTrue(di.is_valid)
        self.assertEqual(di.date, datetime(1999, 1, 1))
        self.assertEqual(di.header_1, "Firmenname")
        self.assertEqual(di.header_2, "E-Business")
        self.assertEqual(di.header_3, "Ansprechpartner, Tel.-Nr.")
        self.assertEqual(di.version, 4)
        self.assertEqual(di.currency, "EUR")
        self.assertEqual(di.type, "N")
        self.assertEqual(di.article_id, "899977")
        self.assertEqual(di.text_indicator, "00")
        self.assertEqual(di.short_text_1, "HAGER Leitungsschutzschalter AC C 16A 3p")
        self.assertEqual(di.short_text_2, "MCS316 415V 3TE 50Hz Zusatzeinr.mögl")
        self.assertEqual(di.price_indicator, "1")
        self.assertEqual(di.price_unit_raw, "0")
        self.assertEqual(di.price_unit, 1)
        self.assertEqual(di.unit_of_measure, "Stk")
        self.assertEqual(di.price_retail, Decimal("100.00"))
        self.assertEqual(di.discount_group, "HB86")
        self.assertEqual(di.main_product_group_id, "01")
        self.assertIsNone(di.main_product_group_name)
        self.assertEqual(di.product_group_id, "12")
        self.assertIsNone(di.product_group_name)
        self.assertEqual(di.longtext_key, "")
        self.assertEqual(di.matchcode, "MCS316")
        self.assertEqual(di.alt_article_id, "MCS316")
        self.assertEqual(di.catalogue_page, "")
        self.assertEqual(di.raw_material_key, "0")
        self.assertEqual(di.raw_material_weight, "0")
        self.assertEqual(di.ean, GOOD_EAN_13)
        self.assertEqual(di.type_of_cost, "0")
        self.assertEqual(di.minimum_packaging_quantity, "1")
        self.assertEqual(di.reference_number, "")


class TestDatanormProductGroupFile(unittest.TestCase):

    def setUp(self):
        this_package = import_module(".", package="tests")
        self.DATANORM_PATH = str(files(this_package).joinpath("datanorm_test.001"))
        self.DATANORM_WRG_PATH = str(files(this_package).joinpath("datanorm_test.WRG"))
        return super().setUp()

    def test_file_name_is_valid_abs_path(self):
        dut = DatanormProductGroupFile(self.DATANORM_WRG_PATH)
        self.assertTrue(dut.file_name_is_valid())

    def test_file_name_is_valid_rel_path(self):
        dut = DatanormProductGroupFile('./data/Datanorm/DATANORM.WRG')
        self.assertTrue(dut.file_name_is_valid())

    def test_search_file_for_id(self):
        dut = DatanormProductGroupFile(self.DATANORM_WRG_PATH)

        expected_result = {
            "V": "V 010199Firmenname                              DATANORM WARENGRP                                                          04EUR",  # noqa: E501
            "S": "S;;01;Installationsgeräte & -systeme;;;",
            "S_2": "S;;01;;12;Sicherungsautomaten & Hauptschalter;",
        }
        self.assertEqual(dut._search_file_for_group_ids("01", "12"), expected_result)
        self.assertIsNone(dut._search_file_for_group_ids("04", "12"))

    def test_search_file_for_id_nonexisting_file(self):
        dut = DatanormProductGroupFile("Datanorm.wrg")
        self.assertIsNone(dut._search_file_for_group_ids("01", "12"))

    def test_parse_line_separate_lines(self):
        di = DatanormItem()
        di.main_product_group_id = "01"
        di.product_group_id = "12"

        dut = DatanormProductGroupFile("")

        lines = {
            "V": "V 010199Firmenname                              DATANORM WARENGRP                                                          04EUR",  # noqa: E501
            "S": "S;;01;Installationsgeräte & -systeme;;;",
            "S_2": "S;;01;;12;Sicherungsautomaten & Hauptschalter;",
        }

        for line in lines.items():
            dut._parse_line(line, di)

        self.assertEqual(di.main_product_group_id, "01")
        self.assertEqual(di.main_product_group_name, "Installationsgeräte & -systeme")
        self.assertEqual(di.product_group_id, "12")
        self.assertEqual(di.product_group_name, "Sicherungsautomaten & Hauptschalter")

    def test_parse_line_single_line(self):
        di = DatanormItem()
        di.main_product_group_id = "02"
        di.product_group_id = "020101"

        dut = DatanormProductGroupFile("")

        lines = {
            "V": "V 010199Firmenname                              DATANORM WARENGRP                                                          04EUR",  # noqa: E501
            "S": "S;;02;Kabel & Leitung;020101;Fernmeldekabel (Aussen /Innen);",
        }

        for line in lines.items():
            dut._parse_line(line, di)

        self.assertEqual(di.main_product_group_id, "02")
        self.assertEqual(di.main_product_group_name, "Kabel & Leitung")
        self.assertEqual(di.product_group_id, "020101")
        self.assertEqual(di.product_group_name, "Fernmeldekabel (Aussen /Innen)")

    def test_parse_line_only_main_product_group(self):
        di = DatanormItem()
        di.main_product_group_id = "03"
        di.product_group_id = ""

        dut = DatanormProductGroupFile("")

        lines = {
            "V": "V 010199Firmenname                              DATANORM WARENGRP                                                          04EUR",  # noqa: E501
            "S": "S;;89;Gummileitungen;;;",
        }

        for line in lines.items():
            dut._parse_line(line, di)

        self.assertEqual(di.main_product_group_id, "03")
        self.assertEqual(di.main_product_group_name, "Gummileitungen")
        self.assertEqual(di.product_group_id, "")
        self.assertIsNone(di.product_group_name)

    def test_parse_invalid_datanorm_item(self):
        di = DatanormItem()
        di.main_product_group_id = "01"
        di.product_group_id = "12"

        dut = DatanormProductGroupFile(self.DATANORM_WRG_PATH)
        dut.parse(di)

        self.assertFalse(di.is_valid)
        self.assertEqual(di.main_product_group_id, "01")
        self.assertIsNone(di.main_product_group_name)
        self.assertEqual(di.product_group_id, "12")
        self.assertIsNone(di.product_group_name)

    def test_parse_separate_lines(self):
        di = DatanormItem()
        di.main_product_group_id = "01"
        di.product_group_id = "12"
        di.is_valid = True

        dut = DatanormProductGroupFile(self.DATANORM_WRG_PATH)
        dut.parse(di)

        self.assertTrue(di.is_valid)
        self.assertEqual(di.main_product_group_id, "01")
        self.assertEqual(di.main_product_group_name, "Installationsgeräte & -systeme")
        self.assertEqual(di.product_group_id, "12")
        self.assertEqual(di.product_group_name, "Sicherungsautomaten & Hauptschalter")

    def test_parse_single_line(self):
        di = DatanormItem()
        di.main_product_group_id = "02"
        di.product_group_id = "020101"
        di.is_valid = True

        dut = DatanormProductGroupFile(self.DATANORM_WRG_PATH)
        dut.parse(di)

        self.assertEqual(di.main_product_group_id, "02")
        self.assertEqual(di.main_product_group_name, "Kabel & Leitung")
        self.assertEqual(di.product_group_id, "020101")
        self.assertEqual(di.product_group_name, "Fernmeldekabel (Aussen /Innen)")

    def test_parse_only_main_product_group(self):
        di = DatanormItem()
        di.main_product_group_id = "03"
        di.product_group_id = ""
        di.is_valid = True

        dut = DatanormProductGroupFile(self.DATANORM_WRG_PATH)
        dut.parse(di)

        self.assertEqual(di.main_product_group_id, "03")
        self.assertEqual(di.main_product_group_name, "Gummileitungen")
        self.assertEqual(di.product_group_id, "")
        self.assertIsNone(di.product_group_name)

    def test_file_name_is_valid(self):
        self.assertTrue(
            DatanormProductGroupFile(self.DATANORM_WRG_PATH).file_name_is_valid()
        )
        self.assertFalse(DatanormProductGroupFile("Test.123").file_name_is_valid())


class TestDatanormPriceFile(unittest.TestCase):

    def setUp(self):
        this_package = import_module(".", package="tests")
        self.DATANORM_PATH = str(files(this_package).joinpath("datanorm_test.001"))
        self.DATPREIS_PATH = str(files(this_package).joinpath("datpreis_test.001"))
        return super().setUp()
    
    def test_file_name_is_valid_abs_path(self):
        dut = DatanormPriceFile(self.DATPREIS_PATH)
        self.assertTrue(dut.file_name_is_valid())

    def test_file_name_is_valid_rel_path(self):
        dut = DatanormPriceFile('./data/Datanorm/DATPREIS.999')
        self.assertTrue(dut.file_name_is_valid())

    def test_search_file_for_article_id_over_single_line(self):
        dut = DatanormPriceFile(self.DATPREIS_PATH)
        expected_result = {
            "V": "V 010199Firmenname                              DATANORM WARENGRP                                                          04EUR",  # noqa: E501
            "P": "P;A;996633;1;10000;1;1000;;;;;996634;1;10000;1;1000;;;;;996635;1;10000;1;1000;;;;;",  # noqa: E501
        }
        self.assertEqual(dut._search_file_for_article_id("996634"), expected_result)
        self.assertIsNone(dut._search_file_for_article_id("1234"))

    def test_search_file_for_article_id_over_two_lines(self):
        dut = DatanormPriceFile(self.DATPREIS_PATH)
        expected_result = {
            "V": "V 010199Firmenname                              DATANORM WARENGRP                                                          04EUR",  # noqa: E501
            "P": "P;A;899976;1;11000;;;;;;;899976;2;11500;;;;;;;899977;1;10000;;;;;;;899977;2;9000;;;;;;;899978;1;8000;;;;;;;899978;2;7000;;;;;;;",  # noqa: E501
        }
        self.assertEqual(dut._search_file_for_article_id("899977"), expected_result)

    def test_search_file_for_id_nonexisting_file(self):
        dut = DatanormPriceFile("Datpreis.123")
        self.assertIsNone(dut._search_file_for_article_id("899977"))

    def test_parse_line_separate_lines(self):
        di = DatanormItem()
        di.article_id = "899977"
        dut = DatanormPriceFile("")
        lines = {
            "V": "V 010199Firmenname                              DATANORM WARENGRP                                                          04EUR",  # noqa: E501
            "P": "P;A;899976;1;11000;;;;;;;899976;2;11500;;;;;;;899977;1;10000;;;;;;;899977;2;9000;;;;;;;899978;1;8000;;;;;;;899978;2;7000;;;;;;;",  # noqa: E501
        }
        for line in lines.items():
            dut._parse_line(line, di)
        self.assertEqual(di.price_retail, Decimal("100.00"))
        self.assertEqual(di.price_wholesale, Decimal("90.00"))

    def test_parse_line_single_line_rabattsatz(self):
        di = DatanormItem()
        di.article_id = "996634"
        dut = DatanormPriceFile("")
        lines = {
            "V": "V 010199Firmenname                              DATANORM WARENGRP                                                          04EUR",  # noqa: E501
            "P": "P;A;996633;1;11840;1;6781;;;;;996634;1;12920;1;6568;;;;;996635;1;15760;1;7039;;;;;",  # noqa: E501
        }
        for line in lines.items():
            dut._parse_line(line, di)
        self.assertEqual(di.price_retail, Decimal("129.20"))
        self.assertEqual(di.price_wholesale, Decimal("44.34"))

    def test_parse_line_single_line_only_wholesale(self):
        di = DatanormItem()
        di.article_id = "996834"
        di.price_retail = Decimal("70.00")
        dut = DatanormPriceFile("")
        lines = {
            "V": "V 010199Firmenname                              DATANORM WARENGRP                                                          04EUR",  # noqa: E501
            "P": "P;A;996833;2;7000;1;0;1;0;1;0;996834;2;6000;1;0;1;0;1;0;996835;2;6500;1;0;1;0;1;0;",  # noqa: E501
        }
        for line in lines.items():
            dut._parse_line(line, di)
        self.assertEqual(di.price_retail, Decimal("70.00"))
        self.assertEqual(di.price_wholesale, Decimal("60.00"))

    def test_parse_invalid_datanorm_item(self):
        di = DatanormItem()
        di.article_id = "899977"
        dut = DatanormPriceFile(self.DATPREIS_PATH)
        dut.parse(di)
        self.assertFalse(di.is_valid)
        self.assertEqual(di.price_retail, Decimal("0"))
        self.assertEqual(di.price_wholesale, Decimal("0"))

    def test_parse_separate_lines(self):
        di = DatanormItem()
        di.article_id = "899977"
        di.is_valid = True
        dut = DatanormPriceFile(self.DATPREIS_PATH)
        dut.parse(di)
        self.assertTrue(di.is_valid)
        self.assertEqual(di.price_retail, Decimal("100.00"))
        self.assertEqual(di.price_wholesale, Decimal("90.00"))
