"""
DATANORM File Wrappers
----------------------
The DatanormItem is updated by each file wrapper regarding to existing information in
the DatanormItem.

REFERENCE for technical details: https://docplayer.org/115761786-Technische-spezifikationen-der-datanorm-dateien-in-haufe-lexware.html  # noqa: E501
"""

from abc import ABC
import datetime
from decimal import Decimal
import mmap
import os
import re
from . import DatanormItem

DATANORM_REGEX = {
    "V": r"^(?P<Satzkennzeichen>[V])\s(?P<Datum>\d{6})(?P<Informationstext1>.{40})(?P<Informationstext2>.{40})(?P<Informationstext3>.{35})(?P<DatanormVersion>\d{2})(?P<Waehrung>.{3})",  # noqa: E501
    "A": r"^(?P<Satzkennzeichen>[A]);(?P<Verarbeitungskennzeichen>.{1});(?P<Artikelnummer>[^;]*);(?P<Textkennzeichen>[^;]*);(?P<Kurztext1>[^;]*);(?P<Kurztext2>[^;]*);(?P<Preiskennzeichen>[^;]*);(?P<Preiseinheit>[^;]*);(?P<Mengeneinheit>[^;]*);(?P<Preis>[^;]*);(?P<Rabattgruppe>[^;]*);(?P<Hauptwarengruppe>[^;]*);(?P<Langtextschluessel>[^;]*);",  # noqa: E501
    "B": r"^(?P<Satzkennzeichen>[B]);(?P<Verarbeitungskennzeichen>.{1});(?P<Artikelnummer>[^;]*);(?P<Matchcode>[^;]*);(?P<AltArtikelnummer>[^;]*);(?P<Katalogseite>[^;]*);(?P<RohstoffMerker>[^;]*);(?P<RohstoffKennzahl>[^;]*);(?P<RohstoffGewicht>[^;]*);(?P<EanGtin>[^;]*);(?P<Anbindungsnummer>[^;]*);(?P<Warengruppe>[^;]*);(?P<Kostenarten>[^;]*);(?P<MinVerpMenge>[^;]*);(?P<ErstellerKuerzel>[^;]*);(?P<Referenznummer>[^;]*);",  # noqa: E501
    "S": r"^(?P<Satzkennzeichen>[S]);(?P<NONE>[^;]*);(?P<HauptwarengruppeID>[^;]*);(?P<HauptwarengruppeName>[^;]*);(?P<WarengruppeID>[^;]*);(?P<WarengruppeName>[^;]*);",  # noqa: E501
    "S_2": r"^(?P<Satzkennzeichen>[S]);(?P<NONE>[^;]*);(?P<HauptwarengruppeID>[^;]*);(?P<HauptwarengruppeName>\s*);(?P<WarengruppeID>[^;]*);(?P<WarengruppeName>[^;]*);",  # noqa: E501
    "D": r"^(?P<Satzkennzeichen>[D]);(?P<Verarbeitungskennzeichen>.{1});(?P<Artikelnummer>[^;]*);(?P<Zeilennummer>\d*);(?P<Unterkennzeichen>[^;]*);(?P<Text>[^;]*);(?P<Zeilentext>[^;]*);",  # noqa: E501
    "T": r"^(?P<Satzkennzeichen>[T]);(?P<Verarbeitungskennzeichen>.{1});(?P<Langtextnummer>[^;]*);(?P<Zeilennummer>\d*);(?P<Unterkennzeichen>[^;]*);(?P<Text>[^;]*);(?P<Zeilentext>[^;]*);",  # noqa: E501
    "P": r"^(?P<Satzkennzeichen>[P]);(?P<Verarbeitungskennzeichen>.{1});(?P<Artikelnummer>[^;]*);(?P<Preiskennzeichen>\d*);(?P<Preis>\d*);(?P<RabattkennzeichenA>[^;]*);(?P<RabattOrMultiplikatorA>[^;]*);(?P<RabattkennzeichenB>[^;]*);(?P<RabattOrMultiplikatorB>[^;]*);(?P<RabattkennzeichenC>[^;]*);(?P<RabattOrMultiplikatorC>[^;]*);(?P<NaechsterArtikel>.*)",  # noqa: E501
    "P_SUB": r"^(?P<Artikelnummer>[^;]*);(?P<Preiskennzeichen>\d*);(?P<Preis>\d*);(?P<RabattkennzeichenA>[^;]*);(?P<RabattOrMultiplikatorA>[^;]*);(?P<RabattkennzeichenB>[^;]*);(?P<RabattOrMultiplikatorB>[^;]*);(?P<RabattkennzeichenC>[^;]*);(?P<RabattOrMultiplikatorC>[^;]*);(?P<NaechsterArtikel>.*)",  # noqa: E501
    "R": r"^(?P<Satzkennzeichen>[R]);(?P<NONE>[^;]*);(?P<Rabattgruppe>[^;]*);(?P<Rabattkennzeichen>\d*);(?P<RabattOrMultiplikator>\d*);(?P<Rabattgruppenbezeichnung>[^;]*);(?P<NONE>[^;]*);",  # noqa: E501
}


