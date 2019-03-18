import json
from schematics.exceptions import ModelConversionError
from schematics.models import Model
from schematics.types import StringType, BooleanType, DateTimeType, DecimalType, NumberType
from member_organisations.models import ProductTemplate
from django.core import serializers
from .data import UOMS, TM, LANGUAGES, PACKAGE_TYPES, BARCODE_TYPES
from products.models.package_level import PACKAGE_LEVELS


def get_language(user):
    language = user.profile.language
    if not language:
        language = "en"
    return language


def language_mapping(template, user, reverse=False):
    language = get_language(user)
    translated_keys = {}
    for atri in template.attributes.all():
        field_name = atri.get_fieldname()
        label_dict = json.loads(atri.ui_label_i18n)
        translated = label_dict.get(language)
        if not translated:
            translated = label_dict.get("en")
        if not translated:
            translated = atri.ui_label
        if reverse:
            translated_keys[translated] = field_name
        else:
            translated_keys[field_name] = translated
    return translated_keys


def get_translated_values(value, user):
    language = get_language(user)
    try:
        val_dict = json.loads(value)
        translated = val_dict.get(language)
        if not translated:
            translated = val_dict.get("en")
        if not translated:
            translated = value
        return translated
    except Exception as e:
        return value


def export(products, user, template):
    errors = []
    content = []
    tm = template # ProductTemplate.objects.filter(name="gs1se-base").first()
    keys = set(x.get_fieldname() for x in tm.attributes.all())
    serialized_products = serializers.serialize(
        'json', products, fields=keys)
    products_data = json.loads(serialized_products)
    xls_keys = language_mapping(tm, user)
    for product in products_data:
        try:
            res = {xls_keys[key]: get_translated_values(
                value, user) for key, value in product.get("fields").items()}
        except Exception as e:
            errors.append({product["gtin"]: {'Exception': str(e)}})
            continue
        content.append(res)
    return content, errors


class MyBooleanType(BooleanType):
    def to_primitive(self, value, context=None):
        if value:
            return 'true'
        return 'false'


