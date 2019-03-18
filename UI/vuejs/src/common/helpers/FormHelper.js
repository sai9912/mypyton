export default class FormHelper {


    static measuresFields = {
        weightFormField: [
            'gross_weight',
            'gross_weight_uom',
            'net_weight',
            'net_weight_uom',
        ],
        dimensionFormField: [
            'depth',
            'depth_uom',
            'width',
            'width_uom',
            'height',
            'height_uom'
        ],
        netFormField: [
            'net_content',
            'net_content_uom'
        ]

    }

    static getViewMask(form) {
        return {
            measures: FormHelper.checkMeasures(form),
            picture: FormHelper.checkPicture(form)
        }
    }


    static checkMeasures(form) {
        const isWeight = FormHelper.checkArray(FormHelper.measuresFields.weightFormField, form);
        const isDimension = FormHelper.checkArray(FormHelper.measuresFields.dimensionFormField, form);
        const isNet = FormHelper.checkArray(FormHelper.measuresFields.netFormField, form);

        return {
            isWeight,
            isDimension,
            isNet,
            isAny: isWeight || isDimension || isNet
        }
    }

    static checkPicture(form) {
        return form.image_i18n.type !== 'hidden';
    }


    static checkArray(array, form) {
        return array.some((key) => {
            return form[key].type !== 'hidden'
        })
    }


    static fillFormUom(formData, uom) {

        if (uom.dimensions) {
            this.fillFieldsUom(formData, this.measuresFields.dimensionFormField, uom.dimensions)
        }
        if (uom.weights) {
            this.fillFieldsUom(formData, this.measuresFields.weightFormField, uom.weights)
        }
        if (uom.netContent) {
            this.fillFieldsUom(formData, this.measuresFields.netFormField, uom.netContent)
        }
    }


    static fillFieldsUom(formData, fields, uom) {
        fields.filter(name => name.includes('uom')).forEach((key) => {
            formData[key].enum = uom.map((item) => [item.code, item.uom])
            formData[key].enum.unshift(["", ""])
        })
    }
}