class DatanormFile(ABC):
    encoding = "cp850"
    datanorm_file: str

    _regex_filename_prefix: str = r".+\."
    _regex_filename_suffix: str = r"\..+"

    def __init__(
        self,
        datanorm_file: str,
    ) -> None:
        """DATANORM file wrapper

        Args:
            datanorm_file (str): path to the DATANORM file, the wrapper represents
        """
        self.datanorm_file = datanorm_file
        super().__init__()

    def file_name_is_valid(self) -> bool:
        """Checks if the file name follows the DATANORM file name conventions

        Returns:
            bool: True if the file name is compliant
        """
        upper_basename = os.path.basename(self.datanorm_file).upper()
        prefix = re.search(self._regex_filename_prefix, upper_basename)
        suffix = re.search(self._regex_filename_suffix, upper_basename)
        return prefix is not None and suffix is not None

    def parse(self, di: DatanormItem):
        """Updates the datanorm item with the information from the DATANORM file.

        Args:
            di (DatanormItem): Datanorm item to update.
        """
        pass

    def _parse_line(self, line: tuple, di: DatanormItem):
        """Updates the datanorm item with the information from the given lines.

        Args:
            line (tuple): "Satzkennzeichen" and the whole line
            di (DatanormItem): datanorm item to update
        """
        pass


class DatanormBaseFile(DatanormFile):
    _regex_filename_prefix = r"^DATANORM"
    _regex_filename_suffix = r"\.\d{3}$"

    def parse(self, di: DatanormItem, id: str | None = None):
        """Searches for EAN/GTIN/Art.No. in the given DATANORM file and updates the
        Datanorm item.

        Args:
            di (DatanormItem): Datanorm item to update.
            id (str | None, optional): EAN/GTIN/Art.No. to search for. Defaults to None.
        """
        lines = self._search_file_for_id(id)

        if lines is not None:
            for line in lines.items():
                self._parse_line(line, di)
            di.is_valid = True

    def _search_file_for_id(self, id: str) -> dict | None:
        """Lookup EAN/GTIN/Art.No. in the DATANORM file

        Args:
            id (str): EAN/GTIN/Art.No. to look for

        Returns:
            dict | None: Parsed lines, containing the product with the given ID
        """
        if not os.path.isfile(self.datanorm_file):
            return

        ean_pattern = bytes(f";{id};", encoding=self.encoding)
        lines = None

        with open(self.datanorm_file, "r+") as file_obj:
            mm_object = mmap.mmap(
                file_obj.fileno(), length=0, access=mmap.ACCESS_READ, offset=0
            )
            line_v = mm_object.readline()
            while True:
                line = mm_object.readline()
                if line == b"":
                    break
                elif line.startswith(b"A"):
                    line_a = line
                elif line.find(ean_pattern) != -1:
                    lines = dict()
                    lines["A"] = line_a.decode(self.encoding).strip()
                    lines["B"] = line.decode(self.encoding).strip()
                    lines["V"] = line_v.decode(self.encoding).strip()
                    break
        file_obj.close()
        return lines

    def _parse_line(self, line: tuple, di: DatanormItem):
        """Updates the datanorm item with the information from the given lines.

        Args:
            line (tuple): "Satzkennzeichen" and the whole line
            di (DatanormItem): datanorm item to update
        """
        match = re.search(DATANORM_REGEX[line[0]], line[1])
        if match.group("Satzkennzeichen") == "V":
            di.date = datetime.datetime.strptime(match.group("Datum"), "%d%m%y")
            di.header_1 = match.group("Informationstext1").rstrip()
            di.header_2 = match.group("Informationstext2").rstrip()
            di.header_3 = match.group("Informationstext3").rstrip()
            di.version = int(match.group("DatanormVersion"))
            di.currency = match.group("Waehrung")

        elif match.group("Satzkennzeichen") == "A":
            di.type = match.group("Verarbeitungskennzeichen")
            di.article_id = match.group("Artikelnummer")
            di.text_indicator = match.group("Textkennzeichen")
            di.short_text_1 = match.group("Kurztext1")
            di.short_text_2 = match.group("Kurztext2")
            di.price_indicator = match.group("Preiskennzeichen")
            di.price_unit_raw = match.group("Preiseinheit")
            di.unit_of_measure = match.group("Mengeneinheit")
            di.price_retail = Decimal(match.group("Preis")) / Decimal(100)
            di.discount_group = match.group("Rabattgruppe")
            di.main_product_group_id = match.group("Hauptwarengruppe")
            di.longtext_key = match.group("Langtextschluessel")

        elif match.group("Satzkennzeichen") == "B":
            di.matchcode = match.group("Matchcode")
            di.alt_article_id = match.group("AltArtikelnummer")
            di.catalogue_page = match.group("Katalogseite")
            di.raw_material_key = match.group("RohstoffKennzahl")
            di.raw_material_weight = match.group("RohstoffGewicht")
            di.ean = match.group("EanGtin")
            di.product_group_id = match.group("Warengruppe")
            di.type_of_cost = match.group("Kostenarten")
            di.minimum_packaging_quantity = match.group("MinVerpMenge")
            di.reference_number = match.group("Referenznummer")


