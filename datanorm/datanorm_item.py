"""
A class that contains informations of a single DATANORM article

REFERENCE for technical details: https://docplayer.org/115761786-Technische-spezifikationen-der-datanorm-dateien-in-haufe-lexware.html  # noqa: E501
"""

import datetime
from decimal import Decimal
import re


class DatanormItem:
    _MANUFACTURER_REGEX = r"^([A-Z|0-9|\'|-]{2,})\s"

    is_valid: bool = False

    date: datetime = datetime.datetime(1970, 1, 1)
    header_1: str = ""
    header_2: str = ""
    header_3: str = ""
    version: int = 0
    currency: str = ""
    type: str = ""  # enum?
    article_id: str = ""
    text_indicator: str = ""
    short_text_1: str = ""
    short_text_2: str = ""
    price_indicator: str = ""  # 1: Brutto, 2: Netto
    price_unit_raw: str = (
        ""  # 0: per 1 unit, 1: per 10 units, 2: per 100 units 3: per 1000 units
    )
    unit_of_measure: str = ""
    price_retail: Decimal = Decimal("0")
    price_wholesale: Decimal = Decimal("0")
    discount_group: str = ""
    main_product_group_id: str = ""
    main_product_group_name: str | None = None
    product_group_id: str = ""
    product_group_name: str | None = None
    longtext_key: str = ""
    longtext: str = ""
    matchcode: str = ""
    alt_article_id: str = ""
    catalogue_page: str = ""
    raw_material_key: str = ""
    raw_material_weight: str = ""
    ean: str = ""
    type_of_cost: str = ""
    minimum_packaging_quantity: str = ""
    reference_number: str = ""
    dimensions_text: str = ""
    discount_indicator: str = ""

    def __init__(self, tag: str = ""):
        """A class that contains informations of a single DATANORM article.

        Args:
            tag (str, optional): Optional tag for the datanorm item
        """
        self.tag = tag

    @property
    def manufacturer_name(self) -> str | None:
        """Extracts Manufacturer name from the short_text_1 field.
        Therefor the manufacturer has to be written in upper case.
        """
        company_name = None
        match = re.match(self._MANUFACTURER_REGEX, self.short_text_1)
        if match is not None:
            company_name = match.group().rstrip()
        return company_name

    @property
    def item_name(self) -> str | None:
        """Extracts item name from the short_text_1 field"""
        item_name = self.short_text_1
        match = re.match(self._MANUFACTURER_REGEX, self.short_text_1)
        if match is not None:
            item_name = self.short_text_1[match.span()[1] :].lstrip()
        return item_name

    @property
    def description(self) -> str:
        """Generates a description, based on the "Textkennzeichen" in the \
            DATANORM file.
        """
        match self.text_indicator:
            case "00":
                description = f"{self.short_text_1}\n{self.short_text_2}"
            case "01":
                description = f"{self.short_text_1}"
            case "10":
                description = f"{self.longtext}\n{self.short_text_2}"
            case "20":
                description = f"{self.short_text_1}\n{self.dimensions_text}"
            case "30":
                description = f"{self.longtext}\n{self.dimensions_text}"
            case "40":
                description = f"{self.short_text_1}\n{self.short_text_2}\n{self.longtext}"  # noqa: E501
            case "41":
                description = f"{self.short_text_1}\n{self.longtext}"
            case "50":
                description = (
                    f"{self.short_text_1}\n{self.short_text_2}\n{self.dimensions_text}"
                )
            case "51":
                description = f"{self.short_text_1}\n{self.dimensions_text}"
            case "60":
                description = f"{self.short_text_1}\n{self.short_text_2}\n{self.longtext}\n{self.dimensions_text}"  # noqa: E501
            case "61":
                description = (
                    f"{self.short_text_1}\n{self.longtext}\n{self.dimensions_text}"
                )
            case _:
                description = f"{self.short_text_1}\n{self.short_text_2}"
        return description

    @property
    def price_unit(self) -> int | None:
        """Number of units for the given price"""
        if self.price_unit_raw == "0":
            units = 1
        elif self.price_unit_raw == "1":
            units = 10
        elif self.price_unit_raw == "2":
            units = 100
        elif self.price_unit_raw == "3":
            units = 1000
        else:
            units = None
        return units

    @price_unit.setter
    def price_unit(self, units: int):
        if units == 1:
            self.price_unit_raw = "0"
        elif units == 10:
            self.price_unit_raw = "1"
        elif units == 100:
            self.price_unit_raw = "2"
        elif units == 1000:
            self.price_unit_raw = "3"
        else:
            self.price_unit_raw = None