class ProductGDSN(Model):
    # Col_A = StringType(default='', serialize_when_none=False)
    Label_Description = StringType(
        max_length=200, required=False, default='None')
    Trade_Item_GTIN = StringType(
        regex="\d(539|501|509|0\d\d)\d{10}", required=True)
    Product_Description = StringType(max_length=200, required=True)
    Information_Provider_GLN = StringType(regex="\d{13}", required=True)
    Information_Provider_Name = StringType(
        max_length=100, required=False, default='GS1 Ireland')
    Company_Name = StringType(max_length=100, required=True)

    Target_Market = StringType(
        choices=[tm[0] for tm in TM], required=False, default='372')
    Trade_Item_Country_Of_Origin = StringType(
        choices=[tm[0] for tm in TM], required=False, default='372')
    Use_Language_Code_List = StringType(
        choices=[lng[0] for lng in LANGUAGES], default='en')  # 58

    Classification_Category_Code = StringType(required=True)
    Base_Unit_Indicator = MyBooleanType(required=True)
    Consumer_Unit_Indicator = MyBooleanType(required=True)
    Variable_Weight_Trade_Item = MyBooleanType(required=True)
    Ordering_Unit_Indicator = MyBooleanType(required=True)
    Dispatch_Unit_Indicator = MyBooleanType(required=True)
    Invoice_Unit_Indicator = MyBooleanType(required=True)
    Trade_Item_Unit_Descriptor = StringType(
        choices=[d[1] for d in PACKAGE_LEVELS], required=True)
    Functional_Name = StringType(max_length=75, required=True)
    Brand_Name = StringType(max_length=75, required=True)
    Height = DecimalType(required=False)
    Width = DecimalType(required=False)
    Depth = DecimalType(required=False)
    Height_UOM = StringType(choices=[uom[0] for uom in UOMS], required=False)
    Width_UOM = StringType(choices=[uom[0] for uom in UOMS], required=False)
    Depth_UOM = StringType(choices=[uom[0] for uom in UOMS], required=False)
    Gross_Weight = DecimalType(required=False)
    Gross_Weight_UOM = StringType(
        choices=[uom[0] for uom in UOMS], required=False)
    Net_Content = StringType(max_length=10, required=False)
    Net_Content_UOM = StringType(
        choices=[uom[0] for uom in UOMS], required=False)
    Packaging_Type_Code = StringType(
        choices=[pt[0] for pt in PACKAGE_TYPES], required=False)

    Trade_Item_Last_Change_Date = DateTimeType(
        required=False, serialized_format="%Y-%m-%dT%H:%M:%S%zZ")
    Discontinued_Date = DateTimeType(
        required=False, serialized_format="%Y-%m-%dT%H:%M:%S%zZ")
    Col_AM = StringType(default='', serialize_when_none=False)

    Sub_Brand = StringType(max_length=75, required=False)
    Variant_Description = StringType(max_length=75, required=False)
    Net_Weight = DecimalType(required=False)
    Net_Weight_UOM = StringType(
        choices=[uom[0] for uom in UOMS], required=False)
    Manufacturer_GLN = StringType(required=False)
    Manufacturer_Name = StringType(max_length=100, required=False)
    Additional_Trade_Item_Identification_Type = StringType(
        max_length=50, required=False)
    Additional_Trade_Item_Identification_Value = StringType(
        max_length=50, required=False)
    Type_Of_Information = StringType(max_length=100, required=False)
    Uniform_Resource_Identifier = StringType(max_length=100, required=False)
    Packaging_Marked_Returnable = MyBooleanType()
    Is_Price_On_Pack = MyBooleanType()
    GTIN_Of_Next_Lower_Item = StringType(required=False)
    Amount_Of_Next_Lower_Level_Items = StringType(required=False)
    Quantity_Of_Children = NumberType(
        int, 'Integer', min_value=1, required=False)
    Total_Quantity_Of_Next_Lower_Level_Trade_Item = StringType(required=False)
    Start_Availability_Date_Time = DateTimeType(
        required=False, serialized_format="%Y-%m-%dT%H:%M:%S%zZ")
    End_Availability_Date_Time = DateTimeType(
        required=False, serialized_format="%Y-%m-%dT%H:%M:%S%zZ")

    Trade_Item_Status = StringType(
        max_length=25, required=False, default='ADD')

    Brand_Owner_GLN = StringType(required=False)
    Brand_Owner_Name = StringType(max_length=100, required=False)
    Col_AN = StringType(default='', serialize_when_none=False)
    Col_AO = StringType(default='', serialize_when_none=False)
    Col_AP = StringType(default='', serialize_when_none=False)
    Publication_Date = DateTimeType(
        required=False, serialized_format="%Y-%m-%dT%H:%M:%S%zZ")  # pub_date
    Effective_Date = DateTimeType(
        required=False, serialized_format="%Y-%m-%dT%H:%M:%S%zZ")  # eff_date
    Col_AZ = StringType(default='', serialize_when_none=False)
    Col_BA = StringType(default='', serialize_when_none=False)
    Col_BB = StringType(default='', serialize_when_none=False)
    Col_BC = StringType(default='', serialize_when_none=False)
    Col_BD = StringType(default='', serialize_when_none=False)
    Col_BE = StringType(default='', serialize_when_none=False)
    Col_BF = StringType(default='', serialize_when_none=False)
    Col_BG = StringType(default='', serialize_when_none=False)
    Col_BH = StringType(default='', serialize_when_none=False)
    Col_BI = StringType(default='', serialize_when_none=False)
    Col_BJ = StringType(default='', serialize_when_none=False)
    Col_BK = StringType(default='', serialize_when_none=False)
    Col_BL = StringType(default='', serialize_when_none=False)
    Barcode_Type = StringType(choices=[bt[0]
                                       for bt in BARCODE_TYPES], required=False)
    Col_BO = StringType(default='', serialize_when_none=False)
    Col_BP = StringType(default='', serialize_when_none=False)
    Col_BQ = StringType(default='', serialize_when_none=False)
    Col_BV = StringType(default='', serialize_when_none=False)
    Col_BW = StringType(default='', serialize_when_none=False)
    Col_BX = StringType(default='', serialize_when_none=False)
    Col_BY = StringType(default='', serialize_when_none=False)
    Col_BZ = StringType(default='', serialize_when_none=False)
    Col_CA = StringType(default='', serialize_when_none=False)
    Col_CB = StringType(default='', serialize_when_none=False)
    Col_CC = StringType(default='', serialize_when_none=False)
    Col_CD = StringType(default='', serialize_when_none=False)
    Col_CE = StringType(default='', serialize_when_none=False)

    Col_CG = StringType(default='', serialize_when_none=False)
    Col_CH = StringType(default='', serialize_when_none=False)
    Col_CI = StringType(default='', serialize_when_none=False)
    Col_CJ = StringType(default='', serialize_when_none=False)
    Col_CK = StringType(default='', serialize_when_none=False)
    Col_CL = StringType(default='', serialize_when_none=False)
    Col_CM = StringType(default='', serialize_when_none=False)
    Col_CN = StringType(default='', serialize_when_none=False)
    Col_CO = StringType(default='', serialize_when_none=False)
    Col_CP = StringType(default='', serialize_when_none=False)
    Col_CQ = StringType(default='', serialize_when_none=False)
    Col_CR = StringType(default='', serialize_when_none=False)

    Col_CS = StringType(default='', serialize_when_none=False)
    Col_CT = StringType(default='', serialize_when_none=False)
    Col_CU = StringType(default='', serialize_when_none=False)
    Col_CV = StringType(default='', serialize_when_none=False)
    Col_CW = StringType(default='', serialize_when_none=False)
    Col_CX = StringType(default='', serialize_when_none=False)
    Col_CY = StringType(default='', serialize_when_none=False)
    Col_CZ = StringType(default='', serialize_when_none=False)
    Col_DA = StringType(default='', serialize_when_none=False)
    Col_DB = StringType(default='', serialize_when_none=False)
    Col_DC = StringType(default='', serialize_when_none=False)
    Col_DE = StringType(default='', serialize_when_none=False)

    GS1CloudStatus = StringType(choices=['ACTIVE', 'INACTIVE'], required=False)

    '''
    # def validate_Additional_Trade_Item_Identification_Value(self, data, value):
    #    if not value:
    #        raise ValidationError("This field is required")

    def validate_Label_Description(self, data, value):
        if data['Trade_Item_Unit_Descriptor'] == 'BASE_UNIT_OR_EACH':
            if not value:
                raise ValidationError("This field is required for base units")

    def validate_Classification_Category_Code(self, data, value):
        cs = CategoriesService()
        if self.Classification_Category_Code.required and not value:
            raise ValidationError("Classification Category Code is required")
        if value and not cs.first(code=value):
            raise ValidationError(
                "Classification Category Code is not valid, please consult https://www.gs1.org/gpc/browser")

    def validate_Manufacturer_GLN(self, data, value):
        if value and not re.match("\d{13}", value):
            raise ValidationError("Manufacturer GLN is not valid")
        if value and not data['Manufacturer_Name']:
            raise ValidationError("If Manufacturer GLN is present, Manufacturer Name should be present")

    def validate_Manufacturer_Name(self, data, value):
        if value and not data['Manufacturer_GLN']:
            raise ValidationError("If Manufacturer Name is present, Manufacturer GLN should be present")

    # def validate_Brand_Owner_GLN(self, data, value):
    #    if value and not re.match("\d{13}", value):
    #        raise ValidationError("Brand Owner GLN is not valid")

    def validate_Trade_Item_GTIN(self, data, value):
        if not isValid(value):
            raise ValidationError("GTIN not valid")

    def validate_Net_Content(self, data, value):
        if value:
            if not data.get('Net_Content_UOM'):
                raise ValidationError("Net Content is given without Net Content UOM")

    def validate_Net_Content_UOM(self, data, value):
        if value:
            if not data.get('Net_Content'):
                raise ValidationError("Net Content UOM is given without Net Content value")

    def validate_Net_Weight(self, data, value):
        if value:
            if not data.get('Net_Weight_UOM'):
                raise ValidationError("Net Weight is given without Net Weight UOM")

    def validate_Net_Weight_UOM(self, data, value):
        if value:
            if not data.get('Net_Weight'):
                raise ValidationError("Net Weight UOM is given without Net Weight value")

    def validate_Height_UOM(self, data, value):
        if data['Height'] and not value:
            raise ValidationError("Height UOM is required when Height is given")

    def validate_Width_UOM(self, data, value):
        if data['Width'] and not value:
            raise ValidationError("Width UOM is required when Width is given")

    def validate_Depth_UOM(self, data, value):
        if data['Depth'] and not value:
            raise ValidationError("Depth UOM is required when Depth is given")

    def validate_Gross_Weight_UOM(self, data, value):
        if data['Gross_Weight'] and not value:
            raise ValidationError("Gross_Weight UOM is required when Gross_Weight is given")

    def validate_Quantity_Of_Children(self, data, value):
        if data['Trade_Item_Unit_Descriptor'] != BASE_PACKAGE_LEVEL:
            if not value:
                raise ValidationError(
                    "Quantity Of Children is required when Trade Item Unit Descriptor is not BASE UNIT OR EACH")

    def validate_Quantity_Of_Next_Lower_Level_Item(self, data, value):
        if data['GTIN_Of_Next_Lower_Item']:
            if not value:
                raise ValidationError(
                    "Quantity Of Next Lower Level Item is required when GTIN Of Next Lower Item is given")
            if len(data['Quantity_Of_Next_Lower_Level_Item'].split(',')) != int(data['Quantity_Of_Children']):
                raise ValidationError("Length of Quantity Of Next Lower Level Item must equal the Quantity Of Children")

    def validate_GTIN_Of_Next_Lower_Item(self, data, value):
        if data['Trade_Item_Unit_Descriptor'] != BASE_PACKAGE_LEVEL:
            if not value:
                raise ValidationError(
                    "GTIN Of Next Lower Item is required when Trade Item Unit Descriptor is not BASE UNIT OR EACH")
            try:
                int(data['Quantity_Of_Children'])
            except Exception as e:
                raise ValidationError("Quantity_Of_Children must be given")
            if len(data['GTIN_Of_Next_Lower_Item'].split(',')) != int(data['Quantity_Of_Children']):
                raise ValidationError("Length of GTIN_Of_Next_Lower_Item must equal the Quantity Of Children")

    # def validate_fileFormatCode(self, data, value):
    #    pass

    # def validate_Uniform_Resource_Identifier(self, data, value):
    #    if value:
    #        if not value.startswith('http://') or not value.statswith('https://'):
    #            raise ValidationError('Uniform_Resource_Identifier should start with http: or https:')
    '''

    @classmethod
    def get_fieldnames(cls):
        return [
            # 'Col_A',
            'Label_Description',
            'Trade_Item_GTIN',
            'Information_Provider_GLN',
            'Information_Provider_Name',
            'Target_Market',
            'Base_Unit_Indicator',
            'Consumer_Unit_Indicator',
            'Variable_Weight_Trade_Item',
            'Ordering_Unit_Indicator',
            'Dispatch_Unit_Indicator',
            'Invoice_Unit_Indicator',
            'Start_Availability_Date_Time',
            'Classification_Category_Code',
            'Trade_Item_Unit_Descriptor',
            'Functional_Name',
            'Brand_Name',
            'Packaging_Marked_Returnable',
            'Height',
            'Height_UOM',
            'Width',
            'Width_UOM',
            'Depth',
            'Depth_UOM',
            'Gross_Weight',
            'Gross_Weight_UOM',
            'End_Availability_Date_Time',
            'Sub_Brand',
            'Brand_Owner_GLN',
            'Brand_Owner_Name',
            'Product_Description',
            'Variant_Description',
            'Net_Content',
            'Net_Content_UOM',
            'Net_Weight',
            'Net_Weight_UOM',
            'Packaging_Type_Code',
            'Trade_Item_Last_Change_Date',
            'Discontinued_Date',
            'Col_AM',  # Display_Unit_Indicator
            'Col_AN',  # Platform_Type_Code
            'Col_AO',  # Packaging_Weight
            'Col_AP',  # Packaging_Weight_UoM
            'Publication_Date',
            'Effective_Date',
            'GTIN_Of_Next_Lower_Item',
            'Amount_Of_Next_Lower_Level_Items',
            'Quantity_Of_Children',
            'Total_Quantity_Of_Next_Lower_Level_Trade_Item',
            'Trade_Item_Country_Of_Origin',
            'Manufacturer_GLN',
            'Manufacturer_Name',
            'Col_AZ',
            'Col_BA',
            'Col_BB',
            'Col_BC',
            'Col_BD',
            'Col_BE',
            'Col_BF',
            'Col_BG',
            'Col_BH',
            'Col_BI',
            'Col_BJ',
            'Col_BK',
            'Col_BL',
            'Is_Price_On_Pack',
            'Barcode_Type',
            'Col_BO',
            'Col_BP',
            'Col_BQ',
            'Additional_Trade_Item_Identification_Type',
            'Additional_Trade_Item_Identification_Value',
            'Type_Of_Information',
            'Uniform_Resource_Identifier',
            'Col_BV',
            'Col_BW',
            'Col_BX',
            'Col_BY',
            'Col_BZ',
            'Col_CA',
            'Col_CB',
            'Col_CC',
            'Col_CD',
            'Col_CE',
            'Trade_Item_Status',

            'Col_CG',
            'Col_CH',
            'Col_CI',
            'Col_CJ',
            'Col_CK',
            'Col_CL',
            'Col_CM',
            'Col_CN',
            'Col_CO',
            'Col_CP',
            'Col_CQ',
            'Col_CR',
            'Col_CS',
            'Col_CT',
            'Col_CU',
            'Col_CV',
            'Col_CW',
            'Col_CX',
            'Col_CY',
            'Col_CZ',
            'Col_DA',
            'Col_DB',
            'Col_DC',
            'Use_Language_Code_List',
            'Col_DE',

            'GS1CloudStatus',
            'Company_Name'
        ]

    @classmethod
    def export(cls, products, user):
        errors = []
        content = []
        tm = ProductTemplate.objects.filter(name="gs1se-base").first()
        keys = set(x.path.split(".")[-1] for x in tm.attributes.all())
        serialized_products = serializers.serialize(
            'json', products, fields=keys)
        products_data = json.loads(serialized_products)
        xls_keys = language_mapping(tm, user)
        for product in products_data:
            try:
                res = {xls_keys[key]: get_translated_values(
                    value, user) for key, value in product.get("fields").items()}
            except ModelConversionError as e:
                errors.append(
                    {product.gtin: dict([(k, v[0]) for k, v in e.messages.items()])})
                continue
            except Exception as e:
                errors.append({product.gtin: {'Exception': str(e)}})
                continue
            content.append(res)
        return content, errors