class DatanormProductGroupFile(DatanormFile):
    encoding = "cp1252"
    _regex_filename_suffix = r"\.WRG$"

    def parse(self, di: DatanormItem):
        if di.is_valid:
            lines = self._search_file_for_group_ids(
                di.main_product_group_id, di.product_group_id
            )
            if lines is not None:
                for line in lines.items():
                    self._parse_line(line, di)

    def _search_file_for_group_ids(
        self, main_group_id: str, group_id: str
    ) -> dict | None:
        """Lookup Art.No. in the DATANORM.WRG file

        Args:
            datanorm_wrg_file (str): Path to the DATANORM product group file
            id (str): EAN/GTIN/Art.No. to look for

        Returns:
            dict | None: Parsed lines, containing the product with the given ID
        """
        if not os.path.isfile(self.datanorm_file):
            return

        main_category_pattern = bytes(f";{main_group_id};", encoding=self.encoding)
        sub_category_pattern = bytes(
            f";{main_group_id};;{group_id};",
            encoding=self.encoding,
        )
        lines = None

        with open(self.datanorm_file, "r+") as file_obj:
            mm_object = mmap.mmap(
                file_obj.fileno(), length=0, access=mmap.ACCESS_READ, offset=0
            )
            line_v = mm_object.readline()
            while True:
                line = mm_object.readline()
                if line == b"":
                    break
                elif line.find(main_category_pattern) != -1 and lines is None:
                    lines = dict()
                    lines["V"] = line_v.decode(self.encoding).strip()
                    lines["S"] = line.decode(self.encoding).strip()
                elif line.find(sub_category_pattern) != -1:
                    lines["S_2"] = line.decode(self.encoding).strip()
                    break
        file_obj.close()
        return lines

    def _parse_line(self, line: tuple, di: DatanormItem):
        """Sorts the parsed data into the properties of this object

        Args:
            match (re.Match[str]): Match object for a single DATANORM line
        """
        match = re.search(DATANORM_REGEX[line[0]], line[1])

        if match.group("Satzkennzeichen") == "S" and di.main_product_group_name is None:
            di.main_product_group_name = match.group("HauptwarengruppeName")

        # This if has to be seperate since some WRG files do not have only main product
        # group names.
        if (
            match.group("Satzkennzeichen") == "S"
            and di.product_group_name is None
            and match.group("WarengruppeName").strip() != ""
        ):
            di.product_group_name = match.group("WarengruppeName")


