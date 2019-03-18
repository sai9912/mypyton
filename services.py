from service import Service
from prefixes.models import Prefix
from users.models import UsersService
from audit.models import Log
from products.models.product import Product
from products.models.package_level import PackageLevelService
from products.models.country_of_origin import CountryOfOrigin
from products.models.target_market import TargetMarket
from products.models.language import Language
from products.models.net_content_uom import NetContentUOM
from products.models.weight_uom import WeightUOM
from products.models.dimension_uom import DimensionUOM
from products.models.package_type import PackageType
from products.models.sub_product import SubProduct
from products.models.gtin_target_market import GtinTargetMarket

prefix_service = Prefix.service
product_service = Product.service
country_of_origin_service = CountryOfOrigin.service
target_market_service = TargetMarket.service
language_service = Language.service
net_content_uom_service = NetContentUOM.service
weight_uom_service = WeightUOM.service
dimension_uom_service = DimensionUOM.service
package_type_service = PackageType.service
users_service = UsersService()
logs_service = Service(Log)
package_level_service = PackageLevelService()
sub_product_service = SubProduct.service
gtin_target_market_service = GtinTargetMarket.service