'''
class ProductGEPIR(Model):
    Trade_Item_GTIN = StringType(regex="\d(539|501|509|0\d\d)\d{10}", required=True)
    Item_Data_Language = StringType(default="en", required=True)
    Information_Provider_GLN = StringType(regex="\d{13}", required=True)
    Information_Provider_Name = StringType(max_length=100, required=True)
    Product_Description = StringType(max_length=200, required=True)
    Trade_Item_Unit_Descriptor = StringType(choices=[pl[1] for pl in PACKAGE_LEVELS], required=False)
    Brand_Name = StringType(max_length=75, required=False, default='')
    Net_Content = StringType(max_length=10, required=False, default='')
    Net_Content_UOM = StringType(choices=[uom[0] for uom in UOMS], required=False)
    Trade_Item_Last_Change_Date = DateTimeType(required=False, serialized_format="%Y-%m-%dT%H:%M:%S%zZ")
    IPparty_Role = StringType(default="INFORMATION_PROVIDER", required=False)
    IPadditionalPartyIdentification = StringType(max_length=100, required=False, default='')
    Manufacturer_GLN = StringType(regex="\d{13}", required=False)
    Manufacturer_Name = StringType(max_length=100, required=False, default='')
    # ManufacturerpartyRole = StringType(choices=[r[0] for r in ROLES], required=False)
    ManufacturerpartyRole = StringType(max_length=100, required=False, default='')
    ManufactureradditionalPartyIdentification = StringType(max_length=100, required=False, default='')
    Classification_Category_Code = StringType(regex="\d{8,8}", required=True)
    gpcCategoryDefinition = StringType(max_length=200, required=False, default='')
    gpcCategoryName = StringType(max_length=75, required=False, default='')
    additionalTradeItemClassificationSystemCode = StringType(max_length=75, required=False, default='')
    descriptiveSize = StringType(max_length=75, required=False, default='')
    sizeCode = StringType(max_length=25, required=False, default='')
    fileFormatCode = StringType(choices=['HTML', 'TXT', 'XML'], required=False)
    Uniform_Resource_Identifier = StringType(max_length=200, required=False, default='')
    Quantity_Of_Children = StringType(max_length=10, required=False, default='')
    Total_Quantity_Of_Next_Lower_Level_Trade_Item = StringType(max_length=10, required=False, default='')

    @classmethod
    def export(cls, products):
        errors = []
        fieldnames = cls.get_fieldnames()
        content = []
        for product in products:
            try:
                p = cls(product.to_gepir())
            except ModelConversionError as e:
                errors.append({product.gtin: dict([(k, v[0]) for k, v in e.messages.items()])})
                continue
            try:
                p.validate()
            except ModelValidationError as e:
                errors.append({product.gtin: dict([(k, v[0]) for k, v in e.messages.items()])})
                continue
            content.append(['', 'No'] + sort_dict(p.to_primitive(), fieldnames).values())
        return content, errors

    @classmethod
    def get_fieldnames(cls):
        return [
            'Trade_Item_GTIN',
            'Trade_Item_Unit_Descriptor',
            'Product_Description',
            'Brand_Name',
            'Net_Content',
            'Net_Content_UOM',
            'Item_Data_Language',
            'Trade_Item_Last_Change_Date',
            'Information_Provider_GLN',
            'Information_Provider_Name',
            'IPparty_Role',
            'IPadditionalPartyIdentification',
            'Manufacturer_GLN',
            'Manufacturer_Name',
            'ManufacturerpartyRole',
            'ManufactureradditionalPartyIdentification',
            'Classification_Category_Code',
            'gpcCategoryDefinition',
            'gpcCategoryName',
            'additionalTradeItemClassificationSystemCode',
            'descriptiveSize',
            'sizeCode',
            'fileFormatCode',
            'Uniform_Resource_Identifier',
            'Quantity_Of_Children',
            'Total_Quantity_Of_Next_Lower_Level_Trade_Item'
        ]

    def validate_Manufacturer_GLN(self, data, value):
        if value and not re.match("\d{13}", value):
            raise ValidationError("Manufacturer GLN is not valid")
        if value and not data['Manufacturer_Name']:
            raise ValidationError("If Manufacturer GLN is present, Manufacturer Name should be present")

    def validate_Manufacturer_Name(self, data, value):
        if value and not data['Manufacturer_GLN']:
            raise ValidationError("If Manufacturer Name is present, Manufacturer GLN should be present")
'''