class DatanormPriceFile(DatanormFile):
    _regex_filename_prefix = r"^DATPREIS"
    _regex_filename_suffix = r"\.\d{3}$"

    def _discount_group(price: Decimal, discount_group: str) -> Decimal:
        return price

    def _discount_rate(price: Decimal, discount_rate) -> Decimal:
        discount_rate_dec = Decimal(discount_rate) / Decimal(10000)
        result = price - price * discount_rate_dec
        return round(result, 2)

    def _multiplicator(price: Decimal, factor) -> Decimal:
        factor_dec = Decimal(factor) / Decimal(1000)
        result = price * factor_dec
        return round(result, 2)

    def _inflation_surcharge(price: Decimal, factor) -> Decimal:
        factor_dec = Decimal(factor) / Decimal(100)
        result = price + price * factor_dec
        return round(result, 2)

    compute_price = {
        "0": _discount_group,
        "1": _discount_rate,
        "2": _multiplicator,
        "3": _inflation_surcharge,
    }

    def parse(self, di: DatanormItem):
        if di.is_valid:
            lines = self._search_file_for_article_id(di.article_id)
            if lines is not None:
                for line in lines.items():
                    self._parse_line(line, di)

    def _search_file_for_article_id(self, article_id: str) -> dict | None:
        """Lookup Art.No. in the DATPREIS file

        Args:
            article_id (str): Art.No. to look for

        Returns:
            dict | None: Parsed lines, containing the discount information with the \
                         given ID
        """
        if not os.path.isfile(self.datanorm_file):
            return

        article_id_pattern = bytes(f";{article_id};", encoding=self.encoding)
        lines = None

        with open(self.datanorm_file, "r+") as file_obj:
            mm_object = mmap.mmap(
                file_obj.fileno(), length=0, access=mmap.ACCESS_READ, offset=0
            )
            line_v = mm_object.readline()
            while True:
                line = mm_object.readline()
                if line == b"":
                    break
                elif line.find(article_id_pattern) != -1 and lines is None:
                    lines = dict()
                    lines["V"] = line_v.decode(self.encoding).strip()
                    lines["P"] = line.decode(self.encoding).strip()
                elif line.find(article_id_pattern) != -1:
                    # Some suppliers distribute the article over multiple lines
                    lines["P"] += line.decode(self.encoding).lstrip("P;A;").strip()
        file_obj.close()
        return lines

    def _parse_line(self, line: tuple, di: DatanormItem):
        match = re.search(DATANORM_REGEX[line[0]], line[1])

        if match.group("Satzkennzeichen") == "P":
            next_article = line[1][4:]
            # iterate over the articles in the line
            while next_article:
                match = re.search(DATANORM_REGEX["P_SUB"], next_article)
                # skip wrong article IDs
                if match.group("Artikelnummer") == di.article_id:
                    self._update_prices(di, match)

                next_article = match.group("NaechsterArtikel").strip()

    def _update_prices(self, di: DatanormItem, line_groups: re.Match[str]):
        """Computes the prices regarding to the settings in the file.

        Args:
            di (DatanormItem): Datanorm item to update
            line_groups (re.Match[str]): match object with the price information
        """
        price = Decimal(line_groups.group("Preis")) / Decimal(100)
        price_type = line_groups.group("Preiskennzeichen")
        discount_type = line_groups.group("RabattkennzeichenA")
        discount_factor = line_groups.group("RabattOrMultiplikatorA")
        if price_type == "1":
            di.price_retail = price
            if discount_type != "":
                di.price_wholesale = self.compute_price[discount_type](
                    price, discount_factor
                )
        elif price_type == "2":
            di.price_wholesale = price
        elif price_type == "3":
            # Werkspreis, not yet processed
            pass


class DatanormDiscountFile(DatanormFile):
    _regex_filename_prefix = r"^DATANORM"
    _regex_filename_suffix = r"\.RAB$"


def file_name_is_valid(datanorm_file_type: DatanormFile, filename: str) -> bool:
    """This function verifies the compliance of file names for datanorm files.

    Args:
        datanorm_file_type (DatanormFile): Class of the datanorm file to check
        filename (str): Basename of the file

    Returns:
        bool: True if the filename is compliant
    """
    prefix = re.search(datanorm_file_type._regex_filename_prefix, filename.upper())
    suffix = re.search(datanorm_file_type._regex_filename_suffix, filename.upper())
    return prefix is not None and suffix is not None